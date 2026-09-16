import sqlite3
import os
import sys
from datetime import date


def obter_pasta_dados():
    """Retorna uma pasta permanente para guardar o banco de dados.

    - Em desenvolvimento (python main.py): usa a pasta do projeto.
    - Como .exe (PyInstaller): usa %APPDATA%\\LeitorQRCode no Windows,
      ou ~/.local/share/LeitorQRCode no Linux.
    """
    if getattr(sys, 'frozen', False):
        # Rodando como executável
        if sys.platform.startswith('win'):
            base = os.getenv('APPDATA') or os.path.expanduser('~')
        else:
            base = os.path.join(os.path.expanduser('~'), '.local', 'share')
        pasta = os.path.join(base, "LeitorQRCode")
    else:
        # Rodando em desenvolvimento
        pasta = os.path.abspath(".")

    os.makedirs(pasta, exist_ok=True)
    return pasta


class BancoDeDados:
    def __init__(self, nome_banco="refeitorio.db"):
        pasta = obter_pasta_dados()
        self.nome_banco = os.path.join(pasta, nome_banco)
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