import cv2
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

# Importando as nossas classes
from conexao.conexaoBanco import BancoDeDados
from regras.gerenciadorRefeitorio import GerenciadorRefeitorio
from camera.leitorCamera import LeitorCamera
from relatorios.geradorRelatorio import GeradorRelatorio


class AppRefeitorio(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"

        self.banco = BancoDeDados()
        self.gerenciador = GerenciadorRefeitorio(self.banco)
        self.leitor = LeitorCamera(camera_id=0)
        self.gerador_relatorio = GeradorRelatorio(self.banco)

        self.leitor.iniciar()
        self.pausa_leitura = False

        tela = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        titulo = MDLabel(
            text="Leitor do Refeitório",
            halign="center",
            font_style="Headline",
            role="small",
            size_hint_y=0.1
        )

        self.camera_feed = Image(size_hint_y=0.6)

        self.lbl_status = MDLabel(
            text="Aguardando QR Code...",
            halign="center",
            font_style="Title",
            role="medium",
            theme_text_color="Custom",
            text_color=(0, 0.5, 0, 1),
            size_hint_y=0.1
        )

        # ... (código existente da lbl_status) ...

        # --- NOVO BOTÃO DE TROCAR CÂMERA ---
        btn_trocar_camera = MDButton(
            MDButtonText(
                text="Trocar Câmera",
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            ),
            style="tonal",  # Usamos 'tonal' para ele ficar um pouco diferente do botão verde principal
            theme_width="Custom",
            size_hint_x=0.8,
            pos_hint={"center_x": 0.5}
        )
        btn_trocar_camera.bind(on_release=self.acao_trocar_camera)

        # O botão de gerar relatório (já existia)
        btn_relatorio = MDButton(
            MDButtonText(
                text="Gerar Relatório do Dia",
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            ),
            style="filled",
            theme_width="Custom",
            size_hint_x=0.8,
            pos_hint={"center_x": 0.5}
        )
        btn_relatorio.bind(on_release=self.acao_gerar_relatorio)

        # Adicionando tudo no layout na ordem correta:
        layout.add_widget(titulo)
        layout.add_widget(self.camera_feed)
        layout.add_widget(btn_trocar_camera)  # <--- Botão novo aqui
        layout.add_widget(self.lbl_status)
        layout.add_widget(btn_relatorio)
        tela.add_widget(layout)

        Clock.schedule_interval(self.atualizar_camera, 1.0 / 30.0)

        return tela

    def atualizar_camera(self, dt):
        frame, texto_qr = self.leitor.ler_frame_e_qr()

        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_flip = cv2.flip(frame_rgb, 0)
            buf = frame_flip.tobytes()

            textura = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            textura.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.camera_feed.texture = textura

        if texto_qr and not self.pausa_leitura:
            self.processar_qr(texto_qr)

    def processar_qr(self, texto_qr):
        self.pausa_leitura = True

        print(f"\n[CÂMERA] QR Code detectado: {texto_qr}")
        sucesso, mensagem = self.gerenciador.processar_leitura_qr(texto_qr)
        print(f"[SISTEMA] {mensagem}\n")

        self.mostrar_aviso(mensagem)
        Clock.schedule_once(self.liberar_leitura, 2)

    def liberar_leitura(self, dt):
        self.pausa_leitura = False

    def acao_gerar_relatorio(self, instancia):
        sucesso, mensagem = self.gerador_relatorio.exportar_txt_do_dia()
        self.mostrar_aviso(mensagem)

    def acao_trocar_camera(self, instancia):
        self.leitor.alternar_camera()
        self.mostrar_aviso(f"Câmera alternada (ID: {self.leitor.camera_id})")

    def mostrar_aviso(self, mensagem):
        self.lbl_status.text = mensagem
        Clock.schedule_once(self.limpar_aviso, 3)

    def limpar_aviso(self, dt):
        self.lbl_status.text = "Aguardando QR Code..."

    def on_stop(self):
        self.leitor.liberar()


if __name__ == '__main__':
    Window.size = (360, 640)
    AppRefeitorio().run()