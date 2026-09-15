from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PySide6.QtMultimedia import  QSoundEffect
from rich import layout

import cv2


class ThreadCamera(QThread):
    frame_pronto = Signal(QImage)
    qr_detectado = Signal(str)

    def __init__(self, leitor_camera, parent=None):
        super().__init__(parent)
        self.leitor = leitor_camera
        self._rodando = True

    def run(self):
        self.leitor.iniciar()

        while self._rodando:
            frame, texto_qr = self.leitor.ler_frame_e_qr()

            if frame is not None:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            altura, largura, canais = frame_rgb.shape
            bytes_por_linha = canais * largura

            imagem = QImage(
                frame_rgb.data,
                largura,
                altura,
                QImage.Format_RGB888,
            )

            self.frame_pronto.emit(imagem.copy())

            if texto_qr:
                self.qr_detectado.emit(texto_qr)

            self.msleep(30)
    def parar(self):
        self._rodando = False
        self.wait()
        self.leitor.liberar()


class TelaCamera(QMainWindow):
    def __init__(self, leitor_camera, gerenciador, gerador):
        super().__init__()
        self.leitor = leitor_camera
        self.gerenciador = gerenciador
        self.gerador = gerador

        self.setWindowTitle("Controle de Refeitório")
        self.setMinimumSize(800, 700)

        self.som = QSoundEffect()
        self.som.setSource(QUrl.fromLocalFile("bip.wav"))
        self.som.setVolume(0.8)

        self.label_camera = QLabel("Aguardando câmera...")
        self.label_camera.setAlignment(Qt.AlignCenter)
        self.label_camera.setMinimumSize(640, 480)
        self.label_camera.setStyleSheet("background-color: #222; color: #888;")

        self.label_status = QLabel("Aguardando leitura...")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1565C0; padding: 10px;"
        )

        self.botao_relatorio = QPushButton("Gerar Relatorio do dia")
        self.botao_relatorio.setStyleSheet("font-size: 14px; padding: 10px;")
        self.botao_relatorio.clicked.connect(self.gerar_relatorio)

        botoes = QVBoxLayout()
        botoes.addWidget(self.botao_relatorio)

        layout = QVBoxLayout()
        layout.addWidget(self.label_camera, stretch=1)
        layout.addWidget(self.label_status)
        layout.addLayout(botoes)

        self.thread_camera = ThreadCamera(self.leitor_camera, self)
        self.thread_camera.frame_pronto.connect(self.atualizar_frame)
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
        self.thread_camera.parar()
        self.leitor.alternar_camera()
        self.thread_camera = ThreadCamera(self.leitor, self)
        self.thread_camera.frame_pronto.connect(self.atualizar_frame)
        self.thread_camera.qr_detectado.connect(self.processar_qr)
        self.thread_camera.start()

    def closeEvent(self, event):
        self.thread_camera.parar()
        event.accept()

