<?php // tela-funcionario.php: a VISÃO da área do funcionário. Só o HTML ?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mini Loja · Funcionário</title>
  <link rel="stylesheet" href="estilo.css">
</head>
<body>
  <?php require __DIR__ . '/topo.php'; ?>

  <main class="conteudo">
  <h1>Área do funcionário</h1>

  <?php if ($erro): ?>
    <p class="alerta alerta-erro formulario-estreito"><strong>Não deu:</strong> <?= htmlspecialchars($erro) ?></p>
  <?php endif; ?>
  <?php if ($aviso): ?>
    <p class="alerta alerta-sucesso formulario-estreito"><?= htmlspecialchars($aviso) ?></p>
  <?php endif; ?>

  <!-- já entrou? mostra quem é e o botão de sair -->
  <?php if ($logado): ?>
    <p class="barra">Olá, <strong><?= htmlspecialchars($logado) ?></strong>! <a href="cadastro.php">Cadastrar produtos</a> · <a href="funcionario.php?sair=1">Sair</a></p>
  <?php else: ?>
    <h2>Entrar</h2>
    <form class="formulario formulario-estreito" method="post" action="funcionario.php">
      <input type="hidden" name="acao" value="entrar">

      <label for="email-entrar">E-mail</label>
      <input id="email-entrar" name="email" type="email" autocomplete="username" required>

      <label for="senha-entrar">Senha</label>
      <input id="senha-entrar" name="senha" type="password" autocomplete="current-password" required>

      <div class="acoes">
        <button type="submit">Entrar</button>
      </div>
    </form>
  <?php endif; ?>

  <!-- a loja já tem funcionário e ninguém entrou: explica quem cadastra os colegas -->
  <?php if (!$podeCadastrar): ?>
    <p class="barra formulario-estreito">Precisa de um funcionário novo? Quem cadastra é um funcionário logado: entre com a sua conta, ou peça a alguém da equipe.</p>
  <?php endif; ?>

  <!-- NOVO: o formulário de cadastro só aparece para quem pode usar -->
  <?php if ($podeCadastrar): ?>
  <h2 id="cadastrar-funcionario"><?= $logado ? 'Cadastrar funcionário' : 'Primeiro acesso: cadastre o administrador' ?></h2>
  <form class="formulario formulario-estreito" method="post" action="funcionario.php">
    <input type="hidden" name="acao" value="cadastrar">

    <label for="nome">Nome</label>
    <input id="nome" name="nome" autocomplete="name" required>

    <label for="email">E-mail</label>
    <input id="email" name="email" type="email" autocomplete="email" required>

    <label for="senha">Senha (8 caracteres ou mais)</label>
    <input id="senha" name="senha" type="password" minlength="8" autocomplete="new-password" required>

    <div class="acoes">
      <button type="submit">Cadastrar</button>
    </div>
  </form>
  <?php endif; ?>
  </main>
</body>
</html>
