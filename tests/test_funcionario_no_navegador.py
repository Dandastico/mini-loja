# Testes funcionais da área do funcionário: cadastrar, entrar e sair pelo navegador.
# Rodar só estes: pytest -m funcional tests/test_funcionario_no_navegador.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from passos import cadastrar_funcionario, entrar, esperar_a_resposta

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


def test_funcionario_logado_chega_ao_cadastro_de_colega_pelo_link_da_vitrine(navegador, loja, funcionario_logado):
    navegador.get(f"{loja}/cadastro.php")

    navegador.find_element(By.LINK_TEXT, "Cadastrar funcionário").click()

    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//form[input[@name='acao' and @value='cadastrar']]"))
    )
    assert formulario.find_element(By.ID, "nome").is_displayed()


def test_visitante_que_so_ve_o_entrar_fica_sabendo_quem_cadastra_funcionario_novo(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Ana Admin", "ana@loja.com", "senha-secreta")

    navegador.get(f"{loja}/funcionario.php")

    explicacao = navegador.find_element(By.XPATH, "//p[contains(., 'funcionário novo')]")
    assert "logado" in explicacao.text


def test_apertar_enter_com_os_campos_vazios_entra_com_a_conta_de_teste_mostrada_nas_dicas(navegador, loja):
    cadastrar_funcionario(navegador, loja, "Carla Teste", "teste@loja.com", "relogio123")
    navegador.get(f"{loja}/funcionario.php")
    email = navegador.find_element(By.ID, "email-entrar")
    assert email.get_attribute("placeholder") == "teste@loja.com"
    assert navegador.find_element(By.ID, "senha-entrar").get_attribute("placeholder") == "relogio123"

    formulario = navegador.find_element(By.XPATH, "//form[input[@name='acao' and @value='entrar']]")
    email.send_keys(Keys.ENTER)
    esperar_a_resposta(navegador, formulario)

    saudacao = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[starts-with(normalize-space(.), 'Olá,')]"))
    )
    assert saudacao.find_element(By.TAG_NAME, "strong").text == "Carla Teste"
