def main():
    # Simulação de entrada de dados
    input_data = """Eletrônicos
Celular, 5, 1000
Fone de Ouvido, 10, 500
Móveis
Mesa, 2, 800
Cadeira, 4, 400"""
    
    linhas = input_data.strip().split('\n')
    categorias = {}
    categoria_atual = None

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        if ',' not in linha:
            # Linha sem vírgula é uma categoria
            if categoria_atual is not None:
                # Salva a categoria anterior se houver
                categorias[categoria_atual] = Categoria(categoria_atual)
            # Inicia uma nova categoria
            categoria_atual = linha
            if categoria_atual not in categorias:
                categorias[categoria_atual] = Categoria(categoria_atual)
        else:
            # Linha com vírgula é uma venda
            produto, quantidade, valor = linha.split(',')
            quantidade = int(quantidade.strip())
            valor = float(valor.strip())
            
            venda = Venda(produto.strip(), quantidade, valor)
            categorias[categoria_atual].adicionar_venda(venda)
    
    # Salva a última categoria processada
    if categoria_atual is not None:
        categorias[categoria_atual] = Categoria(categoria_atual)
    
    # Exibindo os totais de vendas para cada categoria
    for nome_categoria, categoria in categorias.items():
        print(f"Vendas em {nome_categoria}: {categoria.total_vendas():.1f}")

if __name__ == "__main__":
    main()
