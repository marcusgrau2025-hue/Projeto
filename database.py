import sqlite3
from pathlib import Path

CAMINHO = Path(__file__).parent / "biblioteca.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    matricula TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    disponivel INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    data_emprestimo TEXT NOT NULL,
    data_prevista TEXT NOT NULL,
    data_devolucao TEXT,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);
"""


def conectar():
    conexao = sqlite3.connect(CAMINHO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    conexao = conectar()
    try:
        conexao.executescript(ESQUEMA)
        conexao.commit()
    finally:
        conexao.close()


def consultar(sql, parametros=()):
    conexao = conectar()
    try:
        return conexao.execute(sql, parametros).fetchall()
    finally:
        conexao.close()


def executar(sql, parametros=()):
    conexao = conectar()
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def executar_lote(comandos):
    conexao = conectar()
    try:
        for sql, parametros in comandos:
            conexao.execute(sql, parametros)
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
