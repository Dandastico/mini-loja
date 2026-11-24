# imagens.py: fotos de verdade, geradas pelos próprios testes (nada de arquivo solto no projeto).

import struct
import zlib


def png(largura=1, altura=1):
    """Os bytes de um PNG de verdade, todo vermelho, montado pedaço por pedaço."""

    def pedaco(tipo, dados):
        # cada pedaço do PNG: tamanho, tipo, dados e o CRC (a conferência) de tipo+dados
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados))

    assinatura = b"\x89PNG\r\n\x1a\n"
    cabecalho = struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)  # 8 bits, cores RGB
    linha = b"\x00" + b"\xff\x00\x00" * largura  # cada linha: sem filtro + pixels vermelhos
    pixels = zlib.compress(linha * altura)
    return assinatura + pedaco(b"IHDR", cabecalho) + pedaco(b"IDAT", pixels) + pedaco(b"IEND", b"")
