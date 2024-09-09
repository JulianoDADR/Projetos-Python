from abc import ABC, abstractclassmethod, abstractproperty
# Abstrato

class ControleRemoto(ABC):
    @abstractclassmethod
    def ligar(self):
        pass

    @abstractclassmethod
    def desligar(self):
        pass

# Propriedade
    @property
    @abstractproperty
    def marca(self):
        pass

class ControleTV(ControleRemoto):
    def ligar(self):
        print("Ligando a TV")
        print("Ligada!")

    def desligar(self):
        print("Desligando a TV...")
        print("Desligada!")

    @property
    def marca(self):
        return "LG"
    
class ControleArCondicionado(ControleRemoto):
    def ligar(self):
        print("Ligando o ar condicionado ")
        print("Ligada!")

    def desligar(self):
        print("Desligando o ar condicionado...")
        print("Desligada!")

    @property
    def marca(self):
        return "Samsung"

controleTV = ControleTV()
controleTV.ligar()
controleTV.desligar()
print(controleTV.marca)

controleAR = ControleArCondicionado()
controleAR.ligar()
controleAR.desligar()