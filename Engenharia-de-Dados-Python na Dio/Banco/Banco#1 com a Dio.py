from abc import ABC, abstractclassmethod, abstractproperty
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
1 - Acessar conta
2 - Registrar conta
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


class Interface():
    def __init__ (self, nome_titular, cpf, agencia, data_nasc):
        nome_titular.self = nome_titular
        cpf.self = cpf
        agencia.self = agencia
        data_nasc.self = data_nasc

def funcoes():
    if len(extrato_da_conta) == 10:
            print("Você excedeu o número de transações por acesso na conta.")
            time.sleep(1)
            

    if len(agencia) == 5:
        print(comandos)
        comands = int(input())

        if comands == 1:
            saque(registro)

        if comands == 2:
            deposito(registro)

        if comands == 3:
            visualizar()

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

def registro_conta():
    nome = input("Digite seu nome: ")
    cpf = input("Digite seu cpf: ")
    agencia = input("Digite sua agência com o máximo 5 dígitos: ")
    nascimento = input("Digite sua data de nascimento somente: ")
    agencia = Interface(nome, cpf, agencia, nascimento)

def visualizar():
    print("O saldo da conta ficou ", registro)
    print("Ocorreram essas alterações no saque: ", extrato_de_saque )
    print("Ocorreram essas alterações no deposito: ", extrato_de_deposito )

print(agencia)
time.sleep(1)
inicio = int(input(""))
time.sleep(1)

while comands != 4:
    
    if inicio == 1:
        agencia = input("Digite a sua agência: ")
        funcoes()


    if inicio == 2:
        registro_conta()
        funcoes()

print("O extrato da conta ficou ", registro)