class Estudante:
    escola = "DIO"

    def __init__(self, nome , matricula):
        self.nome = nome 
        self.matricula = matricula

    def __str__(self) -> str:
        return f"{self.nome} - {self.matricula} - {self.escola}"
    
def mostrar_valores(*objs):
    for obj in objs:
        print(obj)

aluno1 = Estudante("Juliano", 100)
aluno2 = Estudante("Pedro", 101)

mostrar_valores(aluno1, aluno2)
aluno1.matricula = 1
mostrar_valores(aluno1, aluno2)