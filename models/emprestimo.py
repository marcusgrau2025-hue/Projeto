from datetime import date, timedelta


class Emprestimo:
    PRAZO_DIAS = 7

    def __init__(self, aluno, livro):
        livro.emprestar()
        self.aluno = aluno
        self.livro = livro
        self.data_emprestimo = date.today()
        self.data_prevista = self.data_emprestimo + timedelta(days=self.PRAZO_DIAS)
        self.data_devolucao = None

    def devolver(self):
        self.livro.devolver()
        self.data_devolucao = date.today()

    def esta_atrasado(self):
        return self.data_devolucao is None and date.today() > self.data_prevista
