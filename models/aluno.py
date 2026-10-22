from models.pessoa import Pessoa


class Aluno(Pessoa):
    def __init__(self, nome, email, matricula):
        super().__init__(nome, email)
        self.__matricula = matricula

    @property
    def matricula(self):
        return self.__matricula

    def exibir_dados(self):
        return f"{super().exibir_dados()} | Matrícula: {self.__matricula}"
