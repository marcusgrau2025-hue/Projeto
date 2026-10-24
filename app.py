from flask import Flask, render_template, request, redirect, url_for, flash
from models.aluno import Aluno
from models.livro import Livro
from models.emprestimo import Emprestimo

app = Flask(__name__)
app.secret_key = "biblioteca"

livros = []
alunos = []
emprestimos = []


@app.route("/")
def index():
    ativos = [e for e in emprestimos if e.data_devolucao is None]
    return render_template("index.html", total_livros=len(livros),
                           total_alunos=len(alunos), total_ativos=len(ativos))


@app.route("/livros", methods=["GET", "POST"])
def pagina_livros():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        if titulo and autor:
            livros.append(Livro(titulo, autor))
            flash("Livro cadastrado.")
        return redirect(url_for("pagina_livros"))
    busca = request.args.get("q", "").strip().lower()
    lista = [(i, l) for i, l in enumerate(livros)
             if busca in l.titulo.lower() or busca in l.autor.lower()]
    return render_template("livros.html", lista=lista, busca=busca)


@app.route("/livros/<int:i>/excluir", methods=["POST"])
def excluir_livro(i):
    if 0 <= i < len(livros):
        if livros[i].disponivel:
            livros.pop(i)
            flash("Livro excluído.")
        else:
            flash("Não é possível excluir um livro emprestado.")
    return redirect(url_for("pagina_livros"))


@app.route("/alunos", methods=["GET", "POST"])
def pagina_alunos():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        matricula = request.form["matricula"].strip()
        if nome and email and matricula:
            alunos.append(Aluno(nome, email, matricula))
            flash("Aluno cadastrado.")
        return redirect(url_for("pagina_alunos"))
    return render_template("alunos.html", lista=list(enumerate(alunos)))


@app.route("/alunos/<int:i>/excluir", methods=["POST"])
def excluir_aluno(i):
    if 0 <= i < len(alunos):
        alunos.pop(i)
        flash("Aluno excluído.")
    return redirect(url_for("pagina_alunos"))


@app.route("/emprestimos", methods=["GET", "POST"])
def pagina_emprestimos():
    if request.method == "POST":
        try:
            aluno = alunos[int(request.form["aluno"])]
            livro = livros[int(request.form["livro"])]
            if any(e.aluno is aluno and e.data_devolucao is None
                   and e.esta_atrasado() for e in emprestimos):
                flash("Aluno com empréstimo em atraso.")
            else:
                emprestimos.append(Emprestimo(aluno, livro))
                flash("Empréstimo registrado.")
        except (ValueError, IndexError, KeyError) as erro:
            flash(str(erro) if str(erro) else "Dados inválidos.")
        return redirect(url_for("pagina_emprestimos"))
    disponiveis = [(i, l) for i, l in enumerate(livros) if l.disponivel]
    return render_template("emprestimos.html", alunos=list(enumerate(alunos)),
                           disponiveis=disponiveis,
                           lista=list(enumerate(emprestimos)))


@app.route("/emprestimos/<int:i>/devolver", methods=["POST"])
def devolver(i):
    if 0 <= i < len(emprestimos) and emprestimos[i].data_devolucao is None:
        emprestimos[i].devolver()
        flash("Devolução registrada.")
    return redirect(url_for("pagina_emprestimos"))


if __name__ == "__main__":
    app.run(debug=True)
