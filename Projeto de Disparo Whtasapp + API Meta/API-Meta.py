import requests
import json

token = "E*************************************************************************ZD"
arquivo = fr'jsons/teste.json'

# Pegar do json resultados_boletos as informações necessárias para disparar a mensagem
def EnvioMensagem(token, arquivo):
    def disparoTemplateBoleto(numero_cliente, aviso, download_url, linha_digitavel): #numero_cliente, #link_boleto, #linha digitavel
      ACCESS_TOKEN = token

      PHONE_NUMBER_ID = "*************21938"
      API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

      payload = json.dumps({
        "messaging_product": "whatsapp",    
        "recipient_type": "individual",
        "to": numero_cliente,
        "type": "template",
        "template": {
            "name":"teste_disparotsi",
            "language":{
                "code":"pt_BR" 
            },
            "components":[{
                    "type":"body",
                    "parameters":[
                        {
                            "type":"text",
                            "text":aviso
                        },
                        {
                            "type":"text",
                            "text":download_url
                        },                    
                        {
                            "type":"text",
                            "text":linha_digitavel
                        }

                    ]
                }
            ]
    }
    })

      headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
      }

      response = requests.request("POST", API_URL, headers=headers, data=payload)

      print(response.status_code)
      print(response.text)


    with open(arquivo, 'r', encoding="utf-8") as arquivo:
      resultados_boletos = json.load(arquivo)

    for i in resultados_boletos:
      disparoTemplateBoleto(i['telefone'], i['aviso'], i['download_url'], i['linha_digitavel'])
#EnvioMensagem(token, arquivo)
