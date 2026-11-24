# Testes funcionais da tranca: o visitante só olha a loja.
# Rodar só estes: pytest -m funcional tests/test_tranca_no_navegador.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from passos import cadastrar_funcionario, entrar, enviar_por_fora

pytestmark = pytest.mark.funcional


def itens_da_vitrine(navegador):
    return [li.text for li in navegador.find_elements(By.CSS_SELECTOR, "ul li")]


def test_visitante_ve_a_vitrine_mas_nao_consegue_editar_nem_excluir(navegador, loja):
    navegador.get(f"{loja}/cadastro.php")

    vitrine = itens_da_vitrine(navegador)
    assert any("Placa ESP32" in item for item in vitrine)
    assert not navegador.find_elements(By.LINK_TEXT, "Editar")
    assert not navegador.find_elements(By.XPATH, "//button[text()='Excluir']")

    # tentar excluir mesmo assim (mandando o pedido sem o botão) leva à tela do funcionário
    enviar_por_fora(navegador, loja, "cadastro.php", {"excluir": "1"})

    WebDriverWait(navegador, 10).until(EC.url_contains("/funcionario.php"))
    navegador.get(f"{loja}/cadastro.php")
    assert itens_da_vitrine(navegador) == vitrine


def test_visitante_que_abre_o_endereco_de_edicao_vai_para_a_tela_do_funcionario(navegador, loja):
    navegador.get(f"{loja}/cadastro.php?editar=1")

    WebDriverWait(navegador, 10).until(EC.url_contains("/funcionario.php"))
    assert not navegador.find_elements(By.XPATH, "//h2[text()='Editar produto']")


def test_com_um_funcionario_cadastrado_visitante_nao_cadastra_funcionario_novo(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Ana Admin", "ana@loja.com", "senha-secreta")

    navegador.get(f"{loja}/funcionario.php")
    assert not navegador.find_elements(By.XPATH, "//form[input[@name='acao' and @value='cadastrar']]")

    # tentar cadastrar mesmo assim (mandando o pedido sem o formulário) é recusado
    enviar_por_fora(navegador, loja, "funcionario.php", {
        "acao": "cadastrar", "nome": "Intruso", "email": "intruso@loja.com", "senha": "senha-do-intruso",
    })
    aviso = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(., 'Não deu:')]"))
    )
    assert aviso.text == "Não deu: Só um funcionário logado cadastra outro."

    # e o intruso não consegue entrar
    entrar(navegador, loja, "intruso@loja.com", "senha-do-intruso")
    assert not navegador.find_elements(By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]")


def test_funcionario_logado_cadastra_outro_funcionario(navegador, loja, funcionario_logado):
    cadastrar_funcionario(navegador, loja, "Bruno Balcão", "bruno@loja.com", "senha-do-bruno")

    aviso = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(., 'Cadastro feito')]"))
    )
    assert aviso.text == "Cadastro feito, Bruno Balcão! Agora é só entrar."

    # o colega novo consegue entrar com o e-mail e a senha dele
    navegador.get(f"{loja}/funcionario.php?sair=1")
    entrar(navegador, loja, "bruno@loja.com", "senha-do-bruno")
    saudacao = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]"))
    )
    assert saudacao.find_element(By.TAG_NAME, "strong").text == "Bruno Balcão"
