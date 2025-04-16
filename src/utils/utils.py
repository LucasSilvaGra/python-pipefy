import os
from pathlib import Path
import time

#Obtem o Diretório Padrão de Downloads do Computador, Substitui o Método 'C:\\Users\\' + os.getlogin() + '\\Downloads' pois causa erros para usuários com .Ext
def obter_caminho_downloads():
    return str(Path.home() / "Downloads")

#Obtem o Arquivo mais recente de uma Pasta
def obter_ultimo_arquivo(diretorio):
    try:
        # Lista todos os arquivos no diretório fornecido
        Arquivos = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, f))]
        
        # Verifica se há arquivos na lista
        if not Arquivos:
            return None
        
        # Encontra o arquivo com a data de modificação mais recente
        Ultimo_Arquivo = max(Arquivos, key=os.path.getmtime)
        return Ultimo_Arquivo
    except Exception as e:
        print(f"Erro ao acessar o diretório: {e}")
        return None
    
def aguardar_arquivo_baixar(Quantidade_Arquivos_Antes, timeout=20, caminho_downloads=None):

    if not caminho_downloads:
        caminho_downloads = obter_caminho_downloads()

    #Aguardar Arquivo Terminar de Baixar e Deixar de ser um Arquivo Temporário do Chrome
    time.sleep(2)
    Verificador = True
    Contador = 0
    while Verificador:
        Contador += 1
        time.sleep(1)
        if len(os.listdir(caminho_downloads)) != Quantidade_Arquivos_Antes:
            Verificador = False
            Arquivo = obter_ultimo_arquivo(caminho_downloads)    
            if ('crdownload' in Arquivo) or ('.tmp') in Arquivo:
                Verificador = True

        if Contador > timeout:
            print('Erro ao Baixar Relatório - Tempo Excedido')
            break