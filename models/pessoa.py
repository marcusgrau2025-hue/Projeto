class Pessoa:
    def __init__(self, nome, email):
        self.__nome = nome
        self.__email = email

    @property
    def nome(self):
        return self.__nome

    @property
    def email(self):
        return self.__email

    def exibir_dados(self):
        return f"Nome: {self.__nome} | E-mail: {self.__email}"
