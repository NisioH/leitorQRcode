from datetime import date
import os
import traceback


class GeradorRelatorio:
    def __init__(self, banco_de_dados):
        self.db = banco_de_dados
        self.pasta_saida = "relatorios_gerados"
        os.makedirs(self.pasta_saida, exist_ok=True)

    def exportar_txt_do_dia(self, data_relatorio=None):
        if data_relatorio is None:
            data_relatorio = date.today().isoformat()

        resultados = self.db.buscar_refeicoes_do_dia(data_relatorio)

        if not resultados:
            return False, f"Aviso: Nenhum registro de refeição encontrado para {data_relatorio}."

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

            return True, f"Sucesso! Relatório TXT gerado na pasta."

        except Exception as e:
            print("\n--- ERRO AO GERAR TXT ---")
            traceback.print_exc()
            return False, f"Erro ao gerar o relatório: {str(e)}"