# Testes unitários da conferência da foto (foto.php).
# Cada arquivo usado aqui é gerado pelo próprio teste, numa pasta temporária.

from imagens import png


def test_arquivo_acima_de_2_mb_e_recusado(conferir_foto, tmp_path):
    grande = tmp_path / "grande.jpg"
    grande.write_bytes(b"\0" * (2 * 1024 * 1024 + 1))

    assert conferir_foto(grande) == "A foto passou de 2 MB. Diminua e tente de novo."


def test_arquivo_vazio_e_recusado(conferir_foto, tmp_path):
    vazio = tmp_path / "vazio.png"
    vazio.write_bytes(b"")

    assert conferir_foto(vazio) == "A foto chegou vazia."


def test_arquivo_de_texto_renomeado_para_jpg_e_recusado(conferir_foto, tmp_path):
    falso = tmp_path / "foto.jpg"
    falso.write_text("isto é só um texto, não uma foto\n")

    assert conferir_foto(falso) == "Isso não é uma foto JPG, PNG ou WEBP."


def test_png_pequeno_e_valido_e_aceito(conferir_foto, tmp_path):
    foto = tmp_path / "foto.png"
    foto.write_bytes(png())

    assert conferir_foto(foto) == ""
