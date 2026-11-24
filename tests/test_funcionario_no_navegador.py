# Testes funcionais da área do funcionário: cadastrar, entrar e sair pelo navegador.
# Rodar só estes: pytest -m funcional tests/test_funcionario_no_navegador.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from passos import cadastrar_funcionario, entrar

pytestmark = pytest.mark.funcional


def test_numa_loja_vazia_o_primeiro_funcionario_se_cadastra(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Ana Admin", "ana@loja.com", "senha-secreta")

    aviso = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(., 'Cadastro feito')]"))
    )
    assert aviso.text == "Cadastro feito, Ana Admin! Agora é só entrar."


def test_entrar_com_email_e_senha_certos_mostra_o_nome_do_funcionario(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Ana Admin", "ana@loja.com", "senha-secreta")

    entrar(navegador, loja, "ana@loja.com", "senha-secreta")

    saudacao = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]"))
    )
    assert saudacao.find_element(By.TAG_NAME, "strong").text == "Ana Admin"


def test_entrar_com_a_senha_errada_mostra_o_aviso_e_nao_loga(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Ana Admin", "ana@loja.com", "senha-secreta")

    entrar(navegador, loja, "ana@loja.com", "senha-errada")

    aviso = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(., 'Não deu:')]"))
    )
    assert aviso.text == "Não deu: E-mail ou senha errados."
    # continua na tela de entrada, sem saudação de ninguém logado
    assert navegador.find_elements(By.ID, "email-entrar")
    assert not navegador.find_elements(By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]")


def test_clicar_em_sair_volta_para_a_tela_de_entrada_sem_ninguem_logado(navegador, funcionario_logado):
    navegador.find_element(By.LINK_TEXT, "Sair").click()

    WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((By.ID, "email-entrar")))
    assert navegador.current_url.endswith("/funcionario.php")
    assert not navegador.find_elements(By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]")
