# conftest.py: o que todos os testes compartilham.
#
# Cada teste ganha uma CÓPIA do app numa pasta temporária. Como o banco.php
# cria o mini-loja.sqlite ao lado dele (__DIR__), a cópia nasce com banco novo
# e o mini-loja.sqlite de verdade do projeto nunca é tocado.

import json
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

RAIZ = Path(__file__).resolve().parent.parent

# os arquivos do app (o banco e a pasta uploads ficam de fora de propósito)
ARQUIVOS_DO_APP = ["*.php", "*.html"]

# roda dentro do php: carrega o modelo, chama a função pedida com os
# argumentos que chegaram em JSON e devolve o resultado em JSON
CHAMADA_PHP = r"""
require 'banco.php';
$pedido = json_decode(stream_get_contents(STDIN), true);
echo json_encode($pedido['funcao'](...$pedido['args']));
"""


# roda dentro do php: carrega SÓ a regra da foto (sem o controle) e confere
# um arquivo que chega do jeito que o PHP entrega um upload em $_FILES
CONFERIR_FOTO_PHP = r"""
require 'foto.php';
$caminho = stream_get_contents(STDIN);
echo json_encode(conferirImagem([
    'name' => basename($caminho),
    'tmp_name' => $caminho,
    'size' => filesize($caminho),
    'error' => UPLOAD_ERR_OK,
]));
"""


def comando_php():
    """O php, já com o pdo_sqlite ligado.

    Se o php.ini deixa o pdo_sqlite desligado (o padrão em várias instalações),
    ele é ligado só para os testes, sem mexer no php.ini.
    """
    modulos = subprocess.run(["php", "-m"], capture_output=True, text=True).stdout
    if "pdo_sqlite" in modulos.split():
        return ["php"]
    return ["php", "-d", "extension=pdo_sqlite"]


PHP = comando_php()


def pytest_addoption(parser):
    parser.addoption(
        "--com-janela",
        action="store_true",
        help="abre o navegador com janela (sem headless), para ver os testes funcionais rodando",
    )


@pytest.fixture
def app(tmp_path):
    """Pasta com uma cópia isolada do app; o pytest apaga no fim."""
    pasta = tmp_path / "mini-loja"
    pasta.mkdir()
    for padrao in ARQUIVOS_DO_APP:
        for arquivo in RAIZ.glob(padrao):
            shutil.copy(arquivo, pasta)
    return pasta


@pytest.fixture
def modelo(app):
    """Chama uma função do banco.php na cópia do app e devolve o resultado em Python.

    Exemplo: modelo("buscarProduto", 1)
    """

    def chamar(funcao, *args):
        resultado = subprocess.run(
            [*PHP, "-r", CHAMADA_PHP],
            cwd=app,
            input=json.dumps({"funcao": funcao, "args": list(args)}),
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            raise RuntimeError(
                f"o PHP falhou em {funcao}{args}:\n{resultado.stdout}{resultado.stderr}"
            )
        return json.loads(resultado.stdout)

    return chamar


@pytest.fixture
def conferir_foto(app):
    """Passa um arquivo pela conferência da foto e devolve a resposta dela.

    '' quer dizer foto aceita; qualquer outro texto é a frase do problema.
    Exemplo: conferir_foto(tmp_path / "foto.png")
    """

    def conferir(caminho):
        resultado = subprocess.run(
            [*PHP, "-r", CONFERIR_FOTO_PHP],
            cwd=app,
            input=str(caminho),
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            raise RuntimeError(
                f"o PHP falhou ao conferir {caminho}:\n{resultado.stdout}{resultado.stderr}"
            )
        return json.loads(resultado.stdout)

    return conferir


def porta_livre():
    """Pede ao sistema uma porta que ninguém está usando."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def loja(app, tmp_path):
    """Sobe o servidor embutido do PHP na cópia do app e devolve o endereço.

    O banco e a pasta uploads nascem dentro da cópia; os do projeto não mudam.
    """
    (app / "uploads").mkdir()
    porta = porta_livre()
    endereco = f"http://127.0.0.1:{porta}"
    with open(tmp_path / "servidor-php.log", "w") as log:
        servidor = subprocess.Popen(
            [*PHP, "-S", f"127.0.0.1:{porta}", "-t", str(app)],
            cwd=app,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    try:
        # espera o servidor responder (até 10 s) antes de entregar o endereço
        prazo = time.monotonic() + 10
        while True:
            try:
                urllib.request.urlopen(f"{endereco}/index.html", timeout=1)
                break
            except OSError:
                if servidor.poll() is not None or time.monotonic() > prazo:
                    raise RuntimeError(
                        "o servidor PHP não respondeu:\n"
                        + (tmp_path / "servidor-php.log").read_text()
                    )
                time.sleep(0.05)
        yield endereco
    finally:
        servidor.terminate()
        servidor.wait(timeout=5)


def caminho_do_chrome():
    """O Chromium (ou o Chrome) instalado na máquina; None deixa o Selenium procurar."""
    for nome in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]:
        caminho = shutil.which(nome)
        if caminho:
            return caminho
    return None


@pytest.fixture
def navegador(request):
    """Um Chrome headless (ou com janela, com --com-janela) que fecha no fim, mesmo se o teste falhar."""
    opcoes = webdriver.ChromeOptions()
    if not request.config.getoption("--com-janela"):
        opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1280,900")
    chrome = caminho_do_chrome()
    if chrome:
        opcoes.binary_location = chrome
    driver = shutil.which("chromedriver")
    servico = Service(driver) if driver else Service()
    nav = webdriver.Chrome(options=opcoes, service=servico)
    yield nav
    nav.quit()


@pytest.fixture
def funcionario_logado(navegador, loja):
    """O navegador já com um funcionário logado (o administrador da loja vazia).

    Devolve os dados dele. Exemplo: def test_algo(navegador, funcionario_logado): ...
    """
    from passos import cadastrar_funcionario, entrar

    dados = {"nome": "Ana Admin", "email": "ana@loja.com", "senha": "senha-secreta"}
    cadastrar_funcionario(navegador, loja, dados["nome"], dados["email"], dados["senha"])
    entrar(navegador, loja, dados["email"], dados["senha"])
    return dados
