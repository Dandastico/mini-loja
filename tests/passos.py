# passos.py: o que uma pessoa faz na loja, escrito uma vez só para todos os testes funcionais.

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def esperar_a_resposta(navegador, formulario):
    """Espera a resposta do envio: o formulário antigo some da página.

    No meio da troca de página o Chrome às vezes responde com um erro genérico
    ("Node ... does not belong to the document") em vez de "elemento velho";
    esse erro é ignorado e a espera tenta de novo.
    """
    WebDriverWait(navegador, 10, ignored_exceptions=(WebDriverException,)).until(
        EC.staleness_of(formulario)
    )


def cadastrar_funcionario(navegador, loja, nome, email, senha):
    """Abre a área do funcionário e preenche o formulário de cadastro."""
    navegador.get(f"{loja}/funcionario.php")
    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//form[input[@name='acao' and @value='cadastrar']]"))
    )
    formulario.find_element(By.ID, "nome").send_keys(nome)
    formulario.find_element(By.ID, "email").send_keys(email)
    formulario.find_element(By.ID, "senha").send_keys(senha)
    formulario.find_element(By.XPATH, ".//button[text()='Cadastrar']").click()
    esperar_a_resposta(navegador, formulario)


def entrar(navegador, loja, email, senha):
    """Abre a área do funcionário e entra com o e-mail e a senha."""
    navegador.get(f"{loja}/funcionario.php")
    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//form[input[@name='acao' and @value='entrar']]"))
    )
    formulario.find_element(By.ID, "email-entrar").send_keys(email)
    formulario.find_element(By.ID, "senha-entrar").send_keys(senha)
    formulario.find_element(By.XPATH, ".//button[text()='Entrar']").click()
    esperar_a_resposta(navegador, formulario)


def enviar_por_fora(navegador, loja, pagina, campos):
    """Envia um POST para a página sem usar os botões dela, como faria um visitante esperto.

    Monta um formulário escondido na página aberta (com os campos pedidos) e envia.
    """
    navegador.get(f"{loja}/index.html")
    navegador.execute_script(
        """
        const [acao, campos] = arguments;
        const form = document.createElement('form');
        form.method = 'post';
        form.action = acao;
        for (const [nome, valor] of Object.entries(campos)) {
            const campo = document.createElement('input');
            campo.type = 'hidden';
            campo.name = nome;
            campo.value = valor;
            form.appendChild(campo);
        }
        document.body.appendChild(form);
        form.submit();
        """,
        f"{loja}/{pagina}",
        campos,
    )


def cadastrar_produto(navegador, loja, nome, preco, foto=None):
    """Abre a vitrine (já logado) e cadastra um produto novo com nome e preço (e a foto, se vier)."""
    navegador.get(f"{loja}/cadastro.php")
    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//form[.//input[@name='nome']]"))
    )
    formulario.find_element(By.ID, "nome").send_keys(nome)
    formulario.find_element(By.ID, "preco").send_keys(preco)
    if foto:
        # o campo de arquivo aceita o caminho do arquivo, como se a pessoa escolhesse na janela
        formulario.find_element(By.ID, "imagem").send_keys(str(foto))
    formulario.find_element(By.XPATH, ".//button[text()='Cadastrar']").click()
    esperar_a_resposta(navegador, formulario)


def editar_produto(navegador, nome, foto=None):
    """Na vitrine aberta (já logado), clica em "Editar" no produto e salva, trocando a foto se vier."""
    navegador.find_element(By.XPATH, f"//ul/li[contains(., '{nome}')]").find_element(By.LINK_TEXT, "Editar").click()
    formulario = WebDriverWait(navegador, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h2[text()='Editar produto']/following::form[1]"))
    )
    if foto:
        formulario.find_element(By.ID, "imagem").send_keys(str(foto))
    formulario.find_element(By.XPATH, ".//button[text()='Salvar alterações']").click()
    esperar_a_resposta(navegador, formulario)
