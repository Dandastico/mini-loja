# conftest.py: o que todos os testes compartilham.
#
# Cada teste ganha uma CÓPIA do app numa pasta temporária. Como o banco.php
# cria o mini-loja.sqlite ao lado dele (__DIR__), a cópia nasce com banco novo
# e o mini-loja.sqlite de verdade do projeto nunca é tocado.

import json
import shutil
import subprocess
from pathlib import Path

import pytest

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
