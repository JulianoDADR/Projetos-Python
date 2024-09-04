from datetime import datetime
import pytz
import time

registro = 0
conta = 0
comands = 0
extrato_de_saque = []
extrato_de_deposito = []
extrato_da_conta = []
data = str(datetime.now(pytz.timezone("America/Sao_Paulo")))
print(data[0:16])

# mensagens
agencia = """
A agencia deve conter extamente 5 dígitos!
"""

comandos = """
Você possui as seguintes opções: 

1 - Saque
2 - Deposito
3 - Visualizar Extrato
4 - Sair
"""
msg_saque = """
Seu saque precisa ser maior que 0."""

msg_deposito = """
Seu deposito precisa ser maior que 0."""

print(agencia)
time.sleep(1)
conta = input("Digite a agencia da sua conta: ")
time.sleep(1)

def saque(registro):
    saque = int(input("Qual o valor do saque: "))

    if saque >= 0:
        registro = registro - saque
        extrato_da_conta.append(registro)
        extrato_de_saque.append(registro)
        extrato_de_saque.append(data[0:16])
        print("O extrato da conta ficou ", registro)
        time.sleep(1)
    else:
        msg_saque

def deposito(registro):
    deposito = int(input("Qual o valor do seu deposito: "))
    if deposito >= 0:
        registro = +deposito 
        extrato_da_conta.append(registro)
        extrato_de_deposito.append(registro)
        extrato_de_deposito.append(data[0:16])
        print("O extrato da conta ficou ", registro)
        time.sleep(1)
    else:
        msg_deposito

def visualizar():
    print("O saldo da conta ficou ", registro)
    print("Ocorreram essas alterações no saque: ", extrato_de_saque )
    print("Ocorreram essas alterações no deposito: ", extrato_de_deposito )

while comands != 4:
    if len(extrato_da_conta) == 10:
        print("Você excedeu o número de transações por acesso na conta.")
        time.sleep(1)
        break

    if len(conta) == 5:
        print(comandos)
        comands = int(input())

        if comands == 1:
            saque(registro)

        if comands == 2:
            deposito(registro)

        if comands == 3:
            visualizar()

print("O extrato da conta ficou ", registro)