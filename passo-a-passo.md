# Mini Loja (PHP + SQLite): passo a passo até o fim da aula 16

Resumo das aulas **11, 12, 14/15 e 16** de `prog-web-php/aulas/`, que constroem a Mini Loja aos poucos.
O ponto de chegada é a **versão 3 da aula 16** (área do funcionário com login e tranca), ou seja, o estado
do projeto **antes** das melhorias livres pedidas na entrega da aula 16 ("do seu jeito: mude, melhore e envie").

> Situação atual deste repositório: a pasta `Mini-Loja/` está igual à **versão 4 da aula 12** (CRUD completo,
> sem foto e sem login). Faltam as etapas 4 (aulas 14/15) e 5 (aula 16) abaixo.

---

## Estrutura final esperada

```text
mini-loja/
├── index.html            # a porta: página inicial, só HTML
├── cadastro.php          # CONTROLE dos produtos (o "vendedor")
├── banco.php             # MODELO: conexão PDO e todo o SQL (o "estoque")
├── tela.php              # VISÃO dos produtos (o "balcão")
├── funcionario.php       # CONTROLE da área do funcionário (cadastro, login, logout)
├── tela-funcionario.php  # VISÃO da área do funcionário
├── teste.php             # confere versão do PHP e se o pdo_sqlite está ligado
├── mini-loja.sqlite      # o banco: nasce sozinho (NÃO vai para o GitHub)
└── uploads/              # fotos dos produtos: nasce sozinha (NÃO vai para o GitHub)
```

Banco (`mini-loja.sqlite`), criado automaticamente por `conectar()` em `banco.php`:

| Tabela | Colunas |
|---|---|
| `produtos` | `id INTEGER PK AUTOINCREMENT`, `nome TEXT NOT NULL`, `preco REAL NOT NULL`, `imagem TEXT` (adicionada via `ALTER TABLE`) |
| `funcionarios` | `id INTEGER PK AUTOINCREMENT`, `nome TEXT NOT NULL`, `email TEXT NOT NULL UNIQUE`, `senha TEXT NOT NULL` (hash) |

Fluxo MVC de um clique: `cadastro.php` → pede dados ao `banco.php` → recebe o array → `require 'tela.php'` para mostrar.

---

## Etapa 0: ambiente

1. Ligar o Apache no XAMPP (o MySQL **não** é necessário: SQLite é um arquivo).
   Alternativa fora do laboratório: `php -S localhost:8000` dentro da pasta do projeto.
2. Criar a pasta `htdocs/mini-loja` (no XAMPP: `C:\xampp\htdocs\mini-loja`) e abri-la no VS Code.
3. Se o `teste.php` mostrar "SQLite: DESLIGADO": no `php.ini`, tirar o `;` de `extension=pdo_sqlite`
   e `extension=sqlite3`, e reiniciar o Apache.
4. Criar o repositório público `mini-loja` no GitHub (as aulas usam upload pela web, um commit por versão).
5. Por causa do PHP2Shell (out/2026), o PHP do laboratório é antigo: ligar o Apache só durante a aula e dar Stop no fim.

---

## Etapa 1: aula 11, vitrine com array e formulário (sem banco)

Objetivo: entender a divisão em 4 arquivos e o "PHP de memória curta".

| Versão | O que fazer | Arquivos |
|---|---|---|
| 1 | `banco.php` tem `listarProdutos(): array` devolvendo 3 produtos fixos (`nome`, `preco`). `cadastro.php` faz `require 'banco.php'`, `$produtos = listarProdutos()` e `require 'tela.php'`. `tela.php` mostra `count($produtos)` e um `<li>` por produto com `foreach`, `htmlspecialchars` e `number_format($preco, 2, ',', '.')`. | `index.html`, `banco.php`, `cadastro.php`, `tela.php` |
| 2 | `tela.php` ganha `<form method="post" action="cadastro.php">` com `nome` e `preco` (`type="number" step="0.01"`). `cadastro.php` testa `$_SERVER['REQUEST_METHOD'] === 'POST'`, lê com `trim($_POST['nome'] ?? '')` e `(float)`, e mostra "Recebi: ...". | `cadastro.php`, `tela.php` |
| 3 | `cadastro.php` faz `$produtos[] = [...]`: o produto aparece, mas some no próximo pedido. Conclusão: precisa de banco. | `cadastro.php`, `tela.php` |

> Esta etapa é didática: tudo o que ela produz é substituído na etapa 2. Dá para pular direto para a aula 12.

---

## Etapa 2: aula 12, CRUD de produtos com SQLite (PDO)

Começa criando `teste.php` (verifica `PHP_VERSION` contra as versões corrigidas e `extension_loaded('pdo_sqlite')`).

| Versão | CRUD | O que muda |
|---|---|---|
| 1 | **R** (SELECT) | `banco.php` ganha `conectar(): PDO` com `new PDO('sqlite:' . __DIR__ . '/mini-loja.sqlite')`, `ERRMODE_EXCEPTION`, `CREATE TABLE IF NOT EXISTS produtos (...)` e, se `COUNT(*) == 0`, insere 3 produtos de exemplo (Placa ESP32 39.90, Arduino Uno 59.90, Sensor DHT11 12.50). `listarProdutos()` faz `SELECT id, nome, preco FROM produtos ORDER BY nome`. `cadastro.php` e `tela.php` iguais à v1 da aula 11. |
| 2 | **C** (INSERT) | `banco.php`: `inserirProduto($nome, $preco)` com `prepare` + `execute` (marcadores `:nome`, `:preco`). `cadastro.php`: no POST grava e faz `header('Location: cadastro.php'); exit;` (padrão PRG, F5 não duplica). `tela.php`: formulário. |
| 3 | **D** (DELETE) | `banco.php`: `excluirProduto(int $id)` com `WHERE id = :id`. `tela.php`: cada `<li>` ganha um mini-form com `<button name="excluir" value="ID">`. `cadastro.php`: `if (isset($_POST['excluir']))` antes do cadastro, com `(int)`. |
| 4 | **U** (UPDATE) | `banco.php`: `buscarProduto(int $id): ?array` e `atualizarProduto($id, $nome, $preco)`. `tela.php`: link `cadastro.php?editar=ID`, `<input type="hidden" name="id">`, campos com `value` preenchido, título/botão mudam para "Editar produto"/"Salvar alterações" + link Cancelar. `cadastro.php`: `isset($_GET['editar'])` busca o produto; no POST, `$id > 0` decide entre atualizar e inserir. |

Fechamento: "faxina" (remover o projeto antigo de clientes) e **nunca** enviar o `mini-loja.sqlite` ao GitHub.

---

## Etapa 3: aulas 14 e 15, foto do produto (upload seguro)

Pré-requisito: a versão 4 da aula 12.

### Versão 1: a foto entra (de propósito, inseguro)
- `banco.php`: depois do `CREATE TABLE`, lê `PRAGMA table_info(produtos)` e, se não houver a coluna `imagem`,
  roda `ALTER TABLE produtos ADD COLUMN imagem TEXT`. `inserirProduto()` passa a receber `$imagem`;
  `listarProdutos()` e `buscarProduto()` passam a trazer `imagem`.
- `cadastro.php`: se `$_FILES['imagem']['error'] === UPLOAD_ERR_OK`, cria `uploads/` com `mkdir` e usa
  `move_uploaded_file` com o nome original.
- `tela.php`: `<form ... enctype="multipart/form-data">`, `<input type="file" name="imagem" accept="image/*">`,
  e na lista `<img src="uploads/...">` ou "📦 sem foto".
- **Teste do ataque** (só local): enviar um `foto-teste.php` como "foto" e abrir `uploads/foto-teste.php`:
  o servidor executa. Depois apagar o arquivo e o produto.

### Versão 2: o vendedor confere (`cadastro.php` e `tela.php`; `banco.php` igual)
- `conferirImagem(array $arquivo): string` devolve `''` ou a mensagem de erro, nesta ordem:
  tamanho (`UPLOAD_ERR_INI_SIZE` ou `> 2 * 1024 * 1024`), `error !== UPLOAD_ERR_OK`, `size === 0`,
  `getimagesize()` com tipo em `IMAGETYPE_JPEG | PNG | WEBP`.
- `guardarImagem(array $arquivo): string` gera o nome `bin2hex(random_bytes(8)) . '.' . extensão`, com a
  extensão tirada do **tipo real** (nunca do nome enviado), e move para `uploads/`.
- Em caso de erro: não grava, não redireciona, e devolve para a tela `$erro` e o que foi digitado
  (`$produto = ['id' => ..., 'nome' => ..., 'preco' => ...]`).
- `tela.php`: mostra "Foto recusada: ..." em vermelho; `accept="image/jpeg, image/png, image/webp"`; aviso "JPG, PNG ou WEBP, até 2 MB".

### Versão 3: trocar e apagar a foto
- `banco.php`: `atualizarProduto($id, $nome, $preco, $imagem)` atualiza também `imagem`.
- `cadastro.php`: `apagarImagem(string $nome)` faz `unlink` de `uploads/` + `basename($nome)`.
  No Excluir: busca o produto, apaga a foto e só depois o registro. No Editar: sem foto nova, mantém a antiga;
  com foto nova, apaga a antiga da pasta.
- `tela.php`: ao editar, mostra "Foto atual" e o rótulo vira "Trocar a foto (só se quiser)".

Fechamento: `uploads/` e `mini-loja.sqlite` **não** vão para o GitHub; apagar qualquer `.php` que tenha sobrado em `uploads/`.

---

## Etapa 4: aula 16, área do funcionário (cadastro, login, tranca)

Pré-requisito: a versão 3 da aula 14.

### Versão 1: o crachá (cadastro de funcionário)
- `banco.php`: `CREATE TABLE IF NOT EXISTS funcionarios (id, nome, email UNIQUE, senha)` dentro de `conectar()`;
  novas funções `inserirFuncionario($nome, $email, $hash)` e `buscarFuncionario($email): ?array`.
- `index.html`: novo link "Área do funcionário" (`funcionario.php`) além de "Ver os produtos" e "Testar o ambiente".
- **Novo** `funcionario.php` (controle): valida nome não vazio, `filter_var($email, FILTER_VALIDATE_EMAIL)`,
  senha com 8 ou mais caracteres e e-mail não repetido; grava com `password_hash($senha, PASSWORD_DEFAULT)`.
  E-mail normalizado com `strtolower(trim(...))`.
- **Novo** `tela-funcionario.php` (visão): formulário com `type="password"`, mensagens `$erro`/`$aviso`.

### Versão 2: a porta (login e logout)
- `funcionario.php`: `session_start()` na primeira linha; campo escondido `acao` = `entrar` ou `cadastrar`.
  Entrar: `buscarFuncionario` + `password_verify`; se certo, `session_regenerate_id(true)`,
  `$_SESSION['funcionario'] = nome` e redireciona para `cadastro.php`. Se errado: "E-mail ou senha errados."
  (sem dizer qual). `?sair=1`: `$_SESSION = []`, `session_destroy()`, redireciona.
- `tela-funcionario.php`: logado mostra "Olá, NOME" + links Cadastrar produtos / Sair; senão, formulário Entrar.
- **Pausa didática**: deslogado, ainda dá para cadastrar produto em `cadastro.php`. A v3 resolve.

### Versão 3: a tranca (ponto de chegada)
- `banco.php`: `contarFuncionarios(): int`.
- `cadastro.php`: `session_start()` no topo; `$logado = $_SESSION['funcionario'] ?? ''`; se `$logado === ''`
  e (POST **ou** `?editar`), `header('Location: funcionario.php'); exit;`. A tranca fica no **controle**.
- `tela.php`: saudação/link de login no topo; formulário, "Editar" e "Excluir" só aparecem se `$logado`.
- `funcionario.php`: `$podeCadastrar = logado || contarFuncionarios() === 0` (o primeiro cadastro é o do
  administrador; depois, só quem está logado cadastra colegas). Recalculado após o POST.
- `tela-funcionario.php`: formulário de cadastro só aparece se `$podeCadastrar`; título
  "Primeiro acesso: cadastre o administrador" ou "Cadastrar funcionário".

### Checklist de verificação final
- [ ] `teste.php` mostra SQLite ligado.
- [ ] Deslogado: `cadastro.php` mostra só a lista (sem formulário, Editar ou Excluir); POST ou `?editar` redirecionam para `funcionario.php`.
- [ ] Banco sem funcionários: `funcionario.php` permite cadastrar o administrador; depois disso, o cadastro some para visitantes.
- [ ] E-mail repetido e senha curta são recusados; senha errada não entra; senha certa mostra "Olá".
- [ ] Logado: cadastrar produto com foto, editar trocando a foto (a antiga sai de `uploads/`), excluir (a foto sai junto).
- [ ] Um `.php` disfarçado de foto é recusado; fotos entram com nome aleatório de 16 hex.
- [ ] GitHub: só os `.php` e o `index.html`; sem `mini-loja.sqlite` e sem `uploads/`.

---

## Testes automáticos (Pytest)

Os testes ficam em `tests/` e são escritos em Python. Eles chamam as funções PHP de verdade
(o Python roda o `php` na linha de comando), sempre numa **cópia do app numa pasta temporária**,
com banco próprio: o `mini-loja.sqlite` do projeto nunca é tocado.

Pré-requisitos: Python 3 e o `php` no terminal (`php -v` precisa funcionar).
O `pdo_sqlite` não precisa estar ligado no `php.ini`: se estiver desligado, os testes ligam só para eles.

1. Criar o ambiente virtual (uma vez só): `python -m venv .venv`
2. Ativar o ambiente: `source .venv/bin/activate` (no Windows: `.venv\Scripts\activate`)
3. Instalar as dependências: `pip install -r requirements.txt`
4. Rodar os testes: `pytest`

---

## Apêndice: código final de cada arquivo (aula 16, versão 3)

Copiado das abas de código das aulas (`teste.php` vem da aula 12 e não muda depois).

### `index.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Mini Loja</title>
</head>
<body>
  <!-- index.html: a página inicial. É só HTML: o PHP entra quando você clica nos produtos -->
  <h1>Mini Loja</h1>
  <p>Componentes eletrônicos para os seus projetos, com PHP e SQLite.</p>

  <ul>
    <li><a href="cadastro.php">Ver os produtos</a></li>
    <li><a href="funcionario.php">Área do funcionário</a></li>
    <li><a href="teste.php">Testar o ambiente</a></li>
  </ul>
</body>
</html>
```

### `banco.php`

```php
<?php
// banco.php: o MODELO.
// Conecta no banco e guarda as funções que falam com ele. Todo o SQL mora aqui.

function conectar(): PDO
{
    // o banco é um arquivo só; se ele não existe, o PHP cria
    $pdo = new PDO('sqlite:' . __DIR__ . '/mini-loja.sqlite');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // a tabela nasce sozinha na primeira vez
    $pdo->exec('CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )');

    // a coluna da foto (aula 14). A tabela já existia? O ALTER TABLE acrescenta a coluna, uma vez só
    $colunas = $pdo->query('PRAGMA table_info(produtos)')->fetchAll(PDO::FETCH_COLUMN, 1);
    if (!in_array('imagem', $colunas)) {
        $pdo->exec('ALTER TABLE produtos ADD COLUMN imagem TEXT');
    }

    // a tabela dos funcionários. A senha nunca entra pura: entra o "hash" dela
    $pdo->exec('CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )');

    // banco vazio? entram três produtos de exemplo, para a lista não começar em branco
    $total = $pdo->query('SELECT COUNT(*) FROM produtos')->fetchColumn();
    if ($total == 0) {
        $pdo->exec("INSERT INTO produtos (nome, preco) VALUES
            ('Placa ESP32', 39.90),
            ('Arduino Uno', 59.90),
            ('Sensor de temperatura DHT11', 12.50)");
    }

    return $pdo;
}

// R: devolve todos os produtos, em ordem alfabética (agora com a foto)
function listarProdutos(): array
{
    $pdo = conectar();
    return $pdo->query('SELECT id, nome, preco, imagem FROM produtos ORDER BY nome')->fetchAll(PDO::FETCH_ASSOC);
}

// C: grava um produto novo; a imagem é só o NOME do arquivo (a foto fica na pasta uploads)
function inserirProduto(string $nome, float $preco, string $imagem): void
{
    $pdo = conectar();
    $stmt = $pdo->prepare('INSERT INTO produtos (nome, preco, imagem) VALUES (:nome, :preco, :imagem)');
    $stmt->execute([':nome' => $nome, ':preco' => $preco, ':imagem' => $imagem]);
}

// D: apaga o produto pelo id (o número que o banco deu a ele)
function excluirProduto(int $id): void
{
    $pdo = conectar();
    $stmt = $pdo->prepare('DELETE FROM produtos WHERE id = :id');
    $stmt->execute([':id' => $id]);
}

// busca um produto só, para preencher o formulário de edição
function buscarProduto(int $id): ?array
{
    $pdo = conectar();
    $stmt = $pdo->prepare('SELECT id, nome, preco, imagem FROM produtos WHERE id = :id');
    $stmt->execute([':id' => $id]);
    return $stmt->fetch(PDO::FETCH_ASSOC) ?: null;
}

// U: troca o nome, o preço e a foto do produto
function atualizarProduto(int $id, string $nome, float $preco, string $imagem): void
{
    $pdo = conectar();
    $stmt = $pdo->prepare('UPDATE produtos SET nome = :nome, preco = :preco, imagem = :imagem WHERE id = :id');
    $stmt->execute([':nome' => $nome, ':preco' => $preco, ':imagem' => $imagem, ':id' => $id]);
}

// grava um funcionário; a senha já chega embaralhada (o hash)
function inserirFuncionario(string $nome, string $email, string $hash): void
{
    $pdo = conectar();
    $stmt = $pdo->prepare('INSERT INTO funcionarios (nome, email, senha) VALUES (:nome, :email, :senha)');
    $stmt->execute([':nome' => $nome, ':email' => $email, ':senha' => $hash]);
}

// procura o funcionário pelo e-mail (devolve null se não tem)
function buscarFuncionario(string $email): ?array
{
    $pdo = conectar();
    $stmt = $pdo->prepare('SELECT id, nome, email, senha FROM funcionarios WHERE email = :email');
    $stmt->execute([':email' => $email]);
    return $stmt->fetch(PDO::FETCH_ASSOC) ?: null;
}

// NOVO: quantos funcionários a loja tem (zero = o primeiro cadastro é livre)
function contarFuncionarios(): int
{
    $pdo = conectar();
    return (int) $pdo->query('SELECT COUNT(*) FROM funcionarios')->fetchColumn();
}
```

### `cadastro.php`

```php
<?php
// cadastro.php: o CONTROLE.
// Recebe o formulário, pede ao modelo (banco.php) e chama a visão (tela.php).
// NOVO: a sessão conta quem está logado
session_start();
require __DIR__ . '/banco.php';

// NOVO: a tranca. Visitante só olha; mexer (cadastrar, editar, excluir) é com funcionário logado
$logado = $_SESSION['funcionario'] ?? '';
if ($logado === '' && ($_SERVER['REQUEST_METHOD'] === 'POST' || isset($_GET['editar']))) {
    header('Location: funcionario.php');
    exit;
}

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
```

### `tela.php`

```php
<?php // tela.php: a VISÃO. Só o HTML; as variáveis vêm do cadastro.php ?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Mini Loja</title>
</head>
<body>
  <p><a href="index.html">← Página inicial</a></p>
  <h1>Mini Loja</h1>

  <!-- NOVO: quem está logado vê o próprio nome; o visitante vê o caminho para entrar -->
  <?php if ($logado): ?>
    <p>Olá, <strong><?= htmlspecialchars($logado) ?></strong>! · <a href="funcionario.php">Área do funcionário</a> · <a href="funcionario.php?sair=1">Sair</a></p>
  <?php else: ?>
    <p>É funcionário? <a href="funcionario.php">Entre</a> para cadastrar produtos.</p>
  <?php endif; ?>

  <!-- NOVO: o formulário só aparece para o funcionário logado -->
  <?php if ($logado): ?>

  <h2><?= !empty($produto['id']) ? 'Editar produto' : 'Novo produto' ?></h2>

  <?php if ($erro): ?>
    <p style="color: firebrick"><strong>Foto recusada:</strong> <?= htmlspecialchars($erro) ?></p>
  <?php endif; ?>
  <!-- sem o enctype, o arquivo não viaja (chega só o nome dele) -->
  <form method="post" action="cadastro.php" enctype="multipart/form-data">
    <!-- o id escondido diz ao controle qual produto editar (vazio = produto novo) -->
    <input type="hidden" name="id" value="<?= $produto['id'] ?? '' ?>">

    <label for="nome">Nome</label>
    <input id="nome" name="nome" required value="<?= htmlspecialchars($produto['nome'] ?? '') ?>">

    <label for="preco">Preço (R$)</label>
    <input id="preco" name="preco" type="number" step="0.01" min="0" required value="<?= $produto['preco'] ?? '' ?>">

    <?php if (!empty($produto['imagem'])): ?>
      <p>Foto atual: <img src="uploads/<?= htmlspecialchars($produto['imagem']) ?>" alt="" width="60"></p>
    <?php endif; ?>

    <label for="imagem"><?= !empty($produto['id']) ? 'Trocar a foto (só se quiser)' : 'Foto do produto' ?></label>
    <input id="imagem" name="imagem" type="file" accept="image/jpeg, image/png, image/webp">
    <small>JPG, PNG ou WEBP, até 2 MB.</small>

    <button type="submit"><?= !empty($produto['id']) ? 'Salvar alterações' : 'Cadastrar' ?></button>
    <?php if (!empty($produto['id'])): ?>
      <a href="cadastro.php">Cancelar</a>
    <?php endif; ?>
  </form>
  <?php endif; ?>

  <h2>Produtos (<?= count($produtos) ?>)</h2>
  <ul>
    <?php foreach ($produtos as $item): ?>
      <li>
        <?php if ($item['imagem']): ?>
          <img src="uploads/<?= htmlspecialchars($item['imagem']) ?>" alt="" width="60">
        <?php else: ?>
          <span>📦 sem foto</span>
        <?php endif; ?>
        <?= htmlspecialchars($item['nome']) ?> · R$ <?= number_format($item['preco'], 2, ',', '.') ?>
        <?php if ($logado): ?>
          <a href="cadastro.php?editar=<?= $item['id'] ?>">Editar</a>
          <form method="post" action="cadastro.php" style="display: inline">
            <button name="excluir" value="<?= $item['id'] ?>">Excluir</button>
          </form>
        <?php endif; ?>
      </li>
    <?php endforeach; ?>
  </ul>
</body>
</html>
```

### `funcionario.php`

```php
<?php
// funcionario.php: o CONTROLE da área do funcionário.
// a sessão é a "memória" do servidor sobre você; tem que vir antes de qualquer HTML
session_start();
require __DIR__ . '/banco.php';

// clicou em "Sair"? esquece quem estava logado e volta
if (isset($_GET['sair'])) {
    $_SESSION = [];
    session_destroy();
    header('Location: funcionario.php');
    exit;
}

$erro = '';
$aviso = '';

// NOVO: funcionário novo só entra pelas mãos de quem já está logado
// (a loja sem ninguém? o primeiro cadastro é livre: é o do administrador)
$podeCadastrar = isset($_SESSION['funcionario']) || contarFuncionarios() === 0;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // o campo escondido "acao" diz qual formulário foi enviado
    $acao = $_POST['acao'] ?? '';
    $nome = trim($_POST['nome'] ?? '');
    $email = strtolower(trim($_POST['email'] ?? ''));
    $senha = $_POST['senha'] ?? '';

    if ($acao === 'entrar') {
        // password_verify compara a senha digitada com o hash guardado
        $funcionario = buscarFuncionario($email);
        if ($funcionario && password_verify($senha, $funcionario['senha'])) {
            session_regenerate_id(true);  // crachá novo a cada entrada
            $_SESSION['funcionario'] = $funcionario['nome'];
            header('Location: cadastro.php');
            exit;
        }
        // não conta qual dos dois errou: assim ninguém descobre e-mails cadastrados
        $erro = 'E-mail ou senha errados.';
    }

    if ($acao === 'cadastrar') {
        if (!$podeCadastrar) {
            $erro = 'Só um funcionário logado cadastra outro.';
        } elseif ($nome === '') {
            $erro = 'Escreva o seu nome.';
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $erro = 'Esse e-mail não parece um e-mail.';
        } elseif (strlen($senha) < 8) {
            $erro = 'A senha precisa de 8 caracteres ou mais.';
        } elseif (buscarFuncionario($email)) {
            $erro = 'Esse e-mail já tem cadastro.';
        } else {
            inserirFuncionario($nome, $email, password_hash($senha, PASSWORD_DEFAULT));
            $aviso = 'Cadastro feito, ' . $nome . '! Agora é só entrar.';
        }
    }
}

// quem está logado (vazio = ninguém)
$logado = $_SESSION['funcionario'] ?? '';

// NOVO: depois de um cadastro, a conta muda (a loja já não está vazia)
$podeCadastrar = $logado !== '' || contarFuncionarios() === 0;

require __DIR__ . '/tela-funcionario.php';
```

### `tela-funcionario.php`

```php
<?php // tela-funcionario.php: a VISÃO da área do funcionário. Só o HTML ?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Mini Loja · Funcionário</title>
</head>
<body>
  <p><a href="index.html">← Página inicial</a></p>
  <h1>Área do funcionário</h1>

  <?php if ($erro): ?>
    <p style="color: firebrick"><strong>Não deu:</strong> <?= htmlspecialchars($erro) ?></p>
  <?php endif; ?>
  <?php if ($aviso): ?>
    <p style="color: green"><?= htmlspecialchars($aviso) ?></p>
  <?php endif; ?>

  <!-- já entrou? mostra quem é e o botão de sair -->
  <?php if ($logado): ?>
    <p>Olá, <strong><?= htmlspecialchars($logado) ?></strong>! <a href="cadastro.php">Cadastrar produtos</a> · <a href="funcionario.php?sair=1">Sair</a></p>
  <?php else: ?>
    <h2>Entrar</h2>
    <form method="post" action="funcionario.php">
      <input type="hidden" name="acao" value="entrar">

      <label for="email-entrar">E-mail</label>
      <input id="email-entrar" name="email" type="email" required>

      <label for="senha-entrar">Senha</label>
      <input id="senha-entrar" name="senha" type="password" required>

      <button type="submit">Entrar</button>
    </form>
  <?php endif; ?>

  <!-- NOVO: o formulário de cadastro só aparece para quem pode usar -->
  <?php if ($podeCadastrar): ?>
  <h2><?= $logado ? 'Cadastrar funcionário' : 'Primeiro acesso: cadastre o administrador' ?></h2>
  <form method="post" action="funcionario.php">
    <input type="hidden" name="acao" value="cadastrar">

    <label for="nome">Nome</label>
    <input id="nome" name="nome" required>

    <label for="email">E-mail</label>
    <input id="email" name="email" type="email" required>

    <label for="senha">Senha (8 caracteres ou mais)</label>
    <input id="senha" name="senha" type="password" minlength="8" required>

    <button type="submit">Cadastrar</button>
  </form>
  <?php endif; ?>
</body>
</html>
```

### `teste.php`

```php
<?php
// teste.php: confere o ambiente antes de começar.
// 1. a versão do PHP já tem a correção do PHP2Shell?
// 2. o SQLite está ligado?

// as primeiras versões corrigidas de cada série (21/10/2026)
$corrigidas = ['8.5' => '8.5.12', '8.4' => '8.4.27', '8.3' => '8.3.36', '8.2' => '8.2.35'];
$serie = PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION;
$minima = $corrigidas[$serie] ?? null;
$phpOk = $minima !== null && version_compare(PHP_VERSION, $minima, '>=');

$sqliteOk = extension_loaded('pdo_sqlite');
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Teste do ambiente</title>
</head>
<body>
  <h1>Teste do ambiente</h1>

  <p>PHP <?= PHP_VERSION ?>:
    <?= $phpOk ? 'atualizado, com a correção do PHP2Shell.' : 'versão antiga, sem a correção de outubro de 2026. Dá para estudar: só clique em Stop no Apache no fim da aula.' ?></p>

  <p>SQLite:
    <?= $sqliteOk ? 'ligado. Pode começar!' : 'DESLIGADO. Ligue o pdo_sqlite no php.ini (veja o passo a passo da aula).' ?></p>
</body>
</html>
```
