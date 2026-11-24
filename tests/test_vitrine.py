# Testes funcionais da vitrine: um navegador de verdade abre a Mini Loja.
# Rodar só estes: pytest -m funcional   (e para ver a janela: --com-janela)

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.funcional


def test_visitante_segue_o_link_da_vitrine_e_ve_os_3_produtos_de_exemplo(navegador, loja):
    navegador.get(f"{loja}/")

    navegador.find_element(By.LINK_TEXT, "Ver os produtos").click()

    # esperas explícitas: primeiro chegar na vitrine (a página inicial também tem <li>),
    # depois a lista de produtos estar na página
    espera = WebDriverWait(navegador, 10)
    espera.until(EC.url_contains("cadastro.php"))
    itens = espera.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li")))
    vitrine = " ".join(item.text for item in itens)
    for nome in ["Arduino Uno", "Placa ESP32", "Sensor de temperatura DHT11"]:
        assert nome in vitrine


def test_pagina_inicial_mostra_os_produtos_em_grade_com_o_menu_no_topo(navegador, loja):
    navegador.get(f"{loja}/")

    menu = navegador.find_element(By.CSS_SELECTOR, "header nav")
    assert [link.text for link in menu.find_elements(By.TAG_NAME, "a")] == ["Ver os produtos", "Área do funcionário"]
    assert not navegador.find_elements(By.LINK_TEXT, "Testar o ambiente")

    vitrine = [item.text for item in navegador.find_elements(By.CSS_SELECTOR, "ul li")]
    for produto in ["Arduino Uno · R$ 59,90", "Placa ESP32 · R$ 39,90", "Sensor de temperatura DHT11 · R$ 12,50"]:
        assert any(produto in item for item in vitrine)


def test_pagina_inicial_abre_com_o_banner_da_loja(navegador, loja):
    navegador.get(f"{loja}/")

    banner = navegador.find_element(By.CSS_SELECTOR, "main img.banner")
    largura = navegador.execute_script("return arguments[0].complete && arguments[0].naturalWidth", banner)
    assert largura == 687
    assert "Mini Loja" in banner.get_attribute("alt")
