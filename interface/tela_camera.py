from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox,
)
from PySide6.QtMultimedia import QSoundEffect
import cv2
import time


# Tempo mínimo (em segundos) entre leituras do MESMO QR Code
SEGUNDOS_ENTRE_LEITURAS = 5


class ThreadCamera(QThread):
    frame_pronto = Signal(QImage)
    qr_detectado = Signal(str)

    def __init__(self, leitor_camera, parent=None):
        super().__init__(parent)
        self.leitor = leitor_camera
        self._rodando = True
        # Trava temporal: guarda o último código e quando foi lido
        self._ultimo_codigo = None
        self._tempo_ultimo_codigo = 0.0

    def run(self):
        self.leitor.iniciar()

        while self._rodando:
            frame, texto_qr = self.leitor.ler_frame_e_qr()

            if frame is None:
                self.msleep(50)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            altura, largura, canais = frame_rgb.shape
            bytes_por_linha = canais * largura

            imagem = QImage(
                frame_rgb.data,
                largura,
                altura,
                bytes_por_linha,
                QImage.Format_RGB888,
            )

            self.frame_pronto.emit(imagem.copy())

            if texto_qr:
                agora = time.time()
                mesmo_codigo = (texto_qr == self._ultimo_codigo)
                tempo_decorrido = agora - self._tempo_ultimo_codigo

                # Só emite se for um código diferente OU se já passou tempo suficiente
                if not mesmo_codigo or tempo_decorrido >= SEGUNDOS_ENTRE_LEITURAS:
                    self._ultimo_codigo = texto_qr
                    self._tempo_ultimo_codigo = agora
                    self.qr_detectado.emit(texto_qr)

            self.msleep(30)

    def parar(self):
        self._rodando = False
        self.wait(3000)  # espera até 3 segundos
        if self.isRunning():
            self.terminate()
            self.wait(1000)
        self.leitor.liberar()


class TelaCamera(QMainWindow):
    def __init__(self, leitor_camera, gerenciador, gerador):
        super().__init__()
        self.leitor = leitor_camera
        self.gerenciador = gerenciador
        self.gerador = gerador

        self.setWindowTitle("Controle de Refeitório")
        self.setMinimumSize(800, 700)

        # Som de confirmação
        self.som = QSoundEffect()
        self.som.setSource(QUrl.fromLocalFile("bip.wav"))
        self.som.setVolume(0.8)

        # Widgets
        self.label_camera = QLabel("Aguardando câmera...")
        self.label_camera.setAlignment(Qt.AlignCenter)
        self.label_camera.setMinimumSize(640, 480)
        self.label_camera.setStyleSheet("background-color: #222; color: #888;")

        self.label_status = QLabel("Aguardando leitura...")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1565C0; padding: 10px;"
        )

        self.botao_relatorio = QPushButton("Gerar Relatório do Dia")
        self.botao_relatorio.setStyleSheet("font-size: 14px; padding: 10px;")
        self.botao_relatorio.clicked.connect(self.gerar_relatorio)

        self.botao_alternar = QPushButton("Alternar Câmera")
        self.botao_alternar.setStyleSheet("font-size: 14px; padding: 10px;")
        self.botao_alternar.clicked.connect(self.alternar_camera)

        # Layout
        botoes = QHBoxLayout()
        botoes.addWidget(self.botao_relatorio)
        botoes.addWidget(self.botao_alternar)

        layout = QVBoxLayout()
        layout.addWidget(self.label_camera, stretch=1)
        layout.addWidget(self.label_status)
        layout.addLayout(botoes)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Thread da câmera
        self.thread_camera = None
        self._iniciar_thread_camera()

    def _iniciar_thread_camera(self):
        self.thread_camera = ThreadCamera(self.leitor, self)
        self.thread_camera.frame_pronto.connect(self.atualizar_frame)
        self.thread_camera.qr_detectado.connect(self.processar_qr)
        self.thread_camera.start()

    def atualizar_frame(self, imagem: QImage):
        pixmap = QPixmap.fromImage(imagem)
        self.label_camera.setPixmap(
            pixmap.scaled(
                self.label_camera.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def processar_qr(self, texto_qr):
        sucesso, mensagem = self.gerenciador.processar_leitura_qr(texto_qr)

        if sucesso:
            self.label_status.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #2E7D32; padding: 10px;"
            )
            self.som.play()
        else:
            self.label_status.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #C62828; padding: 10px;"
            )

        self.label_status.setText(mensagem)

    def gerar_relatorio(self):
        sucesso, mensagem = self.gerador.exportar_txt_do_dia()

        if sucesso:
            QMessageBox.information(self, "Relatório", mensagem)
        else:
            QMessageBox.warning(self, "Relatório", mensagem)

    def alternar_camera(self):
        # Evita cliques repetidos enquanto a troca acontece
        self.botao_alternar.setEnabled(False)
        self.botao_alternar.setText("Trocando câmera...")

        try:
            # 1. Para a thread atual e aguarda ela realmente terminar
            if self.thread_camera is not None:
                self.thread_camera.parar()
                self.thread_camera = None

            # 2. Tenta alternar. Se não houver outra câmera, mantém a atual.
            trocou = self.leitor.alternar_camera()

            if not trocou:
                self.label_status.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #E65100; padding: 10px;"
                )
                self.label_status.setText(
                    "Nenhuma câmera alternativa encontrada. Mantendo a atual."
                )

            # 3. Reinicia a thread (com a câmera atual ou a nova)
            self._iniciar_thread_camera()

        except Exception as e:
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao alternar câmera:\n{e}\n\nReiniciando com a câmera atual."
            )
            try:
                self.leitor.liberar()
                self.leitor.camera_id = 0
                self._iniciar_thread_camera()
            except Exception:
                pass

        finally:
            self.botao_alternar.setEnabled(True)
            self.botao_alternar.setText("Alternar Câmera")

    def closeEvent(self, event):
        if self.thread_camera is not None:
            self.thread_camera.parar()
        event.accept()