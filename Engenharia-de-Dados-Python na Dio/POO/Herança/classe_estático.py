class Pessoa:
    def __init__(self, nome=None, idade=None):
        self.nome = nome
        self.idade = idade
    
    #method of Class
    @classmethod
    def apartir_datanascimento(cls, ano, mes, dia, nome):
        print(cls)
        idade = 2024 - ano
        return cls(nome, idade)
#-------------------------------------------------------------
# Method static
    @staticmethod
    def maior_idade(idade):
        return idade >= 18
#-------------------------------------------------------------
    #def apartir_datanascimento(self, ano, mes, dia, nome):
    #    idade = 2024 - ano
    #    return Pessoa(nome, idade)

# p = Pessoa("Guilherme", 28)
# print(p.nome, p.idade)

p = Pessoa.apartir_datanascimento(2005, 7, 13, "Juliano")
print(p.nome, p.idade)

print(Pessoa.maior_idade(18))
print(Pessoa.maior_idade(8))
