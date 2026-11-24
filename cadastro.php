<?php
// cadastro.php: o CONTROLE.
// Recebe o formulário, pede ao modelo (banco.php) e chama a visão (tela.php).
// NOVO: a sessão conta quem está logado
session_start();
require __DIR__ . '/banco.php';
// a conferência da foto mora num arquivo próprio
require __DIR__ . '/foto.php';

// NOVO: a tranca. Visitante só olha; mexer (cadastrar, editar, excluir) é com funcionário logado
$logado = $_SESSION['funcionario'] ?? '';
if ($logado === '' && ($_SERVER['REQUEST_METHOD'] === 'POST' || isset($_GET['editar']))) {
    header('Location: funcionario.php');
    exit;
}

// guarda a foto conferida com um nome inventado pelo sistema e devolve esse nome
function guardarImagem(array $arquivo): string
{
    $extensoes = [IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp'];
    $tipo = getimagesize($arquivo['tmp_name'])[2];

    // o nome que veio do computador do usuário é jogado fora
    $nome = bin2hex(random_bytes(8)) . '.' . $extensoes[$tipo];

    if (!is_dir(__DIR__ . '/uploads')) {
        mkdir(__DIR__ . '/uploads');
    }
    move_uploaded_file($arquivo['tmp_name'], __DIR__ . '/uploads/' . $nome);
    return $nome;
}

// tira uma foto da pasta uploads (basename impede sair da pasta)
function apagarImagem(string $nome): void
{
    $caminho = __DIR__ . '/uploads/' . basename($nome);
    if ($nome !== '' && is_file($caminho)) {
        unlink($caminho);
    }
}

// clicou em "Excluir"? apaga a foto, depois o produto, e volta para a página limpa
if (isset($_POST['excluir'])) {
    $id = (int) $_POST['excluir'];
    $produto = buscarProduto($id);
    if ($produto) {
        apagarImagem($produto['imagem'] ?? '');
    }
    excluirProduto($id);
    header('Location: cadastro.php');
    exit;
}

// começa sem aviso e sem produto para editar
$erro = '';
$produto = null;

// o formulário foi enviado? com id é edição; sem id é produto novo
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = (int) ($_POST['id'] ?? 0);
    $nome = trim($_POST['nome'] ?? '');
    $preco = (float) ($_POST['preco'] ?? 0);

    // escolheram uma foto? o vendedor confere antes de guardar
    $imagem = '';
    $temFoto = isset($_FILES['imagem']) && $_FILES['imagem']['error'] !== UPLOAD_ERR_NO_FILE;
    if ($temFoto) {
        $erro = conferirImagem($_FILES['imagem']);
    }

    if ($erro === '') {
        if ($temFoto) {
            $imagem = guardarImagem($_FILES['imagem']);
        }
        if ($id > 0) {
            // edição: sem foto nova, fica a de antes; com foto nova, a antiga sai da pasta
            $antigo = buscarProduto($id);
            $fotoAntiga = $antigo['imagem'] ?? '';
            if ($imagem === '') {
                $imagem = $fotoAntiga;
            } else {
                apagarImagem($fotoAntiga);
            }
            atualizarProduto($id, $nome, $preco, $imagem);
        } else {
            inserirProduto($nome, $preco, $imagem);
        }

        // volta para a página limpa: assim o F5 não grava de novo
        header('Location: cadastro.php');
        exit;
    }

    // deu problema: a tela volta com o aviso e com o que a pessoa já tinha digitado
    $produto = ['id' => $id ?: '', 'nome' => $nome, 'preco' => $preco];
}

// clicou em "Editar"? busca o produto para preencher o formulário
if (isset($_GET['editar'])) {
    $produto = buscarProduto((int) $_GET['editar']);
}

$produtos = listarProdutos();

require __DIR__ . '/tela.php';
