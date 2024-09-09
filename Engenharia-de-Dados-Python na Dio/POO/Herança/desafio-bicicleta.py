class Bicicleta:
    def __init__(self, cor, modelo, ano, valor):
        self.cor = cor
        self.modelo = modelo
        self.ano = ano
        self.valor = valor

    def buzinar(self):
        print("plim-plim")

    def parar(self):
        print("Parando a bicicleta...")
        print("Bicicleta parada")

    def correr(self):
        print("Vrummmmmmm...")

    def trocar_marcha(self, nro_marcha):
        print("Marcha trocada!")
        def _trocar_marcha():    
            if nro_marcha > self.marcha:
                pass 
                print("Marcha trocada...")   

            else:
                print("Não foi possível mudade de marchar")

    def __str__(self):
        return f"{self.__class__.__name__}: {''.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}"

    # def __str__(self):
       # return f"Bicicletas: {self.cor}, {self.modelo}, {self.ano}, {self.valor}"

b1 = Bicicleta("Vermelha", "GT", 2022, 1200)
b1.buzinar()
b1.correr()
b1.parar()
print(b1.cor, b1.modelo, b1.ano, b1.valor)


b2 = Bicicleta("Verde", "Monarque", 2000, 900)
b2.buzinar()
print (b2)