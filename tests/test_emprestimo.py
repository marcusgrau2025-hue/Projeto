import pytest
from models.aluno import Aluno
from models.livro import Livro
from models.emprestimo import Emprestimo


def test_emprestimo_deixa_livro_indisponivel():
    aluno = Aluno("Ana", "ana@email.com", "2026001")
    livro = Livro("Dom Casmurro", "Machado de Assis")
    Emprestimo(aluno, livro)
    assert livro.disponivel is False


def test_nao_empresta_livro_ja_emprestado():
    aluno = Aluno("Ana", "ana@email.com", "2026001")
    livro = Livro("O Cortiço", "Aluísio Azevedo")
    Emprestimo(aluno, livro)
    with pytest.raises(ValueError):
        Emprestimo(aluno, livro)
