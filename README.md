# Mini Loja

Uma lojinha de componentes eletrônicos feita com **PHP** e **SQLite**, no padrão MVC.

- O **visitante** vê a vitrine com os produtos, o preço e a foto.
- O **funcionário** entra com e-mail e senha e cadastra, edita e exclui produtos, inclusive com foto.

Os testes automáticos ficam em `tests/` e usam **pytest** (testes unitários) e **Selenium** (testes funcionais, que abrem um navegador de verdade).

### Como o projeto está organizado

| Arquivo | Papel |
|---|---|
| `index.php` | Página inicial: a vitrine com os produtos em grade |
| `topo.php` | O cabeçalho de todas as páginas, com o menu no canto direito |
| `lista-de-produtos.php` | A grade de cartões dos produtos (usada pela página inicial e pela tela de produtos) |
| `cadastro.php` | CONTROLE dos produtos: recebe o formulário, pede ao modelo e chama a tela |
| `banco.php` | MODELO: a conexão com o SQLite e todo o SQL |
| `foto.php` | A regra que aceita ou recusa a foto enviada |
| `tela.php` | VISÃO da vitrine e do formulário de produto |
| `funcionario.php` | CONTROLE da área do funcionário (cadastro, entrada e saída) |
| `tela-funcionario.php` | VISÃO da área do funcionário |
| `teste.php` | Confere o ambiente (versão do PHP e SQLite) |
| `tests/` | Os testes (pytest e Selenium) |
| `passo-a-passo.md` | O resumo das aulas que constroem a loja |

---

## 1. Abrir a loja no navegador

O PHP já traz um **servidor embutido**. Ele basta para rodar a loja: **não precisa de Apache, XAMPP nem MySQL** (o SQLite é um arquivo só).

### O que precisa estar instalado

- **PHP 8.2 ou mais novo**, com a extensão **`pdo_sqlite`** ligada.

Para conferir, rode no terminal:

```bash
php -v                    # mostra a versão
php -m | grep pdo_sqlite  # tem que aparecer "pdo_sqlite"
```

> No Windows, troque o `grep` por `findstr`: `php -m | findstr pdo_sqlite`.

### Se o `pdo_sqlite` estiver desligado

Você tem duas saídas:

- **Para sempre:** descubra qual php.ini o PHP usa com `php --ini` (linha `Loaded Configuration File`). Abra esse arquivo e tire o `;` do começo da linha:

  ```ini
  ;extension=pdo_sqlite
  ```

  Ela vira `extension=pdo_sqlite`. Salve o arquivo e rode `php -m` de novo.
- **Só desta vez, sem mexer no php.ini:** acrescente `-d extension=pdo_sqlite` ao comando do servidor (veja abaixo).

Se nem assim aparecer, a extensão não está instalada. No Linux ela costuma vir num pacote à parte (por exemplo `php-sqlite3` no Debian/Ubuntu ou `php-sqlite` no Arch).

### Subir o servidor

Na pasta do projeto, rode:

```bash
php -S localhost:8000
```

Se precisar ligar o `pdo_sqlite` só desta vez, use `php -d extension=pdo_sqlite -S localhost:8000`.

Agora abra **http://localhost:8000** no navegador. Para desligar o servidor, aperte `Ctrl+C` no terminal.

> A porta 8000 está ocupada? Troque por outra, por exemplo `php -S localhost:8080`, e abra http://localhost:8080.

### Conferir o ambiente

Abra http://localhost:8000/teste.php (ela não aparece no menu do site, de propósito). Essa página diz duas coisas:

- se a sua versão do PHP já tem a correção de segurança de outubro de 2026;
- se o SQLite está **ligado**.

Se aparecer "SQLite: DESLIGADO", volte ao passo anterior. O aviso de "versão antiga" do PHP não impede a loja de rodar: serve para estudo, mas vale atualizar o PHP.

> A página foi escrita para as aulas, que usam o XAMPP, por isso fala em "Apache" e em "passo a passo da aula". Com o servidor embutido vale o mesmo: o que importa é o SQLite aparecer ligado.

### O que nasce sozinho

Não é preciso criar banco nem pasta nenhuma.

- **Banco:** na primeira visita à loja, o PHP cria o arquivo `mini-loja.sqlite` com as tabelas e três produtos de exemplo.
- **Fotos:** a pasta `uploads/` nasce quando a primeira foto é enviada.

Os dois ficam de fora do Git (estão no `.gitignore`). Para começar com a loja zerada, desligue o servidor e apague o `mini-loja.sqlite` e a pasta `uploads/`.

### Entrar na área do funcionário

1. No menu do topo, clique em **Área do funcionário**.
2. **Com a loja vazia, o primeiro cadastro é livre:** ele é o do administrador. Em **Primeiro acesso: cadastre o administrador**, preencha nome, e-mail e uma senha de **8 caracteres ou mais** e clique em **Cadastrar**.
3. Na mesma página, em **Entrar**, use o e-mail e a senha que você acabou de cadastrar.
4. Pronto: você cai direto na vitrine, agora com o formulário de produto novo e os botões **Editar** e **Excluir** em cada produto. A foto é opcional e aceita JPG, PNG ou WEBP de até 2 MB.

Depois do primeiro, só um funcionário **logado** cadastra outro: com a conta aberta, clique em **Cadastrar funcionário** na barra do topo da vitrine. Quem não entrou vê só o formulário de entrar e um aviso explicando isso.

---

## 2. Rodar os testes

Os testes são escritos em **Python**. Você vai precisar de:

| Para rodar | Precisa de |
|---|---|
| Testes unitários (pytest) | PHP com `pdo_sqlite` + **Python 3.10 ou mais novo** |
| Testes funcionais (Selenium) | Tudo acima + **Chromium** (ou Google Chrome) + **chromedriver** |

### Preparar o ambiente Python (uma vez só)

Na pasta do projeto, crie um ambiente virtual e instale as dependências do `requirements.txt` (pytest e Selenium):

```bash
python -m venv .venv
source .venv/bin/activate         # Linux/macOS
# .venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Se o comando `python` não existir, use `python3` (comum no Debian/Ubuntu e no macOS).

O `source .venv/bin/activate` vale só para aquele terminal. Num terminal novo, rode-o de novo antes dos testes.

### Testes unitários (pytest)

Eles conferem o modelo (`banco.php`: produtos e funcionários) e a regra da foto (`foto.php`) chamando o PHP direto, sem navegador e sem servidor:

```bash
pytest -m "not funcional"
```

Para rodar só um arquivo, ou só um teste:

```bash
pytest tests/test_produtos.py
pytest tests/test_foto.py::test_png_pequeno_e_valido_e_aceito
pytest -k "foto"   # todos os testes com "foto" no nome
```

Acrescente `-v` para ver o nome de cada teste, ou `-x` para parar no primeiro que falhar.

### Testes funcionais (Selenium)

Eles abrem um Chrome de verdade e usam a loja como uma pessoa faria: cadastram um funcionário, entram e saem, cadastram, editam e excluem produtos, enviam e trocam fotos. Também conferem a tranca: o visitante só olha a vitrine e não consegue mexer em nada.

**Instale primeiro o Chromium (ou o Chrome) e o chromedriver.** As versões dos dois **precisam ser iguais**: o chromedriver 131 só conversa com o Chrome 131.

- **Linux:** pelo gerenciador de pacotes. No Arch, `chromium` já traz o chromedriver. No Debian/Ubuntu, instale `chromium` e `chromium-driver`.
- **Windows/macOS:** com o Google Chrome instalado, o Selenium baixa sozinho o chromedriver certo na primeira vez (precisa de internet).

Para conferir: `chromedriver --version` e `chromium --version` (ou `google-chrome --version`).

Rode só os funcionais:

```bash
pytest -m funcional
```

Um arquivo só também funciona: `pytest -m funcional tests/test_foto_no_navegador.py`.

#### Ver o navegador trabalhando: `--com-janela`

**Por padrão, nenhuma janela abre.** O Chrome roda escondido (o modo *headless*): os testes passam, mas você não vê nada na tela. Isso é de propósito, porque assim os testes rodam mais rápido e não atrapalham o que você está fazendo.

Para **ver** o navegador abrir a loja e clicar sozinho, acrescente `--com-janela`:

```bash
pytest -m funcional --com-janela
pytest -m funcional --com-janela tests/test_produto_no_navegador.py   # um arquivo só, mais fácil de acompanhar
```

O que esperar:

- **A janela é nova, separada do navegador que você já tem aberto.** O Selenium abre o Chromium (ou o Chrome) instalado no computador, mas com um perfil limpo e temporário: sem as suas abas, logins ou extensões. Assim os testes não mexem nos seus dados, e os seus dados não atrapalham os testes.
- **Ela abre e fecha rápido.** Cada teste abre a própria janela e fecha no fim, e os passos levam frações de segundo. Rode um arquivo só, ou um teste só com `-k`, para conseguir acompanhar.
- **Se o teste falhar, a janela também fecha.** Para descobrir em que tela ele parou, leia a mensagem de erro do pytest.

> Quer só navegar pela loja você mesmo? Isso não é com o Selenium: suba o servidor como na seção 1 e abra http://localhost:8000 no seu navegador de sempre.

**Não precisa deixar o servidor da seção 1 rodando:** cada teste funcional sobe o próprio servidor PHP, numa porta livre.

### Tudo de uma vez

```bash
pytest
```

### Os testes não mexem na sua loja

Cada teste ganha uma **cópia do app numa pasta temporária**, e o pytest apaga essa cópia no fim. O banco e as fotos de teste nascem nessa cópia. O seu `mini-loja.sqlite` e a sua pasta `uploads/` nunca são tocados, e dá para rodar os testes com o servidor da seção 1 ligado.

### Quando algo dá errado

| Sintoma | O que fazer |
|---|---|
| `could not find driver` ou erro de PDO nos testes | Os testes ligam o `pdo_sqlite` sozinhos quando ele está desligado no php.ini, mas a extensão **precisa estar instalada**. Veja "Se o `pdo_sqlite` estiver desligado" na seção 1. |
| `pytest: command not found` | O ambiente virtual não está ativado. Rode `source .venv/bin/activate` (ou `.venv\Scripts\activate` no Windows). |
| `This version of ChromeDriver only supports Chrome version ...` | O chromedriver e o navegador estão em versões diferentes. Atualize os dois juntos. |
| `Unable to obtain driver for chrome` / chromedriver não encontrado | Instale o chromedriver e confira se `chromedriver --version` responde no terminal. |
| `o servidor PHP não respondeu` | O PHP não subiu. A mensagem traz o log do servidor; rode `php -m` para conferir se o PHP funciona. |
| Teste funcional falha sem motivo aparente | Rode só esse teste de novo com `--com-janela` (por exemplo `pytest -m funcional --com-janela -k nome_do_teste`) e acompanhe a janela até ela fechar. |
| Rodei os funcionais e nenhuma janela abriu | É o normal: sem `--com-janela`, o Chrome roda escondido. |
