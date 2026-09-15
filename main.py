import sys
from PySide6.QtWidgets import QApplication

from camera.leitorCamera import LeitorCamera
from conexao.conexaoBanco import BancoDeDados
from regras.gerenciadorRefeitorio import GerenciadorRefeitorio
from relatorios.geradorRelatorio import GeradorRelatorio
from interface.tela_camera import TelaCamera


def main():
    app = QApplication(sys.argv)

    banco = BancoDeDados()
    gerenciador = GerenciadorRefeitorio(banco)
    gerador = GeradorRelatorio(banco)
    leitor = LeitorCamera(camera_id=0)

    janela = TelaCamera(leitor, gerenciador, gerador)
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()