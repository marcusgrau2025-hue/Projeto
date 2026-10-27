import database


def test_dados_persistem_no_banco(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "CAMINHO", tmp_path / "teste.db")
    database.criar_tabelas()
    database.executar(
        "INSERT INTO livros (titulo, autor, disponivel) VALUES (?, ?, 1)",
        ("Dom Casmurro", "Machado de Assis"),
    )
    linhas = database.consultar("SELECT * FROM livros")
    assert len(linhas) == 1
    assert linhas[0]["titulo"] == "Dom Casmurro"
