# Testes funcionais da vitrine: um navegador de verdade abre a Mini Loja.
# Rodar só estes: pytest -m funcional   (e para ver a janela: --com-janela)

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.funcional


def test_visitante_segue_o_link_da_vitrine_e_ve_os_3_produtos_de_exemplo(navegador, loja):
    navegador.get(f"{loja}/index.html")

    navegador.find_element(By.LINK_TEXT, "Ver os produtos").click()

    # esperas explícitas: primeiro chegar na vitrine (o index.html também tem <li>),
    # depois a lista de produtos estar na página
    espera = WebDriverWait(navegador, 10)
    espera.until(EC.url_contains("cadastro.php"))
    itens = espera.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li")))
    vitrine = " ".join(item.text for item in itens)
    for nome in ["Arduino Uno", "Placa ESP32", "Sensor de temperatura DHT11"]:
        assert nome in vitrine
