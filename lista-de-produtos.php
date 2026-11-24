<?php
// lista-de-produtos.php: a grade de cartões dos produtos, usada pela página inicial e pela vitrine.
// Precisa de $produtos; com $logado preenchido, cada cartão ganha "Editar" e "Excluir".
?>
<!-- cada produto é um cartão: a grade arruma em colunas no computador e numa só no celular -->
<ul class="vitrine">
  <?php foreach ($produtos as $item): ?>
    <li class="cartao">
      <div class="cartao-foto">
        <?php if ($item['imagem']): ?>
          <img src="uploads/<?= htmlspecialchars($item['imagem']) ?>" alt="">
        <?php else: ?>
          <span>📦 sem foto</span>
        <?php endif; ?>
      </div>
      <p class="cartao-info"><?= htmlspecialchars($item['nome']) ?> · R$ <?= number_format($item['preco'], 2, ',', '.') ?></p>
      <?php if ($logado): ?>
        <div class="cartao-acoes">
          <a class="botao botao-leve botao-pequeno" href="cadastro.php?editar=<?= $item['id'] ?>">Editar</a>
          <form method="post" action="cadastro.php">
            <button class="botao-perigo botao-pequeno" name="excluir" value="<?= $item['id'] ?>">Excluir</button>
          </form>
        </div>
      <?php endif; ?>
    </li>
  <?php endforeach; ?>
</ul>
