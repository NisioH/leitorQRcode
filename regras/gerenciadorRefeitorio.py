class GerenciadorRefeitorio:
    def __init__(self, banco_de_dados):
        self.db = banco_de_dados

    def processar_leitura_qr(self, texto_qr):
        try:
            partes = texto_qr.split('|')
            if len(partes) != 3:
                return False, "Aviso: QR Code inválido ou sujo."

            inscricao, nome, secao = partes

            if self.db.verificou_refeicao_hoje(inscricao):
                return False, f"Atenção: {nome} já registrou refeição hoje!"

            self.db.registrar_refeicao(nome, inscricao, secao)
            return True, f"Sucesso: {nome} registrado ({secao})."

        except Exception as e:
            return False, f"Erro interno: {str(e)}"