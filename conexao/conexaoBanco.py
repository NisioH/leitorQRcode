import sqlite3
from datetime import date


class BancoDeDados:
    def __init__(self, nome_banco="refeitorio.db"):
        self.nome_banco = nome_banco
        self._criar_tabelas()

    def _conectar(self):
        return sqlite3.connect(self.nome_banco)

    def _criar_tabelas(self):
        conexao = self._conectar()
        cursor = conexao.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS refeicoes
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           nome
                           TEXT
                           NOT
                           NULL,
                           inscricao
                           TEXT
                           NOT
                           NULL,
                           secao
                           TEXT
                           NOT
                           NULL,
                           data_hora
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conexao.commit()
        conexao.close()

    def registrar_refeicao(self, nome, inscricao, secao):
        conexao = self._conectar()
        cursor = conexao.cursor()

        cursor.execute('''
                       INSERT INTO refeicoes (nome, inscricao, secao)
                       VALUES (?, ?, ?)
                       ''', (nome, inscricao, secao))

        conexao.commit()
        conexao.close()

    def verificou_refeicao_hoje(self, inscricao):
        conexao = self._conectar()
        cursor = conexao.cursor()

        data_hoje = date.today().isoformat()

        cursor.execute('''
                       SELECT id
                       FROM refeicoes
                       WHERE inscricao = ? AND date (data_hora) = ?
                       ''', (inscricao, data_hoje))

        resultado = cursor.fetchone()
        conexao.close()

        return resultado is not None

    def buscar_refeicoes_do_dia(self, data_busca=None):
        if data_busca is None:
            data_busca = date.today().isoformat()

        conexao = self._conectar()
        cursor = conexao.cursor()

        cursor.execute('''
                       SELECT nome, secao
                       FROM refeicoes
                       WHERE date (data_hora) = ?
                       ORDER BY secao, nome
                       ''', (data_busca,))

        resultados = cursor.fetchall()
        conexao.close()

        return resultados