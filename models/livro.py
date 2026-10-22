class Livro:
    def __init__(self, titulo, autor):
        self.__titulo = titulo
        self.__autor = autor
        self.__disponivel = True

    @property
    def titulo(self):
        return self.__titulo

    @property
    def autor(self):
        return self.__autor

    @property
    def disponivel(self):
        return self.__disponivel

    def emprestar(self):
        if not self.__disponivel:
            raise ValueError("Livro já está emprestado.")
        self.__disponivel = False

    def devolver(self):
        self.__disponivel = True

    def exibir_dados(self):
        status = "Disponível" if self.__disponivel else "Emprestado"
        return f"{self.__titulo} - {self.__autor} ({status})"
