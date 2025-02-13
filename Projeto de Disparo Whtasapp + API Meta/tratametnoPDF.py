import requests as rq
import pandas as pd
import base64
import json
import io
import os
from PyPDF2 import PdfReader, PdfWriter
import base64
import conexaoBD as bd

boleto = []
banco = []
cpf = []
telefone = []
linha_digitavel = []
aviso = []

def ProcessoPDF(cpf, telefone, banco, boleto, linha_digitavel, aviso):
    query = "SELECT * FROM TABLE"

    def PegarAuth():
        global auth
        # Authorization
        login = "XXX"
        loginsite = "XXX"
        password = "XXXX"
        url_auth = "http://192.xxx.xx.xx:80xx/uauAPI/api/v1.0/Autenticador/AutenticarUsuario"
        xint_auth = "key"
        version = "1.0"
        true = "true"
        header_auth = {
            "Content-Type": "application/json",
            "version": version,
            "Content-Type": "application/json",
            "X-INTEGRATION-Authorization": xint_auth,
            }
        payload_auth = json.dumps({
          "Login": login,
          "Senha": password,
          "UsuarioUAUSite": loginsite
        })
        response_auth = rq.request("POST", url_auth, headers=header_auth, data=payload_auth)
        auth = response_auth.text
        auth = auth.replace('"',"")
        print(f"Token de autenticação: {auth}")
    
    PegarAuth()
    
    def buscar_boleto(cursor):
        """Busca os boletos e adiciona linha por linha nas listas globais."""
        cursor.execute(query)  # O parâmetro precisa estar dentro de uma tupla
        for row in cursor.fetchall():
            cpf.append(row[0])
            telefone.append(row[1]) 
            banco.append(row[2])
            boleto.append(row[3])
            linha_digitavel.append(row[4])
            aviso.append(row[5]) # Adiciona apenas um valor por vez

    def PegarBoletos(num_boleto, banco, cpf, telefone, auth):
        # Authorization
        xint_auth = "key"
        version = "1.0"
        true = "true"
        # ExportarVendasXML
        url = "http://192.xxx.xx.xx:80xx/uauAPI/api/v1.0/BoletoServices/GerarPDFBoleto"
        header = {
            "Content-Type": "application/json",
            "version": version,
            "Content-Type": "application/json",
            "Authorization": auth,
            "Content-Type": "application/json",
            "X-INTEGRATION-Authorization": xint_auth,
            }
        payload = json.dumps({
            "cod_banco": banco,
            "seu_numero": num_boleto,
            "ocultar_dados_pessoais": true
        })
        response = rq.request("POST", url, headers=header, data=payload)
        response = response.text
        print(f"Response: {response}")
        with io.StringIO(response) as file:
            data = json.load(file)
        if "?xml" in data:
            del data["?xml"]
        with open("ExportVendas.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        try:
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1] 

            # Decodifica a resposta Base64 para bytes
            pdf_bytes = base64.b64decode(response, validate=True)
            
            pasta_destino = r"C:\Users\juliano.rodrigues"
            
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)

            # Define o caminho do PDF
            pdf_path = os.path.join(pasta_destino, f"Boleto_{num_boleto}_{telefone}_{banco}.pdf")

            # Salva o PDF temporariamente
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)

            # Criptografa o mesmo arquivo usando os 6 primeiros dígitos do ID
            temp_pdf = pdf_path + ".temp"
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Copia todas as páginas
            for page in reader.pages:
                writer.add_page(page)

            # Define a senha com os 6 primeiros caracteres do ID
            senha = str(cpf)[:6]
            print(senha)
            writer.encrypt(senha, use_128bit=True)

            # Salva no arquivo temporário
            with open(temp_pdf, "wb") as f:
                writer.write(f)

            # Substitui o original pelo criptografado
            os.replace(temp_pdf, pdf_path)
            print(f"✅ PDF salvo e criptografado com sucesso: {pdf_path}")
        except base64.binascii.Error:
            print("❌ Erro: A string Base64 pode estar corrompida. Verifique a resposta da API.")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    buscar_boleto(bd.cursor)

    def SalvarBoletos():
        contar = len(boleto)
        print(f'A quantidade de boletos é {contar}')
        print(f'A quantidade de bancos são {len(banco)}')
        print(f'A quantidade de cpfs são: {len(cpf)}')
        print(f'A quantidade de numeros são: {len(telefone)}')
        print(f'A quantidade de linhas são: {len(linha_digitavel)}')
        print(f'A quantidade de numeros são: {len(aviso)}')
        for i in range(contar):
            PegarBoletos(boleto[i], banco[i], cpf[i], telefone[i], auth)

    SalvarBoletos()

ProcessoPDF(cpf, telefone, banco, boleto, linha_digitavel, aviso)