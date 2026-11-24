# Testes unitários do CRUD de produtos (banco.php).
# Tudo é conferido pelas próprias funções de leitura do modelo, nunca por SQL direto.
#
# Num banco novo, os produtos de exemplo recebem os ids na ordem em que são inseridos:
# 1 = Placa ESP32, 2 = Arduino Uno, 3 = Sensor de temperatura DHT11.


def test_inserir_produto_faz_ele_aparecer_na_listagem_com_os_mesmos_valores(modelo):
    modelo("inserirProduto", "Raspberry Pi 5", 499.90, "raspberry.jpg")

    produtos = modelo("listarProdutos")

    assert {"id": 4, "nome": "Raspberry Pi 5", "preco": 499.9, "imagem": "raspberry.jpg"} in produtos
    assert len(produtos) == 4


def test_buscar_produto_pelo_id_devolve_nome_preco_e_imagem_dele(modelo):
    modelo("inserirProduto", "Raspberry Pi 5", 499.90, "raspberry.jpg")

    produto = modelo("buscarProduto", 4)

    assert produto == {"id": 4, "nome": "Raspberry Pi 5", "preco": 499.9, "imagem": "raspberry.jpg"}


def test_buscar_id_que_nao_existe_devolve_none(modelo):
    assert modelo("buscarProduto", 999) is None


def test_atualizar_produto_troca_nome_preco_e_imagem_e_os_outros_continuam_iguais(modelo):
    modelo("atualizarProduto", 1, "Placa ESP32-S3", 54.90, "esp32s3.jpg")

    assert modelo("listarProdutos") == [
        {"id": 2, "nome": "Arduino Uno", "preco": 59.9, "imagem": None},
        {"id": 1, "nome": "Placa ESP32-S3", "preco": 54.9, "imagem": "esp32s3.jpg"},
        {"id": 3, "nome": "Sensor de temperatura DHT11", "preco": 12.5, "imagem": None},
    ]


def test_excluir_produto_tira_ele_da_listagem_e_os_outros_continuam(modelo):
    modelo("excluirProduto", 2)

    assert modelo("listarProdutos") == [
        {"id": 1, "nome": "Placa ESP32", "preco": 39.9, "imagem": None},
        {"id": 3, "nome": "Sensor de temperatura DHT11", "preco": 12.5, "imagem": None},
    ]
