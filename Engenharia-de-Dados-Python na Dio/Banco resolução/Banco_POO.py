from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereço = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)   

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = historico()

        @classmethod
        def nova_conta(cls, cliente, numero):
            return cls(numero, cliente)
        
        @property
        def saldo(self):
            return self.saldo
        
        @property
        def numero(self):
            return self.numero
        
        @property
        def agencia(self):
            return self.agencia
        
        @property
        def cliente(self):
            return self.cliente
        
        @property
        def historico(self):
            return self. historico

        @property
        def sacar(self, valor):
            saldo = self.saldo
            excedeu_saldo = valor > saldo

            if excedeu_saldo:
                print("\n@@@ Você não possui saldo surficiente. @@@")

            elif valor > 0:
                self.saldo -= valor
                print("Saque realizado com sucesso.")
                return True
            
            else:
                print("Valor informado inválido.")
                return False

        def depositar(self, valor):
            if valor > 0:
                self.saldo += valor
                print("Deposito foi um sucesso.")

            else:
                print("Valor inválido.")
                return False
            
            return True
        
class contaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques = 3):
            super().__init__(numero, cliente)
            self.limite = limite
            self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.
             transacao if transacao ["tipo"] == "Saque"]
        )
        
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques > self.limite_saques

        if excedeu_limite:
            print("Você excedeu o limite.")
        
        elif excedeu_saques:
            print("Excedeu o limite de saques.")

        else:
            return super().sacar(valor)

        return False
        
        def __str__(self):
            return f"""\
                Agência: \t{self.agencia}
                C/C:\t\t{self.numero}
                Titular:\t{self.cliente.nome}
        """
    
class Historico:
    def __init__(self):
        self.transacoes = []
    
    @property
    def transacoes(self):
       return self.transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao._class_._name_,
                "valor": transacao.valor,
                "data": datetime.now().strftime
                ("d%-%m-%yY %H:%M:%s"),
            }
        )
    
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor
    
    def registrar(self, conta):    
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor
    
    def registrar(self, conta):    
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
