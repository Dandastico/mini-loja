# Testes unitários do MODELO (banco.php): chamam as funções PHP de verdade.


def test_banco_novo_lista_os_3_produtos_de_exemplo_em_ordem_alfabetica(modelo):
    produtos = modelo("listarProdutos")

    nomes = [p["nome"] for p in produtos]
    assert nomes == ["Arduino Uno", "Placa ESP32", "Sensor de temperatura DHT11"]
