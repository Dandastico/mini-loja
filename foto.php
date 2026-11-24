<?php
// foto.php: a REGRA que decide se uma foto enviada é aceita.
// Fica num arquivo só dela para poder ser carregada (e testada) sem rodar o controle.

// o vendedor confere a foto antes de pôr na vitrine.
// Devolve '' quando está tudo certo, ou a frase do problema.
function conferirImagem(array $arquivo): string
{
    // grande demais? (o php.ini também tem um limite, o upload_max_filesize)
    if ($arquivo['error'] === UPLOAD_ERR_INI_SIZE || $arquivo['size'] > 2 * 1024 * 1024) {
        return 'A foto passou de 2 MB. Diminua e tente de novo.';
    }
    if ($arquivo['error'] !== UPLOAD_ERR_OK) {
        return 'A foto não chegou inteira. Tente de novo.';
    }
    if ($arquivo['size'] === 0) {
        return 'A foto chegou vazia.';
    }
    // getimagesize olha DENTRO do arquivo; o nome pode mentir, o conteúdo não
    $info = getimagesize($arquivo['tmp_name']);
    if ($info === false || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP])) {
        return 'Isso não é uma foto JPG, PNG ou WEBP.';
    }
    return '';
}
