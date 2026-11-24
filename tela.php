<?php // tela.php: a VISÃO. Só o HTML; as variáveis vêm do cadastro.php ?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mini Loja</title>
  <link rel="stylesheet" href="estilo.css">
</head>
<body>
  <?php require __DIR__ . '/topo.php'; ?>

  <main class="conteudo">
  <h1>Mini Loja</h1>

  <!-- NOVO: quem está logado vê o próprio nome; o visitante vê o caminho para entrar -->
  <?php if ($logado): ?>
    <p class="barra">Olá, <strong><?= htmlspecialchars($logado) ?></strong>! · <a href="funcionario.php">Área do funcionário</a> · <a href="funcionario.php#cadastrar-funcionario">Cadastrar funcionário</a> · <a href="funcionario.php?sair=1">Sair</a></p>
  <?php else: ?>
    <p class="barra">É funcionário? <a href="funcionario.php">Entre</a> para cadastrar produtos.</p>
  <?php endif; ?>

  <!-- NOVO: o formulário só aparece para o funcionário logado -->
  <?php if ($logado): ?>

  <h2><?= !empty($produto['id']) ? 'Editar produto' : 'Novo produto' ?></h2>

  <?php if ($erro): ?>
    <p class="alerta alerta-erro"><strong>Foto recusada:</strong> <?= htmlspecialchars($erro) ?></p>
  <?php endif; ?>
  <!-- sem o enctype, o arquivo não viaja (chega só o nome dele) -->
  <form class="formulario formulario-produto" method="post" action="cadastro.php" enctype="multipart/form-data">
    <!-- o id escondido diz ao controle qual produto editar (vazio = produto novo) -->
    <input type="hidden" name="id" value="<?= $produto['id'] ?? '' ?>">

    <label for="nome">Nome</label>
    <input id="nome" name="nome" required value="<?= htmlspecialchars($produto['nome'] ?? '') ?>">

    <label for="preco">Preço (R$)</label>
    <input id="preco" name="preco" type="number" step="0.01" min="0" required value="<?= $produto['preco'] ?? '' ?>">

    <?php if (!empty($produto['imagem'])): ?>
      <p class="foto-atual">Foto atual: <img src="uploads/<?= htmlspecialchars($produto['imagem']) ?>" alt=""></p>
    <?php endif; ?>

    <label for="imagem"><?= !empty($produto['id']) ? 'Trocar a foto (só se quiser)' : 'Foto do produto' ?></label>
    <input id="imagem" name="imagem" type="file" accept="image/jpeg, image/png, image/webp">
    <small>JPG, PNG ou WEBP, até 2 MB.</small>

    <div class="acoes">
      <button type="submit"><?= !empty($produto['id']) ? 'Salvar alterações' : 'Cadastrar' ?></button>
      <?php if (!empty($produto['id'])): ?>
        <a href="cadastro.php">Cancelar</a>
      <?php endif; ?>
    </div>
  </form>
  <?php endif; ?>

  <h2>Produtos (<?= count($produtos) ?>)</h2>
  <?php require __DIR__ . '/lista-de-produtos.php'; ?>
  </main>
</body>
</html>
