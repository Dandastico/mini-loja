# Testes unitários dos funcionários (banco.php).
# Tudo é conferido pelas próprias funções de leitura do modelo, nunca por SQL direto.

import pytest


def test_banco_novo_nao_tem_funcionarios(modelo):
    assert modelo("contarFuncionarios") == 0


def test_inserir_funcionario_conta_um_e_a_busca_pelo_email_devolve_os_dados_dele(modelo):
    modelo("inserirFuncionario", "Ana Souza", "ana@loja.com", "hash-da-ana")

    assert modelo("contarFuncionarios") == 1
    assert modelo("buscarFuncionario", "ana@loja.com") == {
        "id": 1,
        "nome": "Ana Souza",
        "email": "ana@loja.com",
        "senha": "hash-da-ana",
    }


def test_buscar_email_que_nao_esta_cadastrado_devolve_none(modelo):
    modelo("inserirFuncionario", "Ana Souza", "ana@loja.com", "hash-da-ana")

    assert modelo("buscarFuncionario", "bruno@loja.com") is None


def test_inserir_segundo_funcionario_com_o_mesmo_email_falha_e_a_contagem_continua_um(modelo):
    modelo("inserirFuncionario", "Ana Souza", "ana@loja.com", "hash-da-ana")

    with pytest.raises(RuntimeError, match="UNIQUE"):
        modelo("inserirFuncionario", "Outra Ana", "ana@loja.com", "outro-hash")

    assert modelo("contarFuncionarios") == 1
    assert modelo("buscarFuncionario", "ana@loja.com")["nome"] == "Ana Souza"


def test_o_modelo_guarda_o_hash_exatamente_como_recebeu(modelo):
    # Gerar o hash (password_hash) é trabalho do CONTROLE (funcionario.php).
    # O modelo só guarda: o que entra é o que sai, sem embaralhar de novo.
    hash_do_controle = "$2y$10$abcdefghijklmnopqrstuuJ9C8pYg7xQ0m1z2W3e4R5t6Y7u8I9o0"
    modelo("inserirFuncionario", "Ana Souza", "ana@loja.com", hash_do_controle)

    guardado = modelo("buscarFuncionario", "ana@loja.com")["senha"]

    assert guardado == "$2y$10$abcdefghijklmnopqrstuuJ9C8pYg7xQ0m1z2W3e4R5t6Y7u8I9o0"
