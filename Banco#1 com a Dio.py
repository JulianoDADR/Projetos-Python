import time

registro = 0
conta = 0
comands = 0
extrato_de_saque = []
extrato_de_deposito = []

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

while comands != 4:
    if len(conta) == 5:
        print(comandos)
        comands = int(input())
        if comands == 1:
            saque = int(input("Qual o valor do saque: "))
            if len(extrato_de_saque) == 3:
                print("Você excedeu o número de saque por acesso na conta.")
                time.sleep(1)
                break
            if saque >= 0:
                registro = registro - saque
                extrato_de_saque.append(registro)
                print("O extrato da conta ficou ", registro)
                time.sleep(1)
            else:
                msg_saque

        if comands == 2:
            deposito = int(input("Qual o valor do seu deposito: "))
            if deposito >= 0:
                registro = +deposito 
                extrato_de_deposito.append(registro)
                print("O extrato da conta ficou ", registro)
                time.sleep(1)
            else:
                msg_deposito
        
        if comands == 3:
            print("O saldo da conta ficou ", registro)
            print("Ocorreram essas alterações no saque: ", extrato_de_saque )
            print("Ocorreram essas alterações no deposito: ", extrato_de_deposito )

    time.sleep(1)
    print("Sua agência foi diferente de 5.")
print("O extrato da conta ficou ", registro)