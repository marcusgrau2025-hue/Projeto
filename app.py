import sqlite3
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash

import database
from models.aluno import Aluno
from models.livro import Livro
from models.emprestimo import Emprestimo

app = Flask(__name__)
app.secret_key = "biblioteca"

database.criar_tabelas()


def contar(sql):
    return database.consultar(sql)[0]["n"]


@app.route("/")
def index():
    return render_template(
        "index.html",
        total_livros=contar("SELECT COUNT(*) AS n FROM livros"),
        total_alunos=contar("SELECT COUNT(*) AS n FROM alunos"),
        total_ativos=contar(
            "SELECT COUNT(*) AS n FROM emprestimos WHERE data_devolucao IS NULL"
        ),
    )


@app.route("/livros", methods=["GET", "POST"])
def pagina_livros():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        if titulo and autor:
            livro = Livro(titulo, autor)
            database.executar(
                "INSERT INTO livros (titulo, autor, disponivel) VALUES (?, ?, 1)",
                (livro.titulo, livro.autor),
            )
            flash("Livro cadastrado.")
        return redirect(url_for("pagina_livros"))
    busca = request.args.get("q", "").strip().lower()
    linhas = database.consultar("SELECT * FROM livros ORDER BY titulo")
    lista = [
        (l["id"], l)
        for l in linhas
        if busca in l["titulo"].lower() or busca in l["autor"].lower()
    ]
    return render_template("livros.html", lista=lista, busca=busca)


@app.route("/livros/<int:i>/excluir", methods=["POST"])
def excluir_livro(i):
    linhas = database.consultar("SELECT * FROM livros WHERE id = ?", (i,))
    if not linhas:
        flash("Livro não encontrado.")
    elif not linhas[0]["disponivel"]:
        flash("Não é possível excluir um livro emprestado.")
    else:
        try:
            database.executar("DELETE FROM livros WHERE id = ?", (i,))
            flash("Livro excluído.")
        except sqlite3.IntegrityError:
            flash("Livro com histórico de empréstimos não pode ser excluído.")
    return redirect(url_for("pagina_livros"))


@app.route("/alunos", methods=["GET", "POST"])
def pagina_alunos():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        matricula = request.form["matricula"].strip()
        if nome and email and matricula:
            aluno = Aluno(nome, email, matricula)
            try:
                database.executar(
                    "INSERT INTO alunos (nome, email, matricula) VALUES (?, ?, ?)",
                    (aluno.nome, aluno.email, aluno.matricula),
                )
                flash("Aluno cadastrado.")
            except sqlite3.IntegrityError:
                flash("Matrícula já cadastrada.")
        return redirect(url_for("pagina_alunos"))
    linhas = database.consultar("SELECT * FROM alunos ORDER BY nome")
    return render_template("alunos.html", lista=[(a["id"], a) for a in linhas])


@app.route("/alunos/<int:i>/excluir", methods=["POST"])
def excluir_aluno(i):
    try:
        database.executar("DELETE FROM alunos WHERE id = ?", (i,))
        flash("Aluno excluído.")
    except sqlite3.IntegrityError:
        flash("Aluno com histórico de empréstimos não pode ser excluído.")
    return redirect(url_for("pagina_alunos"))


@app.route("/emprestimos", methods=["GET", "POST"])
def pagina_emprestimos():
    if request.method == "POST":
        try:
            aluno_id = int(request.form["aluno"])
            livro_id = int(request.form["livro"])
            alunos = database.consultar("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
            livros = database.consultar("SELECT * FROM livros WHERE id = ?", (livro_id,))
            if not alunos or not livros:
                raise ValueError("Dados inválidos.")
            atrasados = database.consultar(
                "SELECT 1 FROM emprestimos WHERE aluno_id = ? "
                "AND data_devolucao IS NULL AND data_prevista < ?",
                (aluno_id, date.today().isoformat()),
            )
            if atrasados:
                flash("Aluno com empréstimo em atraso.")
            else:
                a, l = alunos[0], livros[0]
                aluno = Aluno(a["nome"], a["email"], a["matricula"])
                livro = Livro(l["titulo"], l["autor"], bool(l["disponivel"]))
                emprestimo = Emprestimo(aluno, livro)
                database.executar_lote([
                    (
                        "INSERT INTO emprestimos (aluno_id, livro_id, "
                        "data_emprestimo, data_prevista) VALUES (?, ?, ?, ?)",
                        (aluno_id, livro_id,
                         emprestimo.data_emprestimo.isoformat(),
                         emprestimo.data_prevista.isoformat()),
                    ),
                    ("UPDATE livros SET disponivel = 0 WHERE id = ?", (livro_id,)),
                ])
                flash("Empréstimo registrado.")
        except (ValueError, KeyError) as erro:
            flash(str(erro) or "Dados inválidos.")
        return redirect(url_for("pagina_emprestimos"))

    alunos = database.consultar("SELECT * FROM alunos ORDER BY nome")
    disponiveis = database.consultar(
        "SELECT * FROM livros WHERE disponivel = 1 ORDER BY titulo"
    )
    linhas = database.consultar(
        "SELECT e.id, a.nome AS aluno_nome, l.titulo AS livro_titulo, "
        "e.data_prevista, e.data_devolucao "
        "FROM emprestimos e "
        "JOIN alunos a ON a.id = e.aluno_id "
        "JOIN livros l ON l.id = e.livro_id "
        "ORDER BY e.id DESC"
    )
    hoje = date.today()
    lista = []
    for r in linhas:
        prevista = date.fromisoformat(r["data_prevista"])
        devolvido = r["data_devolucao"] is not None
        lista.append({
            "id": r["id"],
            "aluno": r["aluno_nome"],
            "livro": r["livro_titulo"],
            "prazo": prevista.strftime("%d/%m/%Y"),
            "devolvido": devolvido,
            "atrasado": (not devolvido) and hoje > prevista,
        })
    return render_template(
        "emprestimos.html",
        alunos=[(a["id"], a) for a in alunos],
        disponiveis=[(l["id"], l) for l in disponiveis],
        lista=lista,
    )


@app.route("/emprestimos/<int:i>/devolver", methods=["POST"])
def devolver(i):
    linhas = database.consultar(
        "SELECT * FROM emprestimos WHERE id = ? AND data_devolucao IS NULL", (i,)
    )
    if linhas:
        database.executar_lote([
            ("UPDATE emprestimos SET data_devolucao = ? WHERE id = ?",
             (date.today().isoformat(), i)),
            ("UPDATE livros SET disponivel = 1 WHERE id = ?", (linhas[0]["livro_id"],)),
        ])
        flash("Devolução registrada.")
    return redirect(url_for("pagina_emprestimos"))


if __name__ == "__main__":
    app.run(debug=True)
