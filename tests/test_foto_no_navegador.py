# Testes funcionais da foto do produto: o funcionário envia, vê e troca a foto pelo navegador.
# As fotos são geradas pelo teste numa pasta temporária e o upload cai na cópia do app.
# Rodar só estes: pytest -m funcional tests/test_foto_no_navegador.py

import pytest
from selenium.webdriver.common.by import By

from imagens import png
from passos import cadastrar_produto, editar_produto

pytestmark = pytest.mark.funcional


def foto_do_produto(navegador, nome):
    """A <img> do produto na vitrine."""
    return navegador.find_element(By.XPATH, f"//ul/li[contains(., '{nome}')]//img")


def tamanho_carregado(navegador, imagem):
    """Largura e altura que o navegador conseguiu desenhar (0x0 = a imagem não carregou)."""
    return tuple(navegador.execute_script("return [arguments[0].naturalWidth, arguments[0].naturalHeight]", imagem))


def test_cadastrar_com_um_png_valido_mostra_a_foto_na_vitrine_e_ela_carrega(
    navegador, loja, funcionario_logado, tmp_path
):
    foto = tmp_path / "teclado.png"
    foto.write_bytes(png(3, 2))

    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5", foto=foto)

    assert tamanho_carregado(navegador, foto_do_produto(navegador, "Teclado mecânico")) == (3, 2)


def test_enviar_um_arquivo_que_nao_e_imagem_mostra_o_aviso_e_o_formulario_volta_preenchido(
    navegador, loja, funcionario_logado, tmp_path
):
    falsa = tmp_path / "teclado.png"
    falsa.write_text("isto é só um texto com nome de foto\n")

    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5", foto=falsa)

    aviso = navegador.find_element(By.XPATH, "//p[strong[text()='Foto recusada:']]")
    assert aviso.text == "Foto recusada: Isso não é uma foto JPG, PNG ou WEBP."
    assert navegador.find_element(By.ID, "nome").get_attribute("value") == "Teclado mecânico"
    assert float(navegador.find_element(By.ID, "preco").get_attribute("value")) == 1234.5
    assert not navegador.find_elements(By.XPATH, "//ul/li[contains(., 'Teclado mecânico')]")


def test_editar_o_produto_com_outra_foto_mostra_a_foto_nova_na_vitrine(navegador, loja, funcionario_logado, tmp_path):
    antiga = tmp_path / "antiga.png"
    antiga.write_bytes(png(3, 2))
    nova = tmp_path / "nova.png"
    nova.write_bytes(png(5, 4))
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5", foto=antiga)

    editar_produto(navegador, "Teclado mecânico", foto=nova)

    assert tamanho_carregado(navegador, foto_do_produto(navegador, "Teclado mecânico")) == (5, 4)


def test_editar_o_produto_sem_escolher_foto_mantem_a_foto_de_antes(navegador, loja, funcionario_logado, tmp_path):
    foto = tmp_path / "teclado.png"
    foto.write_bytes(png(3, 2))
    cadastrar_produto(navegador, loja, "Teclado mecânico", "1234.5", foto=foto)

    editar_produto(navegador, "Teclado mecânico")

    assert tamanho_carregado(navegador, foto_do_produto(navegador, "Teclado mecânico")) == (3, 2)
