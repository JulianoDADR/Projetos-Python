class Veiculo:
    def __init__(self, cor, placa, nmr_rodas):
        self.cor= cor
        self.placa = placa
        self.nmr_rodas = nmr_rodas
    
    def ligar_motor(self):
        print("Ligando motor")

class Motocicleta(Veiculo):
    pass


class Carro(Veiculo):
    pass


class Caminhão(Veiculo):
    pass

moto = Motocicleta("preta", "PMF3232", 32)
print(moto)
moto.ligar_motor()