import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class Navegador(webdriver.Chrome):
    """
    Classe personalizada do navegador, estendendo o webdriver.Chrome do Selenium.
    """

    def __init__(self, link=None, caminho_downloads=None, options: Options = None, service: Service = None, keep_alive: bool = True, headless = False) -> None:
        """
        Inicializa o navegador com as opções especificadas.
        """
        #  define opções padrão se não forem fornecidas
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
        
        if headless:
            # Configurações para o modo headless
            if not options:
                options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")

        # define o cominho de downloads se fornecido
        if caminho_downloads:
            prefs = {
                "download.default_directory": caminho_downloads,
                "download.prompt_for_download": False,
                "directory_upgrade": True
            }
            options.add_experimental_option("prefs", prefs)

        # Chama a classe pai com as opções fornecidas
        super().__init__(service=service, options=options, keep_alive=keep_alive)

        # se um link for fornecido, abre a página
        if link:
            self.get(link)

    # Realiza uma rolagem para baixo gradualmente ao longo do tempo especificado
    def rolar_para_baixo_gradualmente(self, tipo_find_element, atributo, duracao=5, passos=5):
        """
        Rola a página para baixo gradualmente ao longo do tempo especificado e procura o elemento a cada passo.
        """
        total_height = self.execute_script("return document.body.scrollHeight")
        window_height = self.get_window_size()['height']
        max_scroll = total_height - window_height
        if max_scroll <= 0:
            return

        scroll_amount_per_step = max_scroll / passos
        for step in range(1, passos + 1):
            scroll_position = step * scroll_amount_per_step
            self.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(duracao / passos)
            if len(self.find_elements(tipo_find_element, atributo)) > 0:
                return  # Sai da função assim que encontrar o elemento

    # realiza uma rolagem para cima gradualmente ao longo do tempo especificado
    def rolar_para_cima_gradualmente(self, tipo_find_element, atributo, duracao=5, passos=5):
        """
        Rola a página para cima gradualmente ao longo do tempo especificado e procura o elemento a cada passo.
        """
        total_height = self.execute_script("return document.body.scrollHeight")
        window_height = self.get_window_size()['height']
        max_scroll = total_height - window_height
        if max_scroll <= 0:
            return

        scroll_amount_per_step = max_scroll / passos
        for step in range(passos, -1, -1):
            scroll_position = step * scroll_amount_per_step
            self.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(duracao / passos)
            if len(self.find_elements(tipo_find_element, atributo)) > 0:
                return  # Sai da função assim que encontrar o elemento

    # Aplica zoom in gradualmente ao longo do tempo especificado
    def aplicar_zoom_out_gradualmente(self, tipo_find_element, atributo, duracao=5, passos=5, min_zoom=50):
        """
        Aplica zoom out gradualmente na página ao longo do tempo especificado e procura o elemento a cada passo.
        """
        initial_zoom_level = 100  # Zoom inicial em 100%
        zoom_amount_per_step = (initial_zoom_level - min_zoom) / passos
        for step in range(1, passos + 1):
            zoom_level = initial_zoom_level - (step * zoom_amount_per_step)
            if zoom_level < min_zoom:
                zoom_level = min_zoom
            self.execute_script(f"document.body.style.zoom='{zoom_level}%'")
            time.sleep(duracao / passos)
            if len(self.find_elements(tipo_find_element, atributo)) > 0:
                return  # Sai da função assim que encontrar o elemento

    # Identificação de elementos genérica com base no tipo e atributo fornecidos
    def identifica_elemento(self, tipo_find_element, atributo, timeout=15, varredura=True, multiplo=False):
        """
        Identifica elementos na página com base no tipo e atributo fornecidos.
        Se varredura estiver ativa, realiza rolagens e zoom para tentar localizar o(s) elemento(s).
        """
        initial_scroll_position = self.execute_script("return window.pageYOffset;")
        initial_zoom_level = self.execute_script("return document.body.style.zoom || '100%';")
        verifica_erro = 0
        elemento = None  # Inicializa o elemento como None
        elemento_encontrado = False  # Flag para indicar se o elemento foi encontrado

        try:
            while len(self.find_elements(tipo_find_element, atributo)) < 1:
                time.sleep(1)
                verifica_erro += 1
                if varredura:
                    if verifica_erro == 5:
                        # Aplicar zoom out gradualmente ao longo de 5 segundos e procurar o elemento a cada passo
                        self.aplicar_zoom_out_gradualmente(tipo_find_element, atributo,duracao=timeout/4, min_zoom=50)
                        
                    elif verifica_erro == 10:
                        # Rolar para baixo gradualmente ao longo de 5 segundos e procurar o elemento a cada passo
                        self.rolar_para_baixo_gradualmente(tipo_find_element, atributo, duracao=timeout/4)
                        
                    elif verifica_erro == 15:
                        # Rolar para cima gradualmente ao longo de 5 segundos e procurar o elemento a cada passo
                        self.rolar_para_cima_gradualmente(tipo_find_element, atributo, duracao=timeout/4)
                        
                if verifica_erro > timeout:
                    if varredura:
                        print(f"ERRO: Elemento '{atributo}' não encontrado após várias tentativas.")
                    return None
            time.sleep(1)
            # Elemento encontrado
            elemento_encontrado = True
            if multiplo:
                return self.find_elements(tipo_find_element, atributo)
            else:
                elemento = self.find_element(tipo_find_element, atributo)
                self.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                return elemento
        finally:
            # Restaurar o zoom inicial, independentemente de ter encontrado ou não
            self.execute_script(f"document.body.style.zoom='{initial_zoom_level}'")
            if not elemento_encontrado:
                # Se não encontrou o elemento, retorna à posição inicial de rolagem
                self.execute_script(f"window.scrollTo(0, {initial_scroll_position});")

    # Identificação de elementos genérica
    def identifica_elementos(self, tipo_find_element, atributo, timeout=15, varredura=True):
        return self.identifica_elemento(tipo_find_element, atributo, timeout=timeout, varredura=varredura, multiplo=True)

    # Métodos específicos para busca de elementos únicos
    def identifica_elemento_xpath(self, xpath, timeout=15, varredura=True):
        return self.identifica_elemento(By.XPATH, xpath, timeout=timeout, varredura=varredura)

    def identifica_elemento_id(self, id, timeout=15, varredura=True):
        return self.identifica_elemento(By.ID, id, timeout=timeout, varredura=varredura)

    def identifica_elemento_cssselector(self, cssselector, timeout=15, varredura=True):
        return self.identifica_elemento(By.CSS_SELECTOR, cssselector, timeout=timeout, varredura=varredura)

    def identifica_elemento_name(self, name, timeout=15, varredura=True):
        return self.identifica_elemento(By.NAME, name, timeout=timeout, varredura=varredura)
    
    def identifica_elemento_tagname(self, tagname, timeout=15, varredura=True):
        return self.identifica_elemento(By.TAG_NAME, tagname, timeout=timeout, varredura=True)

    # Métodos específicos para busca de múltiplos elementos
    def identifica_elementos_xpath(self, xpath, timeout=15, varredura=True):
        return self.identifica_elementos(By.XPATH, xpath, timeout=timeout, varredura=varredura)

    def identifica_elementos_id(self, id, timeout=15, varredura=True):
        return self.identifica_elementos(By.ID, id, timeout=timeout, varredura=varredura)

    def identifica_elementos_cssselector(self, cssselector, timeout=15, varredura=True):
        return self.identifica_elementos(By.CSS_SELECTOR, cssselector, timeout=timeout, varredura=varredura)

    def identifica_elementos_name(self, name, timeout=15, varredura=True):
        return self.identifica_elementos(By.NAME, name, timeout=timeout, varredura=varredura)
    
    def identifica_elementos_tagname(self, tagname, timeout=15, varredura=True):
        return self.identifica_elementos(By.TAG_NAME, tagname, timeout=timeout, varredura=varredura)

    # Métodos específicos para busca de elementos únicos
    def clica_elemento_xpath(self, xpath, timeout=15, varredura=True):
        elemento = self.identifica_elemento_xpath(xpath, timeout=timeout, varredura=varredura)
        if elemento:
            elemento.click()

    def envia_teclas_elemento_xpath(self, xpath, valor, timeout=15, varredura=True):
        elemento = self.identifica_elemento_xpath(xpath, timeout=timeout, varredura=varredura)
        if elemento:
            elemento.send_keys(valor)

    # tira um screenshot da página
    def tirar_screenshot(self, file_path):
        try:
            self.save_screenshot(file_path)
        except Exception as e:
            print(f"Erro ao salvar captura de tela: {e}")

    # Muda para a aba do navegador especificada pelo índice
    def mudar_para_aba(self, indice):
        """
        Muda para a aba do navegador especificada pelo índice.
        """
        try:
            self.switch_to.window(self.window_handles[indice])
        except IndexError:
            print(f"Erro: Nenhuma aba encontrada no índice {indice}")

    # rola a tela em um número específico de pixels
    def rolar_tela(self, pixels):
        """
        Rola a tela em um número específico de pixels.
        """
        self.execute_script(f"window.scrollBy(0, {pixels});")

    # espera a página carregar completamente
    def esperar_pagina_carregar(self, timeout=30):
        """
        Espera a página carregar completamente até o tempo limite especificado.
        """
        WebDriverWait(self, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    # responde a um alerta (popup) na página
    def responder_alerta(self, aceitar=False, timeout=15):
        """
        Responde a um alerta (popup) na página.
        """
        try:
            WebDriverWait(self, timeout).until(EC.alert_is_present())
            alert = self.switch_to.alert
            if aceitar:
                alert.accept()
            else:
                alert.dismiss()
        except Exception as e:
            print(f"Erro ao lidar com o alerta: {e}")

    # entra em um iframe específico
    def entrar_no_iframe(self, iframe):
        """
        Entra em um iframe especificado.
        """
        self.esperar_pagina_carregar()
        self.switch_to.frame(iframe)

    # sai do iframe atual
    def sair_do_iframe(self):
        """
        Sai do iframe atual e retorna ao conteúdo padrão.
        """
        self.esperar_pagina_carregar()
        self.switch_to.default_content()
    
    # seleciona uma opção de um menu suspenso
    def menu_selecao(self, elemento, metodo, valor=None):
        """
        Função genérica para selecionar uma opção de um menu suspenso (<select>) na página usando diferentes métodos.
    
        :param elemento: O elemento <select> já encontrado.
        :param metodo: O método de seleção ('value', 'index' ou 'visible_text').
        :param valor: O valor correspondente ao método escolhido.
        """

        elemento_selecao = Select(elemento)
    
        if metodo == 'value':
            elemento_selecao.select_by_value(valor)
        elif metodo == 'index':
            elemento_selecao.select_by_index(int(valor))
        elif metodo == 'visible_text':
            elemento_selecao.select_by_visible_text(valor)
        else:
            raise ValueError("Método de seleção inválido. Use 'value', 'index' ou 'visible_text'.")
        
    def monta_xpath_por_palavras(self, palavras: str) -> str:
        """
        Monta um XPath que contém todas as palavras fornecidas. Para pesquisar um elemento pelo seu texto.
        """
        # Converte todas as palavras para maiúsculas e divide em uma lista
        palavras = palavras.upper().split()
        # Constrói o XPath adicionando uma condição `contains` para cada palavra
        condicoes = ' and '.join([f"contains(text(), '{palavra}')" for palavra in palavras])
        return f"//*[{condicoes}]"
    
    def rolar_para_elemento(self, tipo_find_element, atributo_elemento):
        """
        Rola a página até que o elemento especificado esteja visível na tela.
        """
        # Seleciona um elemento visível na tela
        elemento_rolagem = self.identifica_elemento(tipo_find_element, atributo_elemento)
        # Aguarda 1 segundo
        time.sleep(1)
        # Realiza a rolagem até o elemento
        self.execute_script("arguments[0].scrollIntoView();", elemento_rolagem)