import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import json
import os
import csv
import win32print
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from datetime import datetime
import time

# Class responsável por armazenar todos os arquivos que serão utilizados no código
class Config:
    ARQUIVO_HISTORICO = "historico_senhas.json"
    ARQUIVO_CONTADORES = "contadores.json"
    ARQUIVO_LOG = "log_admin.txt"
    ARQUIVO_ESTATISTICAS = "estatisticas.json"  # Novo arquivo para estatísticas detalhadas
    PASTA_BACKUP = "backups"
    SENHA_ADMIN = "admin123"
    SENHA_DELETE = "naouse321"
    TIPOS_SENHA = [
        "CIVEL - FAMILIA",
        "CRIMINAL",
        "JUIZADO - FAZENDA",
        "CÍVEL FÁMILIA PRIORIDADE",
        "CRIMINAL - PRIORIDADE",
        "JUIZADO FAZENDA - PRIORIDADE"
    ]
    SUBTIPOS_JUIZADO = ["JUIZADO CIVEL", "JUIZADO CRIMINAL", "JUIZADO FAZENDA"]
    SUBTIPOS_JUIZADO_PRIORIDADE = ["JUIZADO CIVEL PRIORIDADE", "JUIZADO CRIMINAL PRIORIDADE", "JUIZADO FAZENDA PRIORIDADE"]

# Class responsável por armazenar os logs do sistema
class Logger:
    @staticmethod
    def registrar_log(mensagem):
        """Registra uma mensagem de log com data e hora."""
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        try:
            with open('log.txt', 'a') as file:
                file.write(f"[{data}] {mensagem}\n")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

# Class responsável por salvar os arquivos antigos com os contadores
class Backup:
    @staticmethod
    def fazer_backup():
        if not os.path.exists(Config.PASTA_BACKUP):
            os.makedirs(Config.PASTA_BACKUP)
        agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        for arquivo in [Config.ARQUIVO_HISTORICO, Config.ARQUIVO_CONTADORES, Config.ARQUIVO_ESTATISTICAS]:
            if os.path.exists(arquivo):
                nome_backup = os.path.join(Config.PASTA_BACKUP, f"{arquivo}_{agora}.bak")
                with open(arquivo, "r") as src, open(nome_backup, "w") as dst:
                    dst.write(src.read())

# Class responsável por gerenciar o historico
class HistoricoManager:
    # Função responsável de salvar a nova senha no historico.json
    @staticmethod
    def salvar_historico(senha, tipo, data):
        """
        Salva um novo registro no histórico.

        Args:
            senha (str): Número da senha
            tipo (str): Tipo da senha
            data (str): Data e hora da geração
        """
        try:
            # Obter caminho do arquivo
            arquivo_historico = Config.ARQUIVO_HISTORICO
            print(f"Tentando salvar no histórico: {senha}, {tipo}, {data}")
            print(f"Arquivo: {arquivo_historico}")

            # Carregar histórico existente
            historico = []
            if os.path.exists(arquivo_historico):
                try:
                    with open(arquivo_historico, "r", encoding="utf-8") as f:
                        conteudo = f.read().strip()
                        if conteudo:
                            historico = json.loads(conteudo)
                            if not isinstance(historico, list):
                                historico = []
                    print(f"Histórico carregado: {len(historico)} registros")
                except Exception as e:
                    print(f"Erro ao carregar histórico: {e}")

            # Verificar se a entrada já existe para evitar duplicatas
            entrada_existe = False
            for item in historico:
                if (item.get("senha") == senha and 
                    item.get("tipo") == tipo and 
                    item.get("data") == data):
                    entrada_existe = True
                    break
                
            if entrada_existe:
                print("Aviso: Esta entrada já existe no histórico. Não será adicionada novamente.")
                return True

            # Adicionar novo item
            novo_item = {"senha": senha, "tipo": tipo, "data": data}
            historico.append(novo_item)
            print(f"Novo item adicionado: {novo_item}")

            # Salvar histórico atualizado
            with open(arquivo_historico, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4)

            # Verificar se o arquivo foi salvo corretamente
            if os.path.exists(arquivo_historico):
                tamanho = os.path.getsize(arquivo_historico)
                print(f"Arquivo salvo: {tamanho} bytes")

                # Verificar o conteúdo
                with open(arquivo_historico, "r", encoding="utf-8") as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        dados = json.loads(conteudo)
                        print(f"Verificação: {len(dados)} registros após salvar")
                        if len(dados) > 0:
                            print(f"Último registro: {dados[-1]}")

            print(f"Histórico salvo com sucesso. Total: {len(historico)} registros")
            return True
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Função responsável por retornar informações no historico.json  
    @staticmethod
    def carregar_historico():
        """
        Carrega o histórico do arquivo JSON.
        
        Returns:
            list: Lista de registros do histórico
        """
        if os.path.exists(Config.ARQUIVO_HISTORICO):
            with open(Config.ARQUIVO_HISTORICO, "r") as f:
                try:
                    historico = json.load(f)
                    if isinstance(historico, dict):
                        historico = [historico]
                    return historico
                except:
                    return []
        return []

    @staticmethod
    def filtrar_historico(data_inicio=None, data_fim=None, tipo=None):
        """
        Filtra o histórico por período e tipo de senha.
        """
        # Carrega o histórico diretamente do arquivo
        historico = HistoricoManager.carregar_historico()
        filtrado = []

        # Converter strings de datas para objetos datetime
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y") if data_inicio else None
            data_fim_dt = datetime.strptime(data_fim, "%d/%m/%Y") if data_fim else None
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
            return []

        for item in historico:
            # Filtrar por tipo
            if tipo and tipo.strip() and tipo.lower() not in item['tipo'].lower():
                continue

            # Extrair e converter a data do histórico
            data_str, _ = item["data"].split()  # Separar a data da hora
            try:
                data_item_dt = datetime.strptime(data_str, "%d/%m/%Y")
            except ValueError:
                continue

            # Filtrar por período
            if data_inicio_dt and data_item_dt < data_inicio_dt:
                continue
            if data_fim_dt and data_item_dt > data_fim_dt:
                continue

            filtrado.append(item)

        return filtrado

    @staticmethod
    def exportar_para_csv(dados=None, arquivo=None):
        """
        Exporta o histórico filtrado para um arquivo CSV.
        
        Args:
            dados (list): Lista de registros a exportar (se None, exporta todo o histórico)
            arquivo (str): Caminho do arquivo (se None, abre diálogo para escolher)
            
        Returns:
            bool: True se exportado com sucesso, False caso contrário
        """
        if dados is None:
            dados = HistoricoManager.carregar_historico()
            
        if not dados:
            messagebox.showinfo("Exportar CSV", "Nenhum dado para exportar.")
            return False
            
        if not arquivo:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".csv", 
                filetypes=[("Arquivos CSV", "*.csv")]
            )
            
        if not arquivo:
            return False
            
        try:
            # Agrupar os dados por data e tipo
            dados_agrupados = {}
            
            for item in dados:
                # Extrair a data (sem a hora)
                data, _ = item['data'].split()
                tipo = item['tipo']
                
                # Inicializar a estrutura de dados se necessário
                if data not in dados_agrupados:
                    dados_agrupados[data] = {}
                
                if tipo not in dados_agrupados[data]:
                    dados_agrupados[data][tipo] = []
                
                # Adicionar o item ao grupo correspondente
                dados_agrupados[data][tipo].append(item)
            
            with open(arquivo, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file, delimiter=';')  # Usar ponto e vírgula como delimitador
                
                # Escrever cabeçalho
                writer.writerow(["Data", "Tipo", "Senha", "Hora"])
                
                # Escrever dados agrupados
                for data in sorted(dados_agrupados.keys()):
                    for tipo in sorted(dados_agrupados[data].keys()):
                        for item in dados_agrupados[data][tipo]:
                            _, hora = item['data'].split()
                            writer.writerow([data, tipo, item['senha'], hora])
                            
            messagebox.showinfo("Exportar CSV", "Histórico exportado com sucesso!")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV: {str(e)}")
            return False
    
    @staticmethod
    def exportar_para_pdf(dados=None, arquivo=None):
        """
        Exporta o histórico filtrado para um arquivo PDF, agrupado por dia e tipo,
        com layout em duas colunas para economia de espaço.
        """
        if dados is None:
            dados = HistoricoManager.carregar_historico()

        if not dados:
            messagebox.showinfo("Exportar PDF", "Nenhum dado para exportar.")
            return False

        if not arquivo:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf")]
            )

        if not arquivo:
            return False

        try:
            from fpdf import FPDF

            # Agrupar os dados por data e tipo
            dados_agrupados = {}
            for item in dados:
                # Separar data e tipo
                data, _ = item['data'].split()
                tipo = item['tipo']
                if data not in dados_agrupados:
                    dados_agrupados[data] = {}
                if tipo not in dados_agrupados[data]:
                    dados_agrupados[data][tipo] = []
                dados_agrupados[data][tipo].append(item)

            # Inicializar o PDF
            pdf = FPDF()
            pdf.add_page()

            # Configurações de layout
            left_margin = 10
            right_margin = pdf.w / 2 + 5
            col_width = pdf.w / 2 - 15
            max_y = 270  # Máxima altura por coluna
            row_height = 8

            # Controle de posição
            current_x = left_margin
            current_y = pdf.get_y()

            # Inicia a escrita no documento
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, txt="Histórico de Senhas", ln=True, align="C")
            pdf.ln(5)

            # Escrever dados agrupados
            for data in sorted(dados_agrupados.keys()):
                for tipo in sorted(dados_agrupados[data].keys()):
                    items = dados_agrupados[data][tipo]

                    # Cabeçalhos (Data e Tipo)
                    if current_y + row_height > max_y:
                        if current_x == left_margin:
                            current_x = right_margin  # Mudar para a coluna direita
                            current_y = 30  # Reiniciar no topo da página
                        else:
                            pdf.add_page()  # Mudar para a próxima página
                            current_x = left_margin
                            current_y = 30  # Reiniciar nas coordenadas iniciais esquerda

                    pdf.set_font("Arial", "B", 10)
                    pdf.set_xy(current_x, current_y)
                    pdf.cell(col_width, row_height, txt=f"Data: {data}", ln=True)
                    current_y += row_height

                    pdf.set_xy(current_x, current_y)
                    pdf.cell(col_width, row_height, txt=f"Tipo: {tipo}", ln=True)
                    current_y += row_height

                    # Cabeçalhos da tabela
                    if current_y + row_height > max_y:
                        if current_x == left_margin:
                            current_x = right_margin  # Mover para a coluna direita
                            current_y = 30  # Reiniciar no topo da página
                        else:
                            pdf.add_page()  # Novo layout esquerdo
                            current_x = left_margin
                            current_y = 30  # Começar no topo da nova página

                    pdf.set_xy(current_x, current_y)
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(col_width * 0.4, row_height, txt="Senha", border=1)
                    pdf.cell(col_width * 0.4, row_height, txt="Hora", border=1)
                    current_y += row_height

                    # Dados das senhas
                    pdf.set_font("Arial", size=9)
                    for item in items:
                        if current_y + row_height > max_y:
                            if current_x == left_margin:
                                current_x = right_margin  # Mudar para a coluna direita
                                current_y = 30  # Reiniciar no topo da página
                            else:
                                pdf.add_page()  # Novo layout esquerdo
                                current_x = left_margin
                                current_y = 30

                            # Cabeçalho da tabela novamente na nova coluna ou página
                            pdf.set_xy(current_x, current_y)
                            pdf.set_font("Arial", "B", 9)
                            pdf.cell(col_width * 0.4, row_height, txt="Senha", border=1)
                            pdf.cell(col_width * 0.4, row_height, txt="Hora", border=1)
                            current_y += row_height

                        # Dados do item
                        pdf.set_xy(current_x, current_y)
                        _, hora = item['data'].split()
                        pdf.cell(col_width * 0.4, row_height, txt=item['senha'], border=1)
                        pdf.cell(col_width * 0.4, row_height, txt=hora, border=1)
                        current_y += row_height

                    # Espaço após cada Tipo
                    current_y += 5

            # Salvar o PDF
            pdf.output(arquivo)
            messagebox.showinfo("Exportar PDF", "Histórico exportado com sucesso!")
            return True

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")
            return False

    @staticmethod
    def verificar_alteracao_historico():
        """Verifica se o histórico está sendo alterado corretamente."""
        try:
            arquivo_historico = Config.ARQUIVO_HISTORICO

            # Verificar se o arquivo existe
            if not os.path.exists(arquivo_historico):
                print(f"Arquivo não existe: {arquivo_historico}")
                return False

            # Ler o conteúdo atual
            with open(arquivo_historico, "r", encoding="utf-8") as f:
                conteudo_inicial = f.read()

            # Tentar adicionar um registro de teste
            registro_teste = {
                "senha": "TEST",
                "tipo": "VERIFICACAO",
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            # Carregar o histórico
            historico = []
            if conteudo_inicial.strip():
                historico = json.loads(conteudo_inicial)
                if not isinstance(historico, list):
                    historico = []

            # Adicionar registro de teste
            historico.append(registro_teste)

            # Salvar o histórico
            with open(arquivo_historico, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4)

            # Ler o conteúdo após a alteração
            with open(arquivo_historico, "r", encoding="utf-8") as f:
                conteudo_final = f.read()

            # Verificar se houve alteração
            alterado = conteudo_inicial != conteudo_final
            print(f"Verificação de alteração: {'Sucesso' if alterado else 'Falha'}")

            # Restaurar o conteúdo original
            with open(arquivo_historico, "w", encoding="utf-8") as f:
                f.write(conteudo_inicial)

            return alterado
        except Exception as e:
            print(f"Erro na verificação: {e}")
            return False

    @staticmethod
    def criar_novo_arquivo_historico():
        """Cria um novo arquivo de histórico, fazendo backup do anterior."""
        try:
            arquivo_historico = Config.ARQUIVO_HISTORICO
            
            # Criar backup do arquivo existente
            if os.path.exists(arquivo_historico):
                # Obter data e hora para o nome do backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                arquivo_backup = f"{arquivo_historico}.{timestamp}.bak"
                
                # Copiar o arquivo para o backup
                import shutil
                shutil.copy2(arquivo_historico, arquivo_backup)
                print(f"Backup criado: {arquivo_backup}")
            
            # Criar novo arquivo vazio
            with open(arquivo_historico, "w", encoding="utf-8") as f:
                f.write("[]")
            
            print(f"Novo arquivo de histórico criado: {arquivo_historico}")
            return True
        except Exception as e:
            print(f"Erro ao criar novo arquivo: {e}")
            return False


class EstatisticasManager:
    @staticmethod
    def carregar_estatisticas():
        if os.path.exists(Config.ARQUIVO_ESTATISTICAS):
            with open(Config.ARQUIVO_ESTATISTICAS, "r") as f:
                try:
                    return json.load(f)
                except:
                    return {
                        "CIVEL": 0, "FAMILIA": 0, "CRIMINAL": 0, "CRIMINAL PRIORIDADE": 0,
                        "JUIZADO CIVEL": 0, "JUIZADO CRIMINAL": 0, "JUIZADO FAZENDA": 0,
                        "JUIZADO CIVEL PRIORIDADE": 0, "JUIZADO CRIMINAL PRIORIDADE": 0, "JUIZADO FAZENDA PRIORIDADE": 0
                    }
        else:
            estatisticas_iniciais = {
                "CIVEL": 0, "FAMILIA": 0, "CRIMINAL": 0, "CRIMINAL PRIORIDADE": 0,
                "JUIZADO CIVEL": 0, "JUIZADO CRIMINAL": 0, "JUIZADO FAZENDA": 0,
                "JUIZADO CIVEL PRIORIDADE": 0, "JUIZADO CRIMINAL PRIORIDADE": 0, "JUIZADO FAZENDA PRIORIDADE": 0
            }
            with open(Config.ARQUIVO_ESTATISTICAS, "w") as f:
                json.dump(estatisticas_iniciais, f)
            return estatisticas_iniciais     
        
    @staticmethod
    def salvar_estatisticas(estatisticas):
        with open(Config.ARQUIVO_ESTATISTICAS, "w") as f:
            json.dump(estatisticas, f, indent=4)
    
    @staticmethod
    def incrementar_estatistica(tipo):
        estatisticas = EstatisticasManager.carregar_estatisticas()
        if tipo in estatisticas:
            estatisticas[tipo] += 1
        else:
            estatisticas[tipo] = 1
        EstatisticasManager.salvar_estatisticas(estatisticas)

        return estatisticas[tipo]

    @staticmethod
    def resetar_estatisticas():
        """Reseta todas as estatísticas para zero."""
        estatisticas = {}
        try:
            with open('estatisticas.json', 'w') as file:
                json.dump(estatisticas, file)
            return True
        except Exception as e:
            print(f"Erro ao resetar estatísticas: {e}")
            return False


class ContadorManager:
    def __init__(self):
        self.counters = self.carregar_contadores()

    def carregar_contadores(self):
        try:
            with open('contadores.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Configura contadores agrupados
            return {
                'CIVEL - FAMILIA': 0,
                'CIVEL - FAMILIA PRIORIDADE': 0,
                'JUIZADO': 0,
                'JUIZADO PRIORIDADE': 0,
                'CRIMINAL': 0,
                'CRIMINAL PRIORIDADE': 0
            }

    def salvar_contadores(self):
        with open('contadores.json', 'w') as file:
            json.dump(self.counters, file)

    def incrementar_contador(self, grupo):
        """Incrementa o contador para um grupo específico."""
        if grupo not in self.counters:
            self.counters[grupo] = 0
        self.counters[grupo] += 1
        self.salvar_contadores()
        return self.counters[grupo]

    def resetar_contadores(self):
        """Reseta todos os contadores para zero."""
        self.counters = {}
        self.salvar_contadores()
        return True


class ImpressaoManager:

    @staticmethod
    def criar_imagem_impressao(senha, tipo, data):
        """
        Cria uma imagem para impressão da senha.
        
        Returns:
            Image: Objeto PIL Image contendo a senha formatada
        """
        try:
            # Definir o tamanho da etiqueta em pixels (10cm x 6cm @ 203 DPI)
            largura_pixels = int(10 * 203)  # 10cm em 203 DPI
            altura_pixels = int(6 * 203)    # 6cm em 203 DPI
    
            # Criar imagem branca
            img = Image.new('RGB', (largura_pixels, altura_pixels), 'white')
            draw = ImageDraw.Draw(img)
    
            # Carregar a fonte
            font_path = os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'Arial.ttf')
            if not os.path.exists(font_path):
                # Tentar encontrar fontes alternativas
                fontes_alternativas = [
                    os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'Calibri.ttf'),
                    os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'Tahoma.ttf'),
                    os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'Verdana.ttf')
                ]
                
                for fonte in fontes_alternativas:
                    if os.path.exists(fonte):
                        font_path = fonte
                        break
                else:
                    raise FileNotFoundError("Nenhuma fonte compatível encontrada.")
    
            font_titulo = ImageFont.truetype(font_path, 110)  # Para "SENHA GERADA"
            font_senha = ImageFont.truetype(font_path, 240)   # Para "SENHA: {senha}"
            font_info = ImageFont.truetype(font_path, 100)    # Para "TIPO" e "DATA/HORA"
    
            # Configurar o texto
            textos = [
                "===============================",
                "         SENHA GERADA         ",
                "",
                f"  SENHA: {senha}",
                f"  TIPO: {tipo}",
                f"  DATA/HORA: {data}",
                "==============================="
            ]
    
            # Calcular altura total dos textos
            espacamento = 10  # Espaço entre linhas
            altura_total = sum(
                [draw.textbbox((0, 0), linha, font=font_titulo if i in [0, 1, 6] else (font_senha if i == 3 else font_info))[3]
                 + espacamento for i, linha in enumerate(textos)]
            )
    
            # Posição inicial no eixo Y para centralizar verticalmente
            y = (altura_pixels - altura_total) // 2
    
            # Desenhar cada linha centralizada
            for i, linha in enumerate(textos):
                fonte = (
                    font_titulo if i in [0, 1, 6] else
                    font_senha if i == 3 else
                    font_info
                )
                largura_texto = draw.textbbox((0, 0), linha, font=fonte)[2]
                x = (largura_pixels - largura_texto) // 2
                draw.text((x, y), linha, font=fonte, fill='black')
                y += draw.textbbox((0, 0), linha, font=fonte)[3] + espacamento
    
            return img
        except Exception as e:
            print(f"Erro ao criar imagem: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def imprimir_senha_termica(senha, tipo, data, impressora):
        """
        Impressão direta da imagem gerada.
        
        Args:
            senha (str): Número da senha
            tipo (str): Tipo da senha
            data (str): Data e hora da geração
            impressora (str): Nome da impressora
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        try:
            print(f"Iniciando impressão para: {impressora}")
            
            # Criar a imagem
            img = ImpressaoManager.criar_imagem_impressao(senha, tipo, data)
            
            if img is None:
                print("Falha ao criar imagem para impressão")
                return False
            
            # Salvar a imagem em um arquivo temporário
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_img_path = os.path.join(temp_dir, f"senha_{senha}_{int(time.time())}.png")
            img.save(temp_img_path)
            print(f"Imagem salva em: {temp_img_path}")
            
            # Salvar a imagem para verificação (debug)
            debug_path = os.path.join(os.path.expanduser("~"), "Desktop", "senha_debug.png")
            img.save(debug_path)
            print(f"Imagem de debug salva em: {debug_path}")
            
            # Verificar se é o Microsoft Print to PDF
            if "Microsoft Print to PDF" in impressora:
                print("Detectado Microsoft Print to PDF - usando método alternativo")
                return ImpressaoManager.imprimir_pdf(temp_img_path, impressora)
            
            # Usar o método padrão para outras impressoras
            import win32print
            import win32ui
            from PIL import ImageWin
            
            # Obter o identificador (handle) da impressora
            hprinter = win32print.OpenPrinter(impressora)
            
            # Configurar o documento
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(impressora)
            
            # Iniciar o documento
            pdc.StartDoc("Impressão de Senha")
            pdc.StartPage()
            
            # Pegar o DC (Device Context) para desenhar
            hdc = pdc.GetSafeHdc()
            
            # Configurar o modo de impressão para preservar a imagem completa
            dib = ImageWin.Dib(img)
            
            # Obter as dimensões da impressora em pixels
            largura_impressora = pdc.GetDeviceCaps(110)  # PHYSICALWIDTH 
            altura_impressora = pdc.GetDeviceCaps(111)   # PHYSICALHEIGHT
            
            # Desenhar a imagem mantendo a proporção e escalando para o tamanho desejado
            dib.draw(hdc, (0, 0, largura_impressora, altura_impressora))
            
            # Finalizar a página e o documento
            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()
            win32print.ClosePrinter(hprinter)
            
            print(f"Impressão concluída com sucesso para: {impressora}")
            return True
        
        except Exception as e:
            print(f"Erro ao imprimir: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Falha ao imprimir: {str(e)}")
            return False
    
    @staticmethod
    def imprimir_pdf(imagem_path, impressora):
        """
        Método alternativo para imprimir usando Microsoft Print to PDF.
        
        Args:
            imagem_path (str): Caminho para a imagem a ser impressa
            impressora (str): Nome da impressora (Microsoft Print to PDF)
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        try:
            print(f"Usando método alternativo para PDF com imagem: {imagem_path}")
            
            # Abrir um diálogo para salvar o PDF
            from tkinter import filedialog
            pdf_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf")],
                title="Salvar senha como PDF"
            )
            
            if not pdf_path:
                print("Operação cancelada pelo usuário")
                return False
            
            print(f"Salvando PDF em: {pdf_path}")
            
            # Usar reportlab para criar um PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Criar o PDF
            c = canvas.Canvas(pdf_path, pagesize=letter)
            
            # Obter dimensões da página
            width, height = letter
            
            # Carregar a imagem
            img = Image.open(imagem_path)
            img_width, img_height = img.size
            
            # Calcular proporção para manter o aspecto
            aspect = img_width / img_height
            
            # Definir tamanho máximo na página (80% da largura/altura)
            max_width = width * 0.8
            max_height = height * 0.8
            
            # Calcular dimensões finais mantendo a proporção
            if img_width / max_width > img_height / max_height:
                # Limitado pela largura
                new_width = max_width
                new_height = new_width / aspect
            else:
                # Limitado pela altura
                new_height = max_height
                new_width = new_height * aspect
            
            # Posicionar a imagem centralizada na página
            x = (width - new_width) / 2
            y = (height - new_height) / 2
            
            # Adicionar a imagem ao PDF
            c.drawImage(imagem_path, x, y, width=new_width, height=new_height)
            
            # Finalizar o PDF
            c.save()
            
            print(f"PDF criado com sucesso: {pdf_path}")
            messagebox.showinfo("Sucesso", f"PDF criado com sucesso:\n{pdf_path}")
            return True
            
        except Exception as e:
            print(f"Erro ao criar PDF: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Falha ao criar PDF: {str(e)}")
            return False


class GeradorSenha:

    def __init__(self):
        self.contador_manager = ContadorManager()
        EstatisticasManager.carregar_estatisticas()
            
    def gerar_senha(self, tipo):
        EstatisticasManager.carregar_estatisticas
        """Gera uma senha com base no tipo especificado."""
        # Mapeamento de tipos específicos para grupos de contadores
        mapa_grupos = {
            'CIVEL': 'CIVEL - FAMILIA',
            'FAMILIA': 'CIVEL - FAMILIA',
            'CIVEL PRIORIDADE': 'CIVEL - FAMILIA PRIORIDADE',
            'FAMILIA PRIORIDADE': 'CIVEL - FAMILIA PRIORIDADE',
            'CRIMINAL': 'CRIMINAL',
            'CRIMINAL PRIORIDADE': 'CRIMINAL PRIORIDADE',
            'JUIZADO CIVEL': 'JUIZADO - FAZENDA',
            'JUIZADO CRIMINAL': 'JUIZADO - FAZENDA',
            'FAZENDA': 'JUIZADO - FAZENDA',
        }
        
        # Determinar qual grupo de contador usar
        grupo_contador = mapa_grupos.get(tipo, tipo)
        
        # Incrementar o contador do grupo
        contador = self.contador_manager.incrementar_contador(grupo_contador)


        # Formatar a senha
        senha_formatada = f"{contador:03d}"  # Formato: 001, 002, etc.
        
        # Data e hora atual
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Retornar a senha, o tipo original e a data/hora
        return senha_formatada, tipo, data_hora
    
    def gerar_senha_juizado(self):
        """Gera uma senha para um subtipo de JUIZADO."""
        subtipo = None

        # Criar janela para selecionar o subtipo
        def selecionar_subtipo(tipo):
            nonlocal subtipo
            subtipo = tipo
            dialogo.destroy()

        dialogo = tk.Toplevel(self.root)
        dialogo.title("Selecione o Subtipo")
        tk.Label(dialogo, text="Escolha entre os tipos de JUIZADO:", font=("Arial", 14)).pack(pady=10)

        tk.Button(dialogo, text="CIVEL", font=("Arial", 12), command=lambda: selecionar_subtipo('JUIZADO CIVEL')).pack(pady=5)
        tk.Button(dialogo, text="CRIMINAL", font=("Arial", 12), command=lambda: selecionar_subtipo('JUIZADO CRIMINAL')).pack(pady=5)
        tk.Button(dialogo, text="FAZENDA", font=("Arial", 12), command=lambda: selecionar_subtipo('JUIZADO FAZENDA')).pack(pady=5)

        dialogo.wait_window()

        if subtipo:
            # Contador geral para "JUIZADO"
            senha = self.gerador_senha.gerar_senha("JUIZADO")
            tipo_impressao = "JUIZADO"  # Nome genérico para impressão
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Exibir a senha gerada
            self.exibir_senha_gerada(senha, tipo_impressao, data)

            # Registrar no histórico com o subtipo específico
            HistoricoManager.adicionar_entrada(senha, subtipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()

            # Perguntar e imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressora = "Nome da Impressora"
                ImpressaoManager.imprimir_senha_termica(senha, tipo_impressao, data, impressora)

    def gerar_senha_juizado_fazenda(self, prioridade=False):
        """
        Gera uma senha de JUIZADO - FAZENDA, permitindo escolher entre CIVEL, CRIMINAL ou FAZENDA.

        Args:
            prioridade (bool): Se True, gera uma senha com prioridade.
        """
        # Criar uma janela de diálogo para escolher o tipo de JUIZADO
        subtipo_dialogo = tk.Toplevel(self.root)
        titulo = "Tipo de JUIZADO" if not prioridade else "Tipo de JUIZADO COM PRIORIDADE"
        subtipo_dialogo.title(titulo)
        subtipo_dialogo.geometry("400x200")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        texto_instrucao = "Selecione o tipo de JUIZADO:" if not prioridade else "Selecione o tipo de JUIZADO COM PRIORIDADE:"
        tk.Label(subtipo_dialogo, text=texto_instrucao, 
                font=("Arial", 12, "bold")).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Cor dos botões (diferente para prioridade)
        cor_botao = "#FF5722" if prioridade else "#4CAF50"

        # Botões para escolher o subtipo - USANDO STRINGS SIMPLES
        tk.Button(frame_subtipo, text="JUIZADO CIVEL", font=("Arial", 12, "bold"),
                 bg=cor_botao, fg="white", width=20,
                 command=lambda: confirmar_subtipo("JUIZADO CIVEL")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="JUIZADO CRIMINAL", font=("Arial", 12, "bold"),
                 bg=cor_botao, fg="white", width=20,
                 command=lambda: confirmar_subtipo("JUIZADO CRIMINAL")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="JUIZADO FAZENDA", font=("Arial", 12, "bold"),
                 bg=cor_botao, fg="white", width=20,
                 command=lambda: confirmar_subtipo("JUIZADO FAZENDA")).pack(side=tk.TOP, pady=5)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]

            # Adicionar texto de prioridade se necessário
            if prioridade:
                subtipo = subtipo + " PRIORIDADE"

            # Incrementar o contador
            contador_tipo = "JUIZADO - FAZENDA" if not prioridade else "JUIZADO FAZENDA - PRIORIDADE"
            contador = self.contador_manager.incrementar_contador(contador_tipo)

            # Formatar a senha
            senha = f"{contador:03d}"

            # Obter a data e hora atual
            data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Exibir a senha gerada
            self.exibir_senha_gerada(senha, subtipo, data)

            # Salvar no histórico
            HistoricoManager.salvar_historico(senha, subtipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()

            # Atualizar o histórico recente
            self.atualizar_historico_recente()

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, subtipo, data, impressora)

            return senha, subtipo, data

        return None, None, None

    def gerar_senha_civel_familia(self):
        """Gera uma senha para CIVEL - FAMILIA."""
        # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Escolha o Subtipo")
        subtipo_dialogo.geometry("300x150")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Esta senha é de CÍVEL ou FAMÍLIA?", 
                font=("Arial", 12)).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="CIVEL", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("CIVEL")).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_subtipo, text="FAMILIA", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("FAMILIA")).pack(side=tk.LEFT, padx=10)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]

            # Gerar a senha usando o subtipo específico
            senha, tipo_original, data = self.gerador_senha.gerar_senha(subtipo)

            # Para exibição e impressão, usar "CIVEL - FAMILIA"
            tipo_exibicao = "CIVEL - FAMILIA"

            # Exibir a senha gerada com o tipo de exibição
            self.exibir_senha_gerada(senha, tipo_exibicao, data)

            # Atualizar estatísticas com o subtipo original
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()

            # Registrar no histórico com o subtipo original
            HistoricoManager.adicionar_entrada(senha, subtipo, data)

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    # Imprimir com o tipo de exibição (genérico)
                    ImpressaoManager.imprimir_senha_termica(senha, tipo_exibicao, data, impressora)


class SistemaGeradorSenhasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gerador de Senhas")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.gerador_senha = GeradorSenha()
        self.contadores = self.gerador_senha.contador_manager.counters

        # Variável para controlar a opção de impressão
        self.imprimir_var = tk.BooleanVar(value=True)

        # Primeiro, criar a interface
        self.criar_interface()


        # Depois, atualizar estatísticas, contadores e histórico
        self.atualizar_estatisticas()
        self.atualizar_contadores()
        self.atualizar_historico_recente()        

    def gerar_senha_civel_familia(self):
        """Gera uma senha para CIVEL - FAMILIA."""
        # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Escolha o Subtipo")
        subtipo_dialogo.geometry("300x150")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Esta senha é de CÍVEL ou FAMÍLIA?", 
                font=("Arial", 12)).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="CIVEL", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("CIVEL")).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_subtipo, text="FAMILIA", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("FAMILIA")).pack(side=tk.LEFT, padx=10)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]
            # Usar o método gerar_senha com o tipo para contador e o subtipo para histórico
            self.gerar_senha("CIVEL - FAMILIA", subtipo)

    def gerar_senha_civel_familia_prioridade(self):
        """
        Gera uma senha do tipo CIVEL PRIORIDADE ou FAMILIA PRIORIDADE após o usuário escolher.
        Exibe um diálogo para o usuário escolher o tipo específico.
        """
        # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Escolha o Tipo com Prioridade")
        dialogo.geometry("300x150")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)  # Torna a janela dependente da janela principal
        dialogo.grab_set()  # Torna a janela modal

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        dialogo.geometry(f"+{x}+{y}")

        # Label de instrução
        tk.Label(dialogo, text="Selecione o tipo específico:", 
                 font=("Arial", 12)).pack(pady=10)

        # Função para gerar a senha com o tipo escolhido
        def confirmar_tipo(tipo_especifico):
            # Fechar o diálogo
            dialogo.destroy()
            # Gerar a senha normalmente (usando "CÍVEL FÁMILIA PRIORIDADE" como tipo visual)
            # Mas registrando o tipo específico com PRIORIDADE no histórico
            self.gerar_senha("CÍVEL FÁMILIA PRIORIDADE", f"{tipo_especifico} PRIORIDADE")
            self.incrementar_contador(tipo_especifico)
            self.incrementar_estatistica(tipo_especifico)
            # Frame para os botões
        frame_botoes = tk.Frame(dialogo)
        frame_botoes.pack(pady=10)

        # Botões para escolher o tipo específico
        tk.Button(frame_botoes, text="CIVEL", font=("Arial", 12, "bold"),
                  bg="#9C27B0", fg="white", width=10,
                  command=lambda: confirmar_tipo("CIVEL")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="FAMILIA", font=("Arial", 12, "bold"),
                  bg="#9C27B0", fg="white", width=10,
                  command=lambda: confirmar_tipo("FAMILIA")).pack(side=tk.LEFT, padx=10)

    def gerar_senha(self, tipo, tipo_historico=None):
            """
            Gera uma nova senha do tipo especificado.

            Args:
                tipo (str): Tipo de senha a ser gerada (para exibição e contador)
                tipo_historico (str, optional): Tipo específico para salvar no histórico
            """
            try:
                print(f"\n--- GERANDO NOVA SENHA ---")
                print(f"Tipo: {tipo}")

                # Incrementar o contador para o tipo
                contador = self.gerador_senha.contador_manager.incrementar_contador(tipo)
                print(f"Contador: {contador}")

                # Formatar a senha (com zeros à esquerda)
                senha = f"{contador:03d}"
                print(f"Senha formatada: {senha}")

                # Obter a data e hora atual
                agora = datetime.now()
                data_hora = agora.strftime("%d/%m/%Y %H:%M:%S")
                print(f"Data/hora: {data_hora}")

                # Determinar o tipo a ser salvo no histórico
                tipo_para_historico = tipo_historico if tipo_historico else tipo
                print(f"Tipo para histórico: {tipo_para_historico}")

                # Registrar no histórico - PONTO CRÍTICO
                print("Salvando no histórico...")

                # Verificar se o histórico pode ser alterado
                if not hasattr(self, '_verificacao_historico_feita'):
                    pode_alterar = HistoricoManager.verificar_alteracao_historico()
                    self._verificacao_historico_feita = True

                    if not pode_alterar:
                        print("AVISO: O arquivo de histórico não pode ser alterado!")
                        resposta = messagebox.askyesno(
                            "Problema no Histórico", 
                            "O sistema detectou que o arquivo de histórico não pode ser alterado.\n\n"
                            "Deseja criar um novo arquivo de histórico?\n"
                            "(Um backup do arquivo atual será criado)"
                        )
                        if resposta:
                            HistoricoManager.criar_novo_arquivo_historico()

                # Tentar salvar no histórico
                sucesso = HistoricoManager.salvar_historico(senha, tipo_para_historico, data_hora)
                print(f"Resultado: {'Sucesso' if sucesso else 'Falha'}")

                # Atualizar estatísticas
                if tipo_historico in ["CIVEL", "FAMILIA"]:
                    EstatisticasManager.incrementar_estatistica(tipo_historico)
                    self.atualizar_estatisticas()
                    

                # Atualizar a interface
                self.senha_label.config(text=senha)
                self.tipo_label.config(text=tipo)  # Exibe o tipo original na interface

                # Atualizar o histórico recente
                if hasattr(self, 'historico_lista'):
                    self.atualizar_historico_recente()
                else:
                    print("Aviso: Componente historico_lista não encontrado")

                # Imprimir a senha se a opção estiver ativada
                if self.imprimir_var.get():
                    # Perguntar se deseja imprimir
                    deseja_imprimir = messagebox.askyesno("Impressão", "Deseja imprimir a senha?")
                    if deseja_imprimir:
                        # Obter lista de impressoras disponíveis
                        impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]

                        # Criar diálogo para seleção de impressora
                        impressora_selecionada = self.selecionar_impressora(impressoras)

                        if impressora_selecionada:
                            # Usar o tipo original para impressão (não o tipo_historico)
                            sucesso = ImpressaoManager.imprimir_senha_termica(senha, tipo, data_hora, impressora_selecionada)
                            if sucesso:
                                messagebox.showinfo("Impressão", "Senha impressa com sucesso!")
                            else:
                                messagebox.showerror("Impressão", "Falha ao imprimir a senha.")

                print("--- SENHA GERADA COM SUCESSO ---\n")
                return senha
            except Exception as e:
                print(f"Erro ao gerar senha: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erro", f"Falha ao gerar senha: {e}")
                return None
            
    def gerar_senha_juizado_fazenda(self):
        """Gera uma senha de JUIZADO - FAZENDA."""
        senha, tipo, data = self.gerador_senha.gerar_senha_juizado_fazenda(prioridade=False)
        if senha:
            self.exibir_senha_gerada(senha, tipo, data)
            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)
    
    def gerar_senha_juizado_fazenda_prioridade(self):
        """Gera uma senha de JUIZADO - FAZENDA com prioridade."""
        senha, tipo, data = self.gerador_senha.gerar_senha_juizado_fazenda(prioridade=True)
        if senha:
            self.exibir_senha_gerada(senha, tipo, data)
            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)
       
    def gerar_senha_civel_familia(self):
        """Gera uma senha para CIVEL - FAMILIA."""
        # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Escolha o Subtipo")
        subtipo_dialogo.geometry("300x150")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Esta senha é de CÍVEL ou FAMÍLIA?", 
                font=("Arial", 12)).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="CIVEL", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("CIVEL")).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_subtipo, text="FAMILIA", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=10,
                 command=lambda: confirmar_subtipo("FAMILIA")).pack(side=tk.LEFT, padx=10)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]
            senha, tipo, data = self.gerador_senha.gerar_senha(subtipo)
            self.exibir_senha_gerada(senha, tipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()
            HistoricoManager.salvar_historico(senha, tipo, data)

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)

    def gerar_senha_civel_familia_prioridade(self):
        """Gera uma senha para CIVEL - FAMILIA com prioridade."""
        # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Escolha o Subtipo com Prioridade")
        subtipo_dialogo.geometry("300x150")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Esta senha é de CÍVEL ou FAMÍLIA?", 
                font=("Arial", 12)).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="CIVEL", font=("Arial", 12, "bold"),
                 bg="#9C27B0", fg="white", width=10,
                 command=lambda: confirmar_subtipo("CIVEL PRIORIDADE")).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_subtipo, text="FAMILIA", font=("Arial", 12, "bold"),
                 bg="#9C27B0", fg="white", width=10,
                 command=lambda: confirmar_subtipo("FAMILIA PRIORIDADE")).pack(side=tk.LEFT, padx=10)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]
            senha, tipo, data = self.gerador_senha.gerar_senha(subtipo)
            self.exibir_senha_gerada(senha, tipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()
            HistoricoManager.salvar_historico(senha, tipo, data)

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)

    def gerar_senha_criminal(self):
        """Gera uma senha para CRIMINAL."""
        senha, tipo, data = self.gerador_senha.gerar_senha("CRIMINAL")
        self.exibir_senha_gerada(senha, tipo, data)

        # Atualizar estatísticas
        EstatisticasManager.incrementar_estatistica(tipo)
        self.atualizar_estatisticas()
        HistoricoManager.salvar_historico(senha, tipo, data)

        # Perguntar se deseja imprimir
        if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
            impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            impressora = self.selecionar_impressora(impressoras)
            if impressora:
                ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)

    def gerar_senha_criminal_prioridade(self):
        """Gera uma senha para CRIMINAL com prioridade."""
        senha, tipo, data = self.gerador_senha.gerar_senha("CRIMINAL - PRIORIDADE")
        self.exibir_senha_gerada(senha, tipo, data)

        # Atualizar estatísticas
        EstatisticasManager.incrementar_estatistica("CRIMINAL - PRIORIDADE")
        self.atualizar_estatisticas()
        HistoricoManager.salvar_historico(senha, tipo, data)

        # Perguntar se deseja imprimir
        if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
            impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            impressora = self.selecionar_impressora(impressoras)
            if impressora:
                ImpressaoManager.imprimir_senha_termica(senha, tipo, data, impressora)
        
    def gerar_senha_juizado_fazenda(self):
        """Gera uma senha para JUIZADO - FAZENDA."""
        # Criar uma janela de diálogo para escolher o tipo de JUIZADO
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Tipo de JUIZADO")
        subtipo_dialogo.geometry("400x200")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Selecione o tipo de JUIZADO:", 
                font=("Arial", 12, "bold")).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="JUIZADO CIVEL", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=20,
                 command=lambda: confirmar_subtipo("JUIZADO CIVEL")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="JUIZADO CRIMINAL", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=20,
                 command=lambda: confirmar_subtipo("JUIZADO CRIMINAL")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="FAZENDA", font=("Arial", 12, "bold"),
                 bg="#4CAF50", fg="white", width=20,
                 command=lambda: confirmar_subtipo("FAZENDA")).pack(side=tk.TOP, pady=5)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]
            senha, tipo, data = self.gerador_senha.gerar_senha("FAZENDA")
            self.exibir_senha_gerada(senha, subtipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()
            HistoricoManager.salvar_historico(senha, subtipo, data)

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, subtipo, data, impressora)

    def gerar_senha_juizado_fazenda_prioridade(self):
        """Gera uma senha para JUIZADO - FAZENDA com prioridade."""
        # Criar uma janela de diálogo para escolher o tipo de JUIZADO
        subtipo_dialogo = tk.Toplevel(self.root)
        subtipo_dialogo.title("Tipo de JUIZADO COM PRIORIDADE")
        subtipo_dialogo.geometry("400x200")
        subtipo_dialogo.resizable(False, False)
        subtipo_dialogo.transient(self.root)
        subtipo_dialogo.grab_set()

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        subtipo_dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o subtipo
        subtipo_resultado = [None]

        # Label de instrução
        tk.Label(subtipo_dialogo, text="Selecione o tipo de JUIZADO COM PRIORIDADE:", 
                font=("Arial", 12, "bold")).pack(pady=10)

        # Função para confirmar o subtipo
        def confirmar_subtipo(subtipo):
            subtipo_resultado[0] = subtipo
            subtipo_dialogo.destroy()

        # Frame para os botões
        frame_subtipo = tk.Frame(subtipo_dialogo)
        frame_subtipo.pack(pady=10)

        # Botões para escolher o subtipo
        tk.Button(frame_subtipo, text="JUIZADO CIVEL PRIORIDADE", font=("Arial", 12, "bold"),
                 bg="#FF5722", fg="white", width=25,
                 command=lambda: confirmar_subtipo("JUIZADO CIVEL PRIORIDADE")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="JUIZADO CRIMINAL PRIORIDADE", font=("Arial", 12, "bold"),
                 bg="#FF5722", fg="white", width=25,
                 command=lambda: confirmar_subtipo("JUIZADO CRIMINAL PRIORIDADE")).pack(side=tk.TOP, pady=5)

        tk.Button(frame_subtipo, text="FAZENDA PRIORIDADE", font=("Arial", 12, "bold"),
                 bg="#FF5722", fg="white", width=25,
                 command=lambda: confirmar_subtipo("FAZENDA PRIORIDADE")).pack(side=tk.TOP, pady=5)

        # Aguardar até que o diálogo seja fechado
        subtipo_dialogo.wait_window()

        # Se o usuário selecionou um subtipo
        if subtipo_resultado[0]:
            subtipo = subtipo_resultado[0]
            senha, tipo, data = self.gerador_senha.gerar_senha("FAZENDA - PRIORIDADE")
            self.exibir_senha_gerada(senha, subtipo, data)

            # Atualizar estatísticas
            EstatisticasManager.incrementar_estatistica(subtipo)
            self.atualizar_estatisticas()
            HistoricoManager.salvar_historico(senha, subtipo, data)

            # Perguntar se deseja imprimir
            if messagebox.askyesno("Impressão", "Deseja imprimir a senha?"):
                impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                impressora = self.selecionar_impressora(impressoras)
                if impressora:
                    ImpressaoManager.imprimir_senha_termica(senha, subtipo, data, impressora)    

    def criar_interface(self):
        """Cria a interface gráfica do sistema."""
        # Configurar a janela principal
        self.root.title("Sistema Gerador de Senhas")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)

        # Frame principal
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame para o título
        frame_titulo = tk.Frame(frame_principal)
        frame_titulo.pack(fill=tk.X, pady=10)

        # Título
        titulo_label = tk.Label(frame_titulo, text="SISTEMA GERADOR DE SENHAS", font=("Arial", 20, "bold"))
        titulo_label.pack()

        # Subtítulo
        subtitulo_label = tk.Label(frame_titulo, text="Selecione o tipo de senha", font=("Arial", 14))
        subtitulo_label.pack(pady=5)

        # Frame para os botões e estatísticas
        frame_conteudo = tk.Frame(frame_principal)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame para os botões
        frame_botoes = tk.Frame(frame_conteudo)
        frame_botoes.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Botão CIVEL - FAMILIA
        botao_civel_familia = tk.Button(frame_botoes, text="CIVEL - FAMILIA", font=("Arial", 14, "bold"),
                                      bg="#00FF00", fg="white", width=15, height=2,
                                      command=self.gerar_senha_civel_familia)
        botao_civel_familia.pack(side=tk.TOP, pady=5)

        # Botão CIVEL - FAMILIA PRIORIDADE
        botao_civel_familia_prioridade = tk.Button(frame_botoes, text="CIVEL - FAMILIA\nPRIORIDADE", 
                                                 font=("Arial", 14, "bold"),
                                                 bg="#006400", fg="white", width=15, height=2,
                                                 command=self.gerar_senha_civel_familia_prioridade)
        botao_civel_familia_prioridade.pack(side=tk.TOP, pady=5)

        # Botão CRIMINAL
        botao_criminal = tk.Button(frame_botoes, text="CRIMINAL", font=("Arial", 14, "bold"),
                                  bg="#0000FF", fg="white", width=15, height=2,
                                  command=self.gerar_senha_criminal)
        botao_criminal.pack(side=tk.TOP, pady=5)

        # Botão CRIMINAL - PRIORIDADE
        botao_criminal_prioridade = tk.Button(frame_botoes, text="CRIMINAL\nPRIORIDADE", 
                                            font=("Arial", 14, "bold"),
                                            bg="#00008B", fg="white", width=15, height=2,
                                            command=self.gerar_senha_criminal_prioridade)
        botao_criminal_prioridade.pack(side=tk.TOP, pady=5)

        # Botão JUIZADO - FAZENDA
        botao_juizado_fazenda = tk.Button(frame_botoes, text="JUIZADO - FAZENDA", font=("Arial", 14, "bold"),
                                         bg="#FFA500", fg="white", width=15, height=2,
                                         command=self.gerar_senha_juizado_fazenda)
        botao_juizado_fazenda.pack(side=tk.TOP, pady=5)

        # Botão JUIZADO - FAZENDA PRIORIDADE
        botao_juizado_fazenda_prioridade = tk.Button(frame_botoes, text="JUIZADO - FAZENDA\nPRIORIDADE", 
                                                   font=("Arial", 14, "bold"),
                                                   bg="#FF5722", fg="white", width=15, height=2,
                                                   command=self.gerar_senha_juizado_fazenda_prioridade)
        botao_juizado_fazenda_prioridade.pack(side=tk.TOP, pady=5)

        # Frame central para exibir a senha gerada
        self.frame_senha_gerada = tk.Frame(frame_conteudo, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        self.frame_senha_gerada.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Label para instruções
        self.instrucao_label = tk.Label(self.frame_senha_gerada, 
                                       text="Clique em um botão para gerar uma senha", 
                                       font=("Arial", 14), bg="#f0f0f0")
        self.instrucao_label.pack(pady=50)

        # Labels para exibir a senha gerada (inicialmente ocultos)
        self.senha_label = tk.Label(self.frame_senha_gerada, text="", 
                                   font=("Arial", 36, "bold"), bg="#f0f0f0")
        self.senha_label.pack_forget()

        self.tipo_label = tk.Label(self.frame_senha_gerada, text="", 
                                  font=("Arial", 18), bg="#f0f0f0")
        self.tipo_label.pack_forget()

        self.data_label = tk.Label(self.frame_senha_gerada, text="", 
                                  font=("Arial", 12), bg="#f0f0f0")
        self.data_label.pack_forget()

        # Frame para estatísticas
        frame_estatisticas = tk.LabelFrame(frame_conteudo, text="Estatísticas", 
                                          font=("Arial", 12, "bold"))
        frame_estatisticas.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Frame para estatísticas CIVEL/FAMILIA
        frame_cf = tk.LabelFrame(frame_estatisticas, text="CÍVEL/FAMÍLIA", font=("Arial", 10))
        frame_cf.pack(padx=5, pady=5, fill=tk.X)

        self.civel_label = tk.Label(frame_cf, text="CÍVEL: 0", font=("Arial", 10))
        self.civel_label.pack(anchor="w", padx=10, pady=2)

        self.familia_label = tk.Label(frame_cf, text="FAMÍLIA: 0", font=("Arial", 10))
        self.familia_label.pack(anchor="w", padx=10, pady=2)

        # Frame para estatísticas CIVEL/FAMILIA PRIORIDADES
        frame_cfp = tk.LabelFrame(frame_estatisticas, text="CÍVEL/FAMÍLIA PRIORIDADE", font=("Arial", 10))
        frame_cfp.pack(padx=5, pady=5, fill=tk.X)
        
        self.civel_prioridade_label = tk.Label(frame_cfp, text="CÍVEL - PRIORIDADE: 0", font=("Arial", 10))
        self.civel_prioridade_label.pack(anchor="w", padx=10, pady=2)

        self.familia_prioridade_label = tk.Label(frame_cfp, text="FAMÍLIA - PRIORIDADE: 0", font=("Arial", 10))
        self.familia_prioridade_label.pack(anchor="w", padx=10, pady=2)

        # Frame para estatísticas CRIMINAL
        frame_criminal = tk.LabelFrame(frame_estatisticas, text="CRIMINAL", font=("Arial", 10))
        frame_criminal.pack(padx=5, pady=5, fill=tk.X)

        self.criminal_label = tk.Label(frame_criminal, text=f"CRIMINAL: 0", font=("Arial", 10))
        self.criminal_label.pack(anchor="w", padx=10, pady=2)

        self.criminal_prioridade_label = tk.Label(frame_criminal, text=f"CRIMINAL - PRIORIDADE: 0", font=("Arial", 10))
        self.criminal_prioridade_label.pack(anchor="w", padx=10, pady=2)

        # Frame para estatísticas JUIZADO
        frame_juizado = tk.LabelFrame(frame_estatisticas, text="JUIZADO", font=("Arial", 10))
        frame_juizado.pack(padx=5, pady=5, fill=tk.X)

        self.juizado_civel_label = tk.Label(frame_juizado, text="JUIZADO CIVEL: 0", font=("Arial", 10))
        self.juizado_civel_label.pack(anchor="w", padx=10, pady=2)

        self.juizado_criminal_label = tk.Label(frame_juizado, text="JUIZADO CRIMINAL: 0", font=("Arial", 10))
        self.juizado_criminal_label.pack(anchor="w", padx=10, pady=2)

        self.juizado_fazenda_label = tk.Label(frame_juizado, text="FAZENDA: 0", font=("Arial", 10))
        self.juizado_fazenda_label.pack(anchor="w", padx=10, pady=2)

        # Frame para estatísticas JUIZADO PRIORIDADE
        frame_juizado_prioridade = tk.LabelFrame(frame_estatisticas, text="JUIZADO PRIORIDADE", font=("Arial", 10))
        frame_juizado_prioridade.pack(padx=5, pady=5, fill=tk.X)

        self.juizado_civel_prioridade_label = tk.Label(frame_juizado_prioridade, text="JUIZADO CIVEL PRIORIDADE: 0", font=("Arial", 10))
        self.juizado_civel_prioridade_label.pack(anchor="w", padx=10, pady=2)

        self.juizado_criminal_prioridade_label = tk.Label(frame_juizado_prioridade, text="JUIZADO CRIMINAL PRIORIDADE: 0", font=("Arial", 10))
        self.juizado_criminal_prioridade_label.pack(anchor="w", padx=10, pady=2)

        self.juizado_fazenda_prioridade_label = tk.Label(frame_juizado_prioridade, text="FAZENDA PRIORIDADE: 0", font=("Arial", 10))
        self.juizado_fazenda_prioridade_label.pack(anchor="w", padx=10, pady=2)

        # Frame para botões de administração
        frame_admin = tk.Frame(frame_principal)
        frame_admin.pack(fill=tk.X, pady=10)

        # Botões de administração - AQUI ESTÁ A CORREÇÃO
        botao_historico = tk.Button(frame_admin, text="Histórico", font=("Arial", 10),
                                   command=self.pesquisar_historico)  # Alterado de visualizar_historico para pesquisar_historico
        botao_historico.pack(side=tk.LEFT, padx=5)

        botao_estatisticas = tk.Button(frame_admin, text="Estatísticas Detalhadas", font=("Arial", 10),
                                      command=self.visualizar_estatisticas)
        botao_estatisticas.pack(side=tk.LEFT, padx=5)

        botao_inserir_manual = tk.Button(frame_admin, text="Inserir Senha Manual", font=("Arial", 10),
                                        command=self.inserir_senha_manual)
        botao_inserir_manual.pack(side=tk.LEFT, padx=5)

        botao_resetar = tk.Button(frame_admin, text="Resetar Contadores", font=("Arial", 10),
                                 command=self.resetar_contadores)
        botao_resetar.pack(side=tk.LEFT, padx=5)

        botao_deletar = tk.Button(frame_admin, text="Deletar Histórico", font=("Arial", 10),
                                 command=self.deletar_historico)
        botao_deletar.pack(side=tk.LEFT, padx=5)

        # Rodapé com informações
        frame_rodape = tk.Frame(frame_principal)
        frame_rodape.pack(fill=tk.X, pady=5)

        rodape_label = tk.Label(frame_rodape, text="© 2025 Sistema Gerador de Senhas | Versão 1.0", 
                               font=("Arial", 8))
        rodape_label.pack(side=tk.RIGHT)

        # Bloco removido, pois não tinha necessidade de ter essa tela de histórico na homepga
        # Juliano Dantas
            ## Frame para o histórico recente
            #frame_historico = tk.LabelFrame(frame_principal, text="Histórico Recente", font=("Arial", 12, "bold"))
            #frame_historico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            ## Criar a lista de histórico
            #self.historico_lista = tk.Listbox(frame_historico, font=("Courier New", 10), height=5)
            #self.historico_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

            ## Adicionar barra de rolagem
            #scrollbar = tk.Scrollbar(frame_historico)
            #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            ## Conectar a barra de rolagem à lista
            #self.historico_lista.config(yscrollcommand=scrollbar.set)
            #scrollbar.config(command=self.historico_lista.yview)

            # Inicializar estatísticas
        self.atualizar_estatisticas()

    def selecionar_impressora(self, impressoras):
        """
        Exibe uma janela de diálogo para selecionar uma impressora da lista.

        Args:
            impressoras (list): Lista de impressoras disponíveis

        Returns:
            str: Nome da impressora selecionada ou None se cancelado
        """
        # Criar janela de diálogo
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Selecionar Impressora")
        dialogo.geometry("400x300")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)  # Torna a janela dependente da janela principal
        dialogo.grab_set()  # Torna a janela modal

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 150
        dialogo.geometry(f"+{x}+{y}")

        # Variável para armazenar o resultado
        resultado = [None]

        # Label de instrução
        tk.Label(dialogo, text="Selecione a impressora:", font=("Arial", 12)).pack(pady=10)

        # Frame para a lista de impressoras
        frame_lista = tk.Frame(dialogo)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar para a lista
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox para selecionar a impressora
        listbox = tk.Listbox(frame_lista, font=("Arial", 10), yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar scrollbar
        scrollbar.config(command=listbox.yview)

        # Preencher a lista com as impressoras disponíveis
        for impressora in impressoras:
            listbox.insert(tk.END, impressora)

        # Selecionar a primeira impressora por padrão
        if impressoras:
            listbox.selection_set(0)

        # Função para confirmar a seleção
        def confirmar():
            selecionados = listbox.curselection()
            if selecionados:
                indice = selecionados[0]
                resultado[0] = impressoras[indice]
            dialogo.destroy()

        # Função para cancelar
        def cancelar():
            dialogo.destroy()

        # Frame para os botões
        frame_botoes = tk.Frame(dialogo)
        frame_botoes.pack(fill=tk.X, pady=10)

        # Botões
        tk.Button(frame_botoes, text="Confirmar", command=confirmar, 
                 font=("Arial", 10), bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_botoes, text="Cancelar", command=cancelar,
                 font=("Arial", 10), bg="#F44336", fg="white", width=10).pack(side=tk.RIGHT, padx=10)

        # Aguardar até que o diálogo seja fechado
        dialogo.wait_window()

        return resultado[0]

    def atualizar_estatisticas(self):
        """Atualiza os labels de estatísticas com os valores atuais."""
        estatisticas = EstatisticasManager.carregar_estatisticas()

        # Dicionário para mapear os atributos e seus valores correspondentes
        # ligado diretamente as estátisticas na tela principal
        labels_map = {
            'civel_label': ('CIVEL', 'CÍVEL: {}'),
            'familia_label': ('FAMILIA', 'FAMÍLIA: {}'),
            'civel_prioridade_label': ('CIVEL PRIORIDADE', 'CÍVEL PRIORIDADE: {}'),
            'familia_prioridade_label': ('FAMILIA PRIORIDADE', 'FAMÍLIA PRIORIDADE: {}'),
            'criminal_label': ('CRIMINAL', 'CRIMINAL: {}'),
            'criminal_prioridade_label': ('CRIMINAL - PRIORIDADE', 'CRIMINAL PRIORIDADE: {}'),
            'juizado_civel_label': ('JUIZADO CIVEL', 'JUIZADO CIVEL: {}'),
            'juizado_criminal_label': ('JUIZADO CRIMINAL', 'JUIZADO CRIMINAL: {}'),
            'juizado_fazenda_label': ('FAZENDA', 'FAZENDA: {}'),
            'juizado_civel_prioridade_label': ('JUIZADO CIVEL PRIORIDADE', 'JUIZADO CIVEL PRIORIDADE: {}'),
            'juizado_criminal_prioridade_label': ('JUIZADO CRIMINAL PRIORIDADE', 'JUIZADO CRIMINAL PRIORIDADE: {}'),
            'juizado_fazenda_prioridade_label': ('FAZENDA PRIORIDADE', 'FAZENDA PRIORIDADE: {}')
        }

        # Atualizar cada label se existir
        for attr_name, (stat_key, format_str) in labels_map.items():
            if hasattr(self, attr_name):
                label = getattr(self, attr_name)
                value = estatisticas.get(stat_key, 0)
                label.config(text=format_str.format(value))

        # Registrar a atualização no log
        Logger.registrar_log("Estatísticas atualizadas")

    def atualizar_contadores(self):
        """Atualiza os contadores com os valores salvos."""
        self.contadores = self.gerador_senha.contador_manager.counters

    def exibir_senha_gerada(self, senha, tipo, data):
        """Exibe a senha gerada na interface."""
        # Esconder a instrução
        if hasattr(self, 'instrucao_label'):
            self.instrucao_label.pack_forget()

        # Mostrar a senha gerada
        if hasattr(self, 'senha_label'):
            self.senha_label.config(text=f"SENHA: {senha}")
            self.senha_label.pack(pady=(50, 10))

        if hasattr(self, 'tipo_label'):
            self.tipo_label.config(text=f"TIPO: {tipo}")
            self.tipo_label.pack(pady=5)

        if hasattr(self, 'data_label'):
            self.data_label.config(text=f"DATA/HORA: {data}")
            self.data_label.pack(pady=5)

        # Atualizar histórico recente, se o método existir
        if hasattr(self, 'atualizar_historico_recente'):
            try:
                self.atualizar_historico_recente()
            except Exception as e:
                print(f"Erro ao atualizar histórico recente: {e}")

    def pesquisar_historico(self):
        """
        Abre uma janela para pesquisar o histórico com filtros de período e tipo, 
        com opções para exportar para CSV e PDF.
        """
        janela = tk.Toplevel(self.root)
        janela.title("Pesquisar Histórico")
        janela.geometry("800x600")
        janela.minsize(800, 600)

        # Frame para filtros
        frame_filtros = tk.LabelFrame(janela, text="Filtros", font=("Arial", 10, "bold"))
        frame_filtros.pack(fill=tk.X, padx=10, pady=10)

        # Filtro de período
        frame_periodo = tk.Frame(frame_filtros)
        frame_periodo.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(frame_periodo, text="Data Inicial (DD/MM/AAAA):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        data_inicial_entry = tk.Entry(frame_periodo, width=12)
        data_inicial_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_periodo, text="Data Final (DD/MM/AAAA):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        data_final_entry = tk.Entry(frame_periodo, width=12)
        data_final_entry.pack(side=tk.LEFT, padx=5)

        # Filtro de tipo com combobox
        frame_tipo = tk.Frame(frame_filtros)
        frame_tipo.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(frame_tipo, text="Tipo de Senha:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Combobox para os tipos de senha
        tipo_options = sorted({item['tipo'] for item in HistoricoManager.carregar_historico()})
        tipo_combobox = ttk.Combobox(frame_tipo, values=tipo_options, state="readonly", width=30)
        tipo_combobox.pack(side=tk.LEFT, padx=5)
        tipo_combobox.set("")  # Valores inicial (vazio)

        # Frame para tabela de resultados
        frame_resultados = tk.LabelFrame(janela, text="Resultados", font=("Arial", 10, "bold"))
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Contador de resultados
        contador_label = tk.Label(frame_resultados, text="Resultados encontrados: 0", 
                                 font=("Arial", 10))
        contador_label.pack(anchor="w", padx=5, pady=5)

        # Tabela de resultados (usando Text widget com formatação)
        tabela = tk.Text(frame_resultados, height=20, font=("Courier New", 10))
        tabela.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Adicionar scrollbar à tabela
        scrollbar = tk.Scrollbar(tabela)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tabela.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tabela.yview)

        # Função para atualizar a tabela com os resultados filtrados e agrupados
        def atualizar_tabela(dados):
            tabela.delete("1.0", tk.END)

            if not dados:
                tabela.insert(tk.END, "Nenhum resultado encontrado.")
                return

            # Agrupar os dados por data e tipo
            dados_agrupados = {}

            for item in dados:
                # Extrair a data (sem a hora)
                data, _ = item['data'].split()
                tipo = item['tipo']

                # Inicializar a estrutura de dados se necessário
                if data not in dados_agrupados:
                    dados_agrupados[data] = {}

                if tipo not in dados_agrupados[data]:
                    dados_agrupados[data][tipo] = []

                # Adicionar o item ao grupo correspondente
                dados_agrupados[data][tipo].append(item)

            # Exibir os dados agrupados na tabela
            for data in sorted(dados_agrupados.keys()):
                # Cabeçalho da data
                tabela.insert(tk.END, f"\n{'='*70}\n")
                tabela.insert(tk.END, f"DATA: {data}\n")
                tabela.insert(tk.END, f"{'='*70}\n\n")

                for tipo in sorted(dados_agrupados[data].keys()):
                    # Cabeçalho do tipo
                    tabela.insert(tk.END, f"TIPO: {tipo}\n")
                    tabela.insert(tk.END, f"{'-'*70}\n")
                    tabela.insert(tk.END, f"{'Senha':<10} | {'Hora':<10}\n")
                    tabela.insert(tk.END, f"{'-'*70}\n")

                    # Itens deste tipo
                    for item in dados_agrupados[data][tipo]:
                        _, hora = item['data'].split()
                        linha = f"{item['senha']:<10} | {hora:<10}\n"
                        tabela.insert(tk.END, linha)

                    tabela.insert(tk.END, "\n")  # Espaço após cada grupo de tipo

        # Botão para aplicar filtros
        def aplicar_filtros():
            data_inicial = data_inicial_entry.get().strip()
            data_final = data_final_entry.get().strip()
            tipo = tipo_combobox.get().strip()

            # Filtrar os dados
            dados_filtrados = HistoricoManager.filtrar_historico(
                data_inicio=data_inicial, 
                data_fim=data_final,
                tipo=tipo
            )

            # Atualizar a tabela com os resultados
            atualizar_tabela(dados_filtrados)

            # Atualizar contador de resultados
            contador_label.config(text=f"Resultados encontrados: {len(dados_filtrados)}")

        tk.Button(frame_filtros, text="Aplicar Filtros", command=aplicar_filtros, 
                 font=("Arial", 10, "bold")).pack(pady=10)

        # Criar o frame de exportação
        frame_exportacao = tk.Frame(janela)
        frame_exportacao.pack(fill=tk.X, padx=10, pady=10)

        # Botões de exportação
        def exportar_csv():
            data_inicial = data_inicial_entry.get().strip()
            data_final = data_final_entry.get().strip()
            tipo = tipo_combobox.get().strip()
            dados_filtrados = HistoricoManager.filtrar_historico(data_inicio=data_inicial, 
                                                                 data_fim=data_final,
                                                                 tipo=tipo)
            HistoricoManager.exportar_para_csv(dados_filtrados)

        def exportar_pdf():
            data_inicial = data_inicial_entry.get().strip()
            data_final = data_final_entry.get().strip()
            tipo = tipo_combobox.get().strip()
            dados_filtrados = HistoricoManager.filtrar_historico(data_inicio=data_inicial, 
                                                                 data_fim=data_final,
                                                                 tipo=tipo)
            HistoricoManager.exportar_para_pdf(dados_filtrados)

        tk.Button(frame_exportacao, text="Exportar para CSV", command=exportar_csv,
                 font=("Arial", 10), bg="#e6f2ff", padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_exportacao, text="Exportar para PDF", command=exportar_pdf,
                 font=("Arial", 10), bg="#fff2e6", padx=10, pady=5).pack(side=tk.LEFT, padx=10)

        # Carregar todos os dados inicialmente
        dados_iniciais = HistoricoManager.carregar_historico()
        atualizar_tabela(dados_iniciais)
        contador_label.config(text=f"Resultados encontrados: {len(dados_iniciais)}")

    def deletar_historico(self):
        senha = simpledialog.askstring("Senha de Admin", "Digite a senha de deleção:", show='*')
        if senha != Config.SENHA_DELETE:
            messagebox.showerror("Erro", "Senha incorreta.")
            return
        if os.path.exists(Config.ARQUIVO_HISTORICO):
            if messagebox.askyesno("Confirmação", "Tem certeza que deseja deletar TODO o histórico?"):
                os.remove(Config.ARQUIVO_HISTORICO)
                messagebox.showinfo("Sucesso", "Histórico deletado com sucesso.")
                Logger.registrar_log("Histórico deletado pelo administrador.")
        else:
            messagebox.showinfo("Info", "Nenhum histórico encontrado.")

    def resetar_contadores(self):
        """Reseta todos os contadores e estatísticas para zero."""
        # Confirmar com o usuário
        if messagebox.askyesno("Resetar Dados", "Tem certeza que deseja resetar todos os contadores e estatísticas?"):
            # Resetar contadores
            self.gerador_senha.contador_manager.resetar_contadores()
            
            # Resetar estatísticas
            EstatisticasManager.resetar_estatisticas()
            
            # Atualizar a exibição dos contadores
            self.atualizar_contadores()
            
            # Atualizar a exibição das estatísticas
            self.atualizar_estatisticas()
            
            # Registrar no log
            Logger.registrar_log("Contadores e estatísticas resetados")
            
            # Informar ao usuário
            messagebox.showinfo("Sucesso", "Contadores e estatísticas resetados com sucesso!")

    def inserir_senha_manual(self): 
        """Insere uma senha manualmente escolhendo o tipo e número, com opção de impressão."""
        # Criar uma janela de diálogo personalizada
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Inserir Senha Manual")
        dialogo.geometry("400x250")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)  # Torna a janela dependente da janela principal
        dialogo.grab_set()  # Torna a janela modal

        # Centralizar a janela
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 125
        dialogo.geometry(f"+{x}+{y}")

        # Variáveis para armazenar os resultados
        resultado = {"tipo": None, "numero": None, "confirmado": False}

        # Frame para o tipo de senha
        frame_tipo = tk.Frame(dialogo)
        frame_tipo.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(frame_tipo, text="Tipo de Senha:", font=("Arial", 10)).pack(side=tk.LEFT)

        # Combobox para selecionar o tipo
        tipo_combobox = ttk.Combobox(frame_tipo, state="readonly", width=30)
        tipo_combobox.pack(side=tk.LEFT, padx=10)

        # Preencher o combobox com os tipos disponíveis
        tipos_disponiveis = Config.TIPOS_SENHA
        tipo_combobox['values'] = tipos_disponiveis
        tipo_combobox.current(0)  # Selecionar o primeiro tipo por padrão

        # Frame para o número da senha
        frame_numero = tk.Frame(dialogo)
        frame_numero.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(frame_numero, text="Número da Senha:", font=("Arial", 10)).pack(side=tk.LEFT)

        # Entry para o número da senha
        numero_entry = tk.Entry(frame_numero, width=10)
        numero_entry.pack(side=tk.LEFT, padx=10)
        numero_entry.insert(0, "001")  # Valor padrão

        # Função para validar e confirmar
        def confirmar():
            # Validar o número da senha
            try:
                numero = int(numero_entry.get())
                if numero < 1 or numero > 999:
                    messagebox.showerror("Erro", "O número da senha deve estar entre 1 e 999.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "O número da senha deve ser um valor numérico.")
                return

            # Armazenar os resultados
            resultado["tipo"] = tipo_combobox.get()
            resultado["numero"] = numero
            resultado["confirmado"] = True

            # Fechar o diálogo
            dialogo.destroy()

        # Função para cancelar
        def cancelar():
            dialogo.destroy()

        # Frame para os botões
        frame_botoes = tk.Frame(dialogo)
        frame_botoes.pack(fill=tk.X, pady=20)

        # Botões
        tk.Button(frame_botoes, text="Confirmar", command=confirmar, 
                 font=("Arial", 10), bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=20)

        tk.Button(frame_botoes, text="Cancelar", command=cancelar,
                 font=("Arial", 10), bg="#F44336", fg="white", width=10).pack(side=tk.RIGHT, padx=20)

        # Aguardar até que o diálogo seja fechado
        dialogo.wait_window()

        # Se o usuário cancelou ou fechou a janela, retornar
        if not resultado["confirmado"]:
            return

        # Processar a senha
        tipo = resultado["tipo"]
        numero = resultado["numero"]
        senha = f"{numero:03d}"  # Formata o número com 3 dígitos
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Verificar se é um tipo que requer especificação CIVEL/FAMILIA
        tipo_especifico = tipo
        if tipo.upper() in ["CIVEL - FAMILIA", "CÍVEL FÁMILIA PRIORIDADE"]:
            # Criar uma janela de diálogo para escolher entre CIVEL e FAMILIA
            subtipo_dialogo = tk.Toplevel(self.root)
            subtipo_dialogo.title("Escolha o Subtipo")
            subtipo_dialogo.geometry("300x150")
            subtipo_dialogo.resizable(False, False)
            subtipo_dialogo.transient(self.root)
            subtipo_dialogo.grab_set()

            # Centralizar a janela
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
            subtipo_dialogo.geometry(f"+{x}+{y}")

            # Variável para armazenar o subtipo
            subtipo_resultado = [None]

            # Label de instrução
            tk.Label(subtipo_dialogo, text="Esta senha é de CÍVEL ou FAMÍLIA?", 
                    font=("Arial", 12)).pack(pady=10)

            # Função para confirmar o subtipo
            def confirmar_subtipo(subtipo):
                subtipo_resultado[0] = subtipo
                subtipo_dialogo.destroy()

            # Frame para os botões
            frame_subtipo = tk.Frame(subtipo_dialogo)
            frame_subtipo.pack(pady=10)

            # Cor do botão baseada no tipo
            cor_botao = "#9C27B0" if "PRIORIDADE" in tipo.upper() else "#4CAF50"

            # Botões para escolher o subtipo
            tk.Button(frame_subtipo, text="CIVEL", font=("Arial", 12, "bold"),
                     bg=cor_botao, fg="white", width=10,
                     command=lambda: confirmar_subtipo("CIVEL")).pack(side=tk.LEFT, padx=10)

            tk.Button(frame_subtipo, text="FAMILIA", font=("Arial", 12, "bold"),
                     bg=cor_botao, fg="white", width=10,
                     command=lambda: confirmar_subtipo("FAMILIA")).pack(side=tk.LEFT, padx=10)

            # Aguardar até que o diálogo seja fechado
            subtipo_dialogo.wait_window()

            # Se o usuário selecionou um subtipo
            if subtipo_resultado[0]:
                subtipo = subtipo_resultado[0]

                # Determinar se é um caso com prioridade
                if "PRIORIDADE" in tipo.upper():
                    tipo_especifico = f"{subtipo} PRIORIDADE"
                else:
                    tipo_especifico = subtipo

                # Atualizar estatísticas
                EstatisticasManager.incrementar_estatistica(subtipo)
                self.atualizar_estatisticas()

        # Verificar se é um tipo que requer especificação JUIZADO
        elif tipo.upper() in ["JUIZADO - FAZENDA", "JUIZADO FAZENDA - PRIORIDADE"]:
            # Criar uma janela de diálogo para escolher o tipo de JUIZADO
            subtipo_dialogo = tk.Toplevel(self.root)
            subtipo_dialogo.title("Escolha o Tipo de JUIZADO")
            subtipo_dialogo.geometry("400x200")
            subtipo_dialogo.resizable(False, False)
            subtipo_dialogo.transient(self.root)
            subtipo_dialogo.grab_set()

            # Centralizar a janela
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
            subtipo_dialogo.geometry(f"+{x}+{y}")

            # Variável para armazenar o subtipo
            subtipo_resultado = [None]

            # Label de instrução
            tk.Label(subtipo_dialogo, text="Selecione o tipo de JUIZADO:", 
                    font=("Arial", 12, "bold")).pack(pady=10)

            # Função para confirmar o subtipo
            def confirmar_subtipo(subtipo):
                subtipo_resultado[0] = subtipo
                subtipo_dialogo.destroy()

            # Frame para os botões
            frame_subtipo = tk.Frame(subtipo_dialogo)
            frame_subtipo.pack(pady=10)

            # Cor do botão baseada no tipo
            cor_botao = "#FF5722" if "PRIORIDADE" in tipo.upper() else "#4CAF50"

            # Determinar os textos dos botões com base no tipo
            sufixo = " PRIORIDADE" if "PRIORIDADE" in tipo.upper() else ""

            # Botões para escolher o subtipo
            tk.Button(frame_subtipo, text=f"JUIZADO CIVEL{sufixo}", font=("Arial", 12, "bold"),
                     bg=cor_botao, fg="white", width=20,
                     command=lambda: confirmar_subtipo(f"JUIZADO CIVEL{sufixo}")).pack(side=tk.TOP, pady=5)

            tk.Button(frame_subtipo, text=f"JUIZADO CRIMINAL{sufixo}", font=("Arial", 12, "bold"),
                     bg=cor_botao, fg="white", width=20,
                     command=lambda: confirmar_subtipo(f"JUIZADO CRIMINAL{sufixo}")).pack(side=tk.TOP, pady=5)

            tk.Button(frame_subtipo, text=f"FAZENDA{sufixo}", font=("Arial", 12, "bold"),
                     bg=cor_botao, fg="white", width=20,
                     command=lambda: confirmar_subtipo(f"FAZENDA{sufixo}")).pack(side=tk.TOP, pady=5)

            # Aguardar até que o diálogo seja fechado
            subtipo_dialogo.wait_window()

            # Se o usuário selecionou um subtipo
            if subtipo_resultado[0]:
                tipo_especifico = subtipo_resultado[0]

                # Atualizar estatísticas
                EstatisticasManager.incrementar_estatistica(tipo_especifico)
                self.atualizar_estatisticas()

        # Salvar no histórico com o tipo específico, se aplicável
        HistoricoManager.salvar_historico(senha, tipo_especifico, now)
        EstatisticasManager.incrementar_estatistica(tipo_especifico)
        self.atualizar_estatisticas()

        # Exibir confirmação ao usuário
        messagebox.showinfo("Senha Inserida", f"Senha: {senha}\nTipo: {tipo_especifico}\nData/Hora: {now}")

        # Perguntar se deseja imprimir
        deseja_imprimir = messagebox.askyesno("Impressão", "Deseja imprimir a senha?")
        if deseja_imprimir:
            # Listar impressoras disponíveis
            impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]

            # Usar o seletor de impressora
            impressora = self.selecionar_impressora(impressoras)

            if impressora:
                sucesso = ImpressaoManager.imprimir_senha_termica(senha, tipo_especifico, now, impressora)
                if sucesso:
                    messagebox.showinfo("Impressão", "Senha impressa com sucesso!")
                else:
                    messagebox.showerror("Impressão", "Falha ao imprimir a senha.")

    def visualizar_estatisticas(self):
        """Abre uma janela com estatísticas detalhadas, filtro por período em DD/MM/AA e exportação."""
        historico = HistoricoManager.carregar_historico()
        estatisticas = EstatisticasManager.carregar_estatisticas()

        # Criar a janela de estatísticas
        janela = tk.Toplevel(self.root)
        janela.title("Estatísticas Detalhadas")
        janela.geometry("700x600")  # Aumentei o tamanho para acomodar mais estatísticas

        # Criar um canvas com scrollbar para as estatísticas
        canvas_frame = tk.Frame(janela)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame de Filtro
        frame_filtros = tk.Frame(scrollable_frame)
        frame_filtros.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame_filtros, text="Data Inicial (DD/MM/AAAA):", font=("Arial", 10)).pack(side=tk.LEFT)
        data_inicial_entry = tk.Entry(frame_filtros, width=12)
        data_inicial_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_filtros, text="Data Final (DD/MM/AAAA):", font=("Arial", 10)).pack(side=tk.LEFT)
        data_final_entry = tk.Entry(frame_filtros, width=12)
        data_final_entry.pack(side=tk.LEFT, padx=5)

        # Botão para filtrar
        def aplicar_filtro():
            data_inicial = data_inicial_entry.get().strip()
            data_final = data_final_entry.get().strip()
            filtrado = HistoricoManager.filtrar_historico(data_inicio=data_inicial, data_fim=data_final)
            atualizar_tela(filtrado)

        tk.Button(frame_filtros, text="Filtrar", command=aplicar_filtro).pack(side=tk.LEFT, padx=10)

        # Estatísticas resumidas (CÍVEL e FAMÍLIA)
        frame_cf = tk.LabelFrame(scrollable_frame, text="Estatísticas CÍVEL/FAMÍLIA", font=("Arial", 10))
        frame_cf.pack(pady=5, padx=10, fill=tk.X)

        total_civel_label = tk.Label(frame_cf, text=f"Total CÍVEL: {estatisticas.get('CIVEL', 0)}", font=("Arial", 10, "bold"))
        total_civel_label.pack(anchor="w", padx=10, pady=5)

        total_familia_label = tk.Label(frame_cf, text=f"Total FAMÍLIA: {estatisticas.get('FAMILIA', 0)}", font=("Arial", 10, "bold"))
        total_familia_label.pack(anchor="w", padx=10, pady=5)


        # Estatísticas resumidas (CÍVEL/FAMILIA PRIORIDADE) 
        frame_cfp = tk.LabelFrame(scrollable_frame, text="Estatísticas CÍVEL/FAMÍLIA PRIORIDADE", font=("Arial", 10))
        frame_cfp.pack(pady=5, padx=10, fill=tk.X)

        total_civel_prioridade_label = tk.Label(frame_cfp, text=f"Total CÍVEL PRIORIDADE: {estatisticas.get('CIVEL PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_civel_prioridade_label.pack(anchor="w", padx=10, pady=5)

        total_familia_prioridade_label = tk.Label(frame_cfp, text=f"Total FAMÍLIA PRIORIDADE: {estatisticas.get('FAMILIA PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_familia_prioridade_label.pack(anchor="w", padx=10, pady=5)


        # Estatísticas CRIMINAL
        frame_criminal = tk.LabelFrame(scrollable_frame, text="Estatísticas CRIMINAL", font=("Arial", 10))
        frame_criminal.pack(pady=5, padx=10, fill=tk.X)

        total_criminal_label = tk.Label(frame_criminal, text=f"Total CRIMINAL: {estatisticas.get('CRIMINAL', 0)}", font=("Arial", 10, "bold"))
        total_criminal_label.pack(anchor="w", padx=10, pady=5)

        total_criminal_prioridade_label = tk.Label(frame_criminal, text=f"Total CRIMINAL - PRIORIDADE: {estatisticas.get('CRIMINAL - PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_criminal_prioridade_label.pack(anchor="w", padx=10, pady=5)

        # Estatísticas JUIZADO
        frame_juizado = tk.LabelFrame(scrollable_frame, text="Estatísticas JUIZADO", font=("Arial", 10))
        frame_juizado.pack(pady=5, padx=10, fill=tk.X)

        total_juizado_civel = tk.Label(frame_juizado, text=f"Total JUIZADO CIVEL: {estatisticas.get('JUIZADO CIVEL', 0)}", font=("Arial", 10, "bold"))
        total_juizado_civel.pack(anchor="w", padx=10, pady=5)

        total_juizado_criminal = tk.Label(frame_juizado, text=f"Total JUIZADO CRIMINAL: {estatisticas.get('JUIZADO CRIMINAL', 0)}", font=("Arial", 10, "bold"))
        total_juizado_criminal.pack(anchor="w", padx=10, pady=5)

        total_juizado_fazenda = tk.Label(frame_juizado, text=f"Total FAZENDA: {estatisticas.get('FAZENDA', 0)}", font=("Arial", 10, "bold"))
        total_juizado_fazenda.pack(anchor="w", padx=10, pady=5)

        # Estatísticas JUIZADO PRIORIDADE
        frame_juizado_prioridade = tk.LabelFrame(scrollable_frame, text="Estatísticas JUIZADO PRIORIDADE", font=("Arial", 10))
        frame_juizado_prioridade.pack(pady=5, padx=10, fill=tk.X)

        total_juizado_civel_prioridade = tk.Label(frame_juizado_prioridade, text=f"Total JUIZADO CIVEL PRIORIDADE: {estatisticas.get('JUIZADO CIVEL PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_juizado_civel_prioridade.pack(anchor="w", padx=10, pady=5)

        total_juizado_criminal_prioridade = tk.Label(frame_juizado_prioridade, text=f"Total JUIZADO CRIMINAL PRIORIDADE: {estatisticas.get('JUIZADO CRIMINAL PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_juizado_criminal_prioridade.pack(anchor="w", padx=10, pady=5)

        total_juizado_fazenda_prioridade = tk.Label(frame_juizado_prioridade, text=f"Total FAZENDA PRIORIDADE: {estatisticas.get('FAZENDA PRIORIDADE', 0)}", font=("Arial", 10, "bold"))
        total_juizado_fazenda_prioridade.pack(anchor="w", padx=10, pady=5)

        # Contagem por tipo de senha
        frame_tipos = tk.LabelFrame(scrollable_frame, text="Contagem por Tipo de Senha")
        frame_tipos.pack(padx=10, pady=10, fill=tk.BOTH)

        lista_tipos = tk.Text(frame_tipos, height=15, wrap=tk.WORD)
        lista_tipos.pack(padx=10, pady=10, fill=tk.BOTH)

        def atualizar_tela(dados):
            contagem_tipos = defaultdict(int)
            for item in dados:
                contagem_tipos[item['tipo']] += 1

            lista_tipos.delete("1.0", tk.END)
            for tipo, quantidade in sorted(contagem_tipos.items()):
                lista_tipos.insert(tk.END, f"{tipo}: {quantidade}\n")

        # Exportar estatísticas
        def exportar_estatisticas():
            data_inicial = data_inicial_entry.get().strip()
            data_final = data_final_entry.get().strip()
            filtrado = HistoricoManager.filtrar_historico(data_inicio=data_inicial, data_fim=data_final)

            if not filtrado:
                messagebox.showinfo("Exportar", "Nenhum dado encontrado para o período especificado.")
                return  
            arquivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Arquivos CSV", "*.csv")])
            if not arquivo:
                return

            # Abrir o arquivo CSV com delimitador ponto e vírgula (;)
            with open(arquivo, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file, delimiter=';')  # Aqui mudamos para ';'
                writer.writerow(["Data", "Tipo de Senha", "Quantidade"])  # Cabeçalhos

                contagem_tipos = defaultdict(int)
                for item in filtrado:
                    contagem_tipos[item['tipo']] += 1

                for tipo, quantidade in sorted(contagem_tipos.items()):
                    writer.writerow(["-"] + [tipo, quantidade])  # Escreve no CSV com separação em colunas

            messagebox.showinfo("Exportar", "Estatísticas exportadas com sucesso!")

        frame_exportacao = tk.Frame(scrollable_frame)
        frame_exportacao.pack(pady=10)

        tk.Button(frame_exportacao, text="Exportar Estatísticas", command=exportar_estatisticas).pack()

        # Inicializar lista com todos os dados
        atualizar_tela(historico)

    def atualizar_historico_recente(self):
        """Atualiza a lista de histórico recente na interface."""
        try:
            # Limpar a lista atual
            self.historico_lista.delete(0, tk.END)

            # Carregar o histórico
            historico = HistoricoManager.carregar_historico()
            print(f"Histórico carregado: {len(historico)} registros")

            # Se não houver histórico, mostrar mensagem
            if not historico:
                self.historico_lista.insert(tk.END, "Nenhum histórico disponível")
                return

            # Mostrar as entradas mais recentes (últimas 10)
            entradas_recentes = historico[-10:] if len(historico) > 10 else historico
            entradas_recentes.reverse()  # Mostrar as mais recentes primeiro

            for entrada in entradas_recentes:
                senha = entrada.get("senha", "")
                tipo = entrada.get("tipo", "")
                data = entrada.get("data", "")

                # Formatar a entrada para exibição
                texto = f"{senha} | {tipo} | {data}"
                self.historico_lista.insert(tk.END, texto)

            print(f"Histórico atualizado na interface: {len(entradas_recentes)} itens")
        except Exception as e:
            print(f"Erro ao atualizar histórico recente: {e}")
            if hasattr(self, 'historico_lista'):
                self.historico_lista.delete(0, tk.END)
                self.historico_lista.insert(tk.END, f"Erro ao carregar histórico: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGeradorSenhasApp(root)
    root.mainloop()