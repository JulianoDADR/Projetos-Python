# Arquivo responsável por todo tratamento do Boleto
# Criado por Juliano Dantas | TSI

import conexaoBD as bd
import requests
import base64
import json
import os
from PyPDF2 import PdfReader, PdfWriter
import msal
import pyshorteners  
import datetime as dt

# Class responsável por retornar o token de autentificação com a API do uau
class AuthManager:
    def __init__(self, login="u*i", login_site="****", password="*****"):# credenciais para realizar a API do token
        self.login = login
        self.login_site = login_site
        self.password = password
        self.api_url = "http://1**.1***.**.*9:***/uauAPI/api/v1.0/Autenticador/AutenticarUsuario"
        self.xint_auth = "******************************************************************Pap2lug"
        self.version = "1.0"
        self.token = None
    
    # Autentica na API e retorna o token
    def GetAuthentUAU(self):
        headers = {
            "Content-Type": "application/json",
            "version": self.version,
            "X-INTEGRATION-Authorization": self.xint_auth,
        }
        payload = json.dumps({
            "Login": self.login,
            "Senha": self.password,
            "UsuarioUAUSite": self.login_site
        })
        response = requests.post(self.api_url, headers=headers, data=payload)
        token = response.text.replace('"', "")
        self.token = token
        print(f"  Token de autenticação obtido com sucesso")
        return token
    
# Class responsável por pegar o código do boleto através de uma API e retorna base64
class BoletoAPI:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.api_url = "http://**4.**9.**.**:****/uauAPI/api/v1.0/BoletoServices/GerarPDFBoleto"
        self.xint_auth = "******************************************************uYC5kt6RD6QVEtPap2lug"
        self.version = "1.0"

    # Função responsável por pegar o código do boleto através da API e retorna em base64
    def GetBoleto(self, banco, num_boleto):
        """Gera um PDF de boleto usando a API e retorna o conteúdo em Base64."""
        if not self.auth_manager.token:
            self.auth_manager.GetAuthentUAU()
        headers = {
            "Content-Type": "application/json",
            "version": self.version,
            "Authorization": self.auth_manager.token,
            "X-INTEGRATION-Authorization": self.xint_auth,
        }
        payload = json.dumps({
            "cod_banco": banco,
            "seu_numero": num_boleto,
            "ocultar_dados_pessoais": True
        })
        response = requests.post(self.api_url, headers=headers, data=payload)
        response_text = response.text

        # Limpa a resposta se necessário
        if response_text.startswith('"') and response_text.endswith('"'):
            response_text = response_text[1:-1]
        return response_text
    
# Class responsável por receber o boleto em base64 e salvar o arquivo em PDF
# e criptografar o arquivo com o cpf do cliente
# e salvar o arquivo em uma pasta específica
class PDFManager:
    def __init__(self, pasta_destino=None):  
        if pasta_destino:
            self.pasta_destino = pasta_destino
        else:
            self.pasta_destino = fr"C:\Users\juliano.rodrigues\OneDrive - Cbl Desenvolvimento Urbano\Boletos API\Boletos_{dt.datetime.today().date()}"
        # Cria a pasta de destino se não existir
        if not os.path.exists(self.pasta_destino):
            os.makedirs(self.pasta_destino)

    # Função responsável por receber o boleto em base64 e salvar o arquivo em PDF
    def salvar_pdf(self, pdf_base64, nome_arquivo):
        try:
            # Decodifica a string Base64
            pdf_bytes = base64.b64decode(pdf_base64, validate=True)
            # Define o caminho completo do arquivo
            pdf_path = os.path.join(self.pasta_destino, nome_arquivo)
            # Salva o arquivo
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)
            return pdf_path
        except base64.binascii.Error:
            print(f"❌ Erro: A string Base64 do arquivo {nome_arquivo} pode estar corrompida.")
            return None
        except Exception as e:
            print(f"❌ Erro ao salvar PDF {nome_arquivo}: {e}")
            return None
    
    # Função responsável por criptografar o arquivo PDF com o cpf do cliente    
    def criptografar_pdf(self, pdf_path, senha):
        """Criptografa um PDF com uma senha."""
        try:
            # Arquivo temporário
            temp_pdf = pdf_path + ".temp"
            # Lê o PDF original
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            # Copia todas as páginas
            for page in reader.pages:
                writer.add_page(page)
            # Criptografa o PDF
            writer.encrypt(senha, use_128bit=True)
            # Salva o PDF criptografado
            with open(temp_pdf, "wb") as f:
                writer.write(f)
            # Substitui o arquivo original
            os.replace(temp_pdf, pdf_path)
            return True
        except Exception as e:
            print(f"❌ Erro ao criptografar PDF {pdf_path}: {e}")
            return False

# Class responsável pelo processo do OneDrive, incluindo autenticação, upload, criação de links públicos e encurtamento de links
class OneDriveManager:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.token = None

    # Função responsável por retornar o token de autenticação Microsoft Graph do OneDrive
    def GetAuthentONEDRIVE(self):
        app = msal.ConfidentialClientApplication(
            self.client_id, 
            authority=self.authority, 
            client_credential=self.client_secret
        )
        token_response = app.acquire_token_for_client(scopes=self.scopes)
        if "access_token" not in token_response:
            print("❌ Erro ao obter token de acesso do Microsoft Graph:")
            print(token_response)
            return False
        self.token = token_response["access_token"]
        return True
    
    #Função responsável por fazer o upload do arquivo para uma pasta específica no OneDrive
    def upload_file(self, file_path, destination_name=None):
        if not self.token:
            success = self.GetAuthentONEDRIVE()
            if not success:
                return None
            
        # Se não for especificado um nome de destino, usa o nome do arquivo original
        if not destination_name:
            destination_name = os.path.basename(file_path)
        upload_url = f"https://graph.microsoft.com/v1.0/drive/root:/{destination_name}:/content"

        try:
            with open(file_path, "rb") as file:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.put(upload_url, headers=headers, data=file)
                if response.status_code in [200, 201]:
                    data = json.loads(response.text)
                    download_url = data.get("@microsoft.graph.downloadUrl")
                    if download_url:
                        #print(f"✅ Arquivo {destination_name} enviado com sucesso para o OneDrive")
                        return download_url
                    else:
                        print(f"❌ Link de download não encontrado para {destination_name}")
                        return None
                else:
                    print(f"❌ Erro ao enviar arquivo {destination_name}: {response.status_code}, {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo {destination_name} para o OneDrive: {e}")
            return None
        
    # Foi notado que as funções comentadas abaixo não eram precisas para o funcionamento do código, mas foram mantidas para caso seja necessário no futuro.
    # 17/04/2025 - Juliano Dantas

        # Função responsável por criar um link público para o arquivo no OneDrive
        #def create_public_share_link(self, file_id):
        #    """Cria um link público para o arquivo no OneDrive."""
        #    share_url = f"https://graph.microsoft.com/v1.0/drive/items/{file_id}/createLink"
        #    headers = {
        #        "Authorization": f"Bearer {self.token}",
        #        "Content-Type": "application/json"
        #    }
        #    payload = {
        #        "type": "view",  # "view" cria um link apenas para visualização
        #        "scope": "anonymous"  # Tornar o link acessível para qualquer pessoa com o link
        #    }

        #    try:
        #        response = requests.post(share_url, headers=headers, json=payload)
        #        if response.status_code == 200:
        #            data = response.json()
        #            link = data.get("link", {}).get("webUrl")
        #            if link:
        #                return link
        #            else:
        #                print("❌ Link público não encontrado na resposta.")
        #                return None
        #        else:
        #            print(f"❌ Erro ao criar link público: {response.status_code}, {response.text}")
        #            return None
        #    except Exception as e:
        #        print(f"❌ Erro ao criar link público para o arquivo: {e}")
        #        return None

        ## Função responsável por encurtar o link usando na função acima utilizando TinyURL    
        #def encurtar_link(self, url):
        #    shortener = pyshorteners.Shortener()
        #    short_url = shortener.tinyurl.short(url)
        #    return short_url

# Class responsável por buscar e retornar todos os dados do uau que utilizamos nas funções acima
# e retorna em um dicionário
class DatabaseManager:
    def __init__(self, cursor):
        self.cursor = cursor
    # Função responsável por retornar que iremos utilizar na função GetBoleto e criptografar_pdf e retorna em um dicionário
    def buscar_boletos(self):
        """Busca informações de boletos no banco de dados."""
        query = """
        SELECT  *
        FROM DADOS 
        """
        self.cursor.execute(query)
        resultados = []
        for row in self.cursor.fetchall():
            boleto_info = {
                'cpf': row[0],
                'telefone': row[1],
                'banco': row[2],
                'num_boleto': row[3],
                'linha_digitavel': row[4],
                'aviso': row[5]
            }
            resultados.append(boleto_info)
        return resultados

# Class responsável por gerenciar o processo de geração, criptografia e upload dos boletos
# utilizando as classes acima e retorna os resultados em um dicionário
class BoletoManager:
    def __init__(self):
        # Inicializa os gerenciadores
        self.auth_manager = AuthManager()
        self.boleto_api = BoletoAPI(self.auth_manager)
        self.pdf_manager = PDFManager()
        self.onedrive_manager = OneDriveManager(
            client_id="16************************3ec859ff581", # ID do aplicativo registrado no Azure
            client_secret="**************************w5.xcAi", # Secret ID do aplicativo registrado no Azure
            tenant_id="8f******************ee" # ID do locatário (tenant) do Azure
        )
        self.db_manager = DatabaseManager(bd.cursor)

    # Função responsável por processar todos os boletos, incluindo busca, geração de PDF, criptografia, upload, encurtamento de link e retorno dos resultados
    # com o resultados ele salva em um arquivo JSON(resultados_boletos.json) na pasta de destino.
    def processar_boletos(self):
        """Processa todos os boletos: busca, gera PDF, criptografa e faz upload."""
        erro_envios = []

        boletos = self.db_manager.buscar_boletos()
        print(f"🔍 Encontrados {len(boletos)} boletos para processar")

        resultados = []

        # Barra retirada para deixar a tela/terminal menos poluída       
            #progress_bar = tqdm(total=len(boletos))

        # Loop para processar cada boleto
        i= 0
        for boleto in boletos:
            # Atualiza a barra de progresso
                #progress_bar.update(1)
            nome_arquivo = f"Boleto_{boleto['num_boleto']}_{boleto['telefone']}_{boleto['banco']}.pdf"
            i += 1

            try:
                
                # Pega o boleto em base64
                pdf_base64 = self.boleto_api.GetBoleto(boleto['banco'], boleto['num_boleto'])
                # Trasnforma o base64 em PDF e salva na pasta de destino
                pdf_path = self.pdf_manager.salvar_pdf(pdf_base64, nome_arquivo)
                if not pdf_path:
                    continue
                
                # Criptografa o PDF com os 6 primeiros dígitos do CPF
                senha = str(boleto['cpf'])[:6]
                success = self.pdf_manager.criptografar_pdf(pdf_path, senha)
                if not success:
                    continue
                
                # Faz upload do PDF criptografado para o OneDrive
                download_url = self.onedrive_manager.upload_file(pdf_path, nome_arquivo)
                if not download_url:
                    continue
                shortener = pyshorteners.Shortener(timeout=10) # Possui um tempo de 10 segundo para criar o link do arquivo
                download_url = shortener.tinyurl.short(download_url)

                # Adiciona o resultado(boleto individual)
                resultado = {
                    'cpf': boleto['cpf'],
                    'telefone': boleto['telefone'],
                    'banco': boleto['banco'],
                    'num_boleto': boleto['num_boleto'],
                    'linha_digitavel': boleto['linha_digitavel'],
                    'aviso': boleto['aviso'],
                    'nome_arquivo': nome_arquivo,
                    'download_url': download_url
                }
                resultados.append(resultado) # 'Resultados' é responsável por aglutinas todo 'resultado' em um dicionário
                print(f"✅ Boleto {nome_arquivo} processado com sucesso ({i}/{len(boletos)})")
                
            except Exception as e:
                print(f"❌ Erro ao processar boleto {boleto['num_boleto']} ({i}/{len(boletos)}): {e}")
                erro_envios.append(f"❌ Erro ao processar boleto {boleto['num_boleto']} ({i}/{len(boletos)}): {e}")
                return
            
        # Fecha a barra de progresso
            #progress_bar.close()

        # Salva o 'resultados' em um arquivo JSON
        with open(fr'C:\Users\juliano.rodrigues\Desktop\Projetos CBL\Projeto de Disparo Whtasapp + API Meta\jsons\resultados_boletos.json', "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)

        print(resultados)
        print(f"✅ Processamento concluído. {len(resultados)} de {len(boletos)} boletos processados com sucesso.")
        print("")
        print("Boletos que geraram erros ao importar: ")
        print("")
        print(erro_envios)
        #for i in erro_envios:
        #    print(i)
        return resultados

# Função que executa o código
def Executa():
    if __name__ == "__main__":
        boleto_manager = BoletoManager()
        boleto_manager.processar_boletos()
