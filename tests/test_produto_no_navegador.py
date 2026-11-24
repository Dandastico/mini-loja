# Testes funcionais do produto: o funcionário cadastra, edita e exclui pelo navegador.
# Rodar só estes: pytest -m funcional tests/test_produto_no_navegador.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from passos import cadastrar_produto, esperar_a_resposta

pytestmark = pytest.mark.funcional


def itens_da_vitrine(navegador):
    return [li.text for li in navegador.find_elements(By.CSS_SELECTOR, "ul li")]


def item_do_produto(navegador, nome):
    return navegador.find_element(By.XPATH, f"//ul/li[contains(., '{nome}')]")


def test_cadastrar_um_produto_faz_ele_aparecer_na_vitrine_com_o_preco_formatado(
    navegador, loja, funcionario_logado
):
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5")

    assert any("Teclado mecânico · R$ 1.234,50" in item for item in itens_da_vitrine(navegador))


def test_editar_abre_o_formulario_preenchido_e_salvar_mostra_os_dados_novos_na_vitrine(
    navegador, loja, funcionario_logado
):
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5")

    item_do_produto(navegador, "Teclado mecânico").find_element(By.LINK_TEXT, "Editar").click()

    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h2[text()='Editar produto']/following::form[1]"))
    )
    nome = formulario.find_element(By.ID, "nome")
    preco = formulario.find_element(By.ID, "preco")
    assert nome.get_attribute("value") == "Teclado mecânico"
    assert float(preco.get_attribute("value")) == 1234.5

    nome.clear()
    nome.send_keys("Teclado sem fio")
    preco.clear()
    preco.send_keys("99.9")
    formulario.find_element(By.XPATH, ".//button[text()='Salvar alterações']").click()
    esperar_a_resposta(navegador, formulario)

    vitrine = itens_da_vitrine(navegador)
    assert any("Teclado sem fio · R$ 99,90" in item for item in vitrine)
    assert not any("Teclado mecânico" in item for item in vitrine)


def test_excluir_o_produto_tira_ele_da_vitrine_e_os_outros_continuam(navegador, loja, funcionario_logado):
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5")
    antes = itens_da_vitrine(navegador)
    outros = [item for item in antes if "Teclado mecânico" not in item]
    assert len(outros) == len(antes) - 1  # os 3 de exemplo

    botao = item_do_produto(navegador, "Teclado mecânico").find_element(By.XPATH, ".//button[text()='Excluir']")
    botao.click()
    esperar_a_resposta(navegador, botao)

    assert itens_da_vitrine(navegador) == outros


def test_recarregar_a_pagina_depois_de_salvar_nao_cadastra_o_produto_de_novo(navegador, loja, funcionario_logado):
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5")

    navegador.refresh()

    vitrine = itens_da_vitrine(navegador)
    assert len([item for item in vitrine if "Teclado mecânico" in item]) == 1
    assert navegador.find_element(By.XPATH, "//h2[starts-with(., 'Produtos')]").text == "Produtos (4)"
