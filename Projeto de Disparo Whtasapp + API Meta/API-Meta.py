import requests
import json

ACCESS_TOKEN = "Key"

PHONE_NUMBER_ID = "101929325884906"
API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

payload = json.dumps({
  "messaging_product": "whatsapp",
  "to": "number",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": { "code": "en_US" }
  }
})

headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}

response = requests.request("POST", API_URL, headers=headers, data=payload)

print(response.status_code)
print(response.text)





#def enviar_mensagem(numero_destino, mensagem):
#    headers = {
#        "Authorization": f"Bearer {ACCESS_TOKEN}",
#        "Content-Type": "application/json"
#    }
#
#    data = {
#        "messaging_product": "whatsapp",
#        "recipient_type": "individual",
#        "to": numero_destino,
#        "type": "text",
#        "text": {
#        "preview_url": 'false',
#        "body": "text-message-content"
#    }
#    }
#
#    response = requests.post(API_URL, json=data, headers=headers)
#    
#    return response.json()
#
## Exemplo de uso
#resposta = enviar_mensagem("5527998681077", "Oi Olá! Este é um teste de envio usando a API do WhatsApp da Met teste Olá! Este é um teste de envio usando a API do WhatsApp da Meta..")
#print(resposta)