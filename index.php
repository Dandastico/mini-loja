<?php
// index.php: a página inicial, a vitrine da loja. Busca os produtos no modelo e mostra a grade.
session_start();
require __DIR__ . '/banco.php';

// quem está logado vê "Editar" e "Excluir" nos cartões, como na tela de produtos
$logado = $_SESSION['funcionario'] ?? '';
$produtos = listarProdutos();
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <!-- viewport: o celular mostra a página no tamanho dele, e não uma miniatura do computador -->
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mini Loja</title>
  <link rel="stylesheet" href="estilo.css">
</head>
<body>
  <?php require __DIR__ . '/topo.php'; ?>

  <main class="conteudo">
    <section class="destaque">
      <h1>Mini Loja</h1>
      <p class="subtitulo">Relógios Casio para o dia a dia.</p>
    </section>

    <h2>Produtos (<?= count($produtos) ?>)</h2>
    <?php require __DIR__ . '/lista-de-produtos.php'; ?>
  </main>
</body>
</html>
