import os
import sys
from datetime import date
import traceback


def obter_pasta_dados():
    """Retorna uma pasta permanente para guardar os dados do app.

    - Em desenvolvimento (python main.py): usa a pasta do projeto.
    - Como .exe (PyInstaller): usa %APPDATA%\\LeitorQRCode no Windows,
      ou ~/.local/share/LeitorQRCode no Linux.
    """
    if getattr(sys, 'frozen', False):
        if sys.platform.startswith('win'):
            base = os.getenv('APPDATA') or os.path.expanduser('~')
        else:
            base = os.path.join(os.path.expanduser('~'), '.local', 'share')
        pasta = os.path.join(base, "LeitorQRCode")
    else:
        pasta = os.path.abspath(".")

    os.makedirs(pasta, exist_ok=True)
    return pasta


class GeradorRelatorio:
    def __init__(self, banco_de_dados):
        self.db = banco_de_dados
        self.pasta_saida = os.path.join(obter_pasta_dados(), "relatorios_gerados")
        os.makedirs(self.pasta_saida, exist_ok=True)

    def exportar_txt_do_dia(self, data_relatorio=None):
        if data_relatorio is None:
            data_relatorio = date.today().isoformat()

        resultados = self.db.buscar_refeicoes_do_dia(data_relatorio)

        if not resultados:
            return False, f"Nenhum registro de refeição encontrado para hoje ({data_relatorio})."

        try:
            nome_arquivo = f"Relatorio_Refeicoes_{data_relatorio}.txt"
            caminho_completo = os.path.join(self.pasta_saida, nome_arquivo)

            with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(f"=== RELATORIO DE REFEICOES: {data_relatorio} ===\n\n")

                setor_atual = None

                for linha in resultados:
                    nome = linha[0]
                    setor = linha[1]

                    if setor != setor_atual:
                        arquivo.write(f"\n[{setor.upper()}]\n")
                        setor_atual = setor

                    arquivo.write(f" - {nome}\n")

                arquivo.write("\n" + "=" * 45 + "\n")
                arquivo.write(f"TOTAL DE REFEICOES SERVIDAS: {len(resultados)}\n")

            # Abre o relatório automaticamente para o usuário
            self._abrir_arquivo(caminho_completo)

            return True, (
                f"Relatório do dia {data_relatorio} gerado com sucesso!\n\n"
                f"Total de refeições: {len(resultados)}\n\n"
                f"O arquivo foi aberto automaticamente."
            )

        except Exception as e:
            print("\n--- ERRO AO GERAR TXT ---")
            traceback.print_exc()
            return False, f"Erro ao gerar o relatório: {str(e)}"

    def _abrir_arquivo(self, caminho):
        """Abre o arquivo no programa padrão do sistema."""
        try:
            if sys.platform.startswith('win'):
                os.startfile(caminho)
            elif sys.platform.startswith('darwin'):
                import subprocess
                subprocess.Popen(['open', caminho])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', caminho])
        except Exception as e:
            # Se não conseguir abrir, não é erro fatal — só ignora
            print(f"Não foi possível abrir o arquivo automaticamente: {e}")