# Importação de módulos personalizados
import API_Meta as api  # Módulo personalizado para interação com a API do Meta
import tratamentoPDFs as tp  # Módulo personalizado para processamento de PDFs
# Importação das bibliotecas necessárias
import customtkinter as ctk  # Biblioteca para criar interfaces gráficas modernas
import threading  # Para executar processos em paralelo
import time  # Para adicionar delays quando necessário
import sys  # Para manipulação de entrada/saída padrão
import io  # Para criar streams de entrada/saída
import logging  # Para registro de logs
import traceback  # Para capturar informações detalhadas de exceções

# Configuração do sistema de logging
# Isso permitirá registrar informações importantes e erros em um arquivo
logging.basicConfig(filename=fr'logs\sistema_disparo.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Class responsável por redirecionar a saída padrão para um widget de texto
# Isso permite que mensagens impressas apareçam na interface gráfica
class TextRedirect(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()  # Inicializa a classe pai (io.StringIO)
        self.text_widget = text_widget  # Widget de texto onde as mensagens serão exibidas

    def write(self, s):
        # Método chamado quando algo é "impresso" no terminal
        self.text_widget.insert(ctk.END, s)  # Insere o texto no widget
        self.text_widget.see(ctk.END)  # Rola o widget para mostrar o texto mais recente
        logging.info(s.strip())  # Registra a mensagem no log

# Class responsável por gerenciar sistema(fluxo)
class SistemaDisparo:
    def __init__(self):
        # Eventos para controlar o fluxo do processo
        # Estes eventos ajudam a sincronizar diferentes partes do programa
        self.processo_importacao_concluido = threading.Event()
        self.processo_em_andamento = threading.Event()

    # Função responsável por gerenciar o login do usuário
    def login(self):
        app = ctk.CTk()  # Cria a janela principal do login
        ctk.set_appearance_mode('dark')  # Define o tema escuro para a interface
        app.title('Sistema de Disparo - Login')
        app.geometry('300x300')  # Define o tamanho da janela

        def validar_login():
            # Função interna para verificar as credenciais
            usuario = campo_usuario.get()
            senha = campo_senha.get()
            if usuario == 'juliano' and senha == '123456':
                app.destroy()  # Fecha a janela de login
                self.homepage()  # Abre a página principal
            else:
                resultado_login.configure(text='Login incorreto', text_color='red')

        # Criação dos widgets de login
        ctk.CTkLabel(app, text='Usuário').pack(pady=10)
        campo_usuario = ctk.CTkEntry(app, placeholder_text='Digite seu usuário')
        campo_usuario.pack(pady=10)

        ctk.CTkLabel(app, text='Senha').pack(pady=10)
        campo_senha = ctk.CTkEntry(app, placeholder_text='Digite sua senha', show='*')
        campo_senha.pack(pady=10)

        ctk.CTkButton(app, text='Login', command=validar_login).pack(pady=10)
        resultado_login = ctk.CTkLabel(app, text='')
        resultado_login.pack(pady=10)

        app.mainloop()  # Inicia o loop principal da interface de login

    # Função responsável por criar a interface principal do sistema que vem após o login
    def homepage(self):
        self.home = ctk.CTk()  # Cria a janela principal
        self.home.title('Sistema de Disparo')
        self.home.geometry('1920x1080')  # Define um tamanho grande para a janela
        self.home.state('zoomed')  # Maximiza a janela

        # Cria um frame de fundo para melhorar a aparência
        frame_background = ctk.CTkFrame(self.home, fg_color="lightgray")
        frame_background.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.7)

        # Adiciona o título principal
        ctk.CTkLabel(self.home, text="Sistema de Disparo Wpp", font=("Verdana", 36), text_color='White').pack(pady=50)

        # Cria o botão para importar boletos
        self.botao_importar = ctk.CTkButton(
            self.home, 
            text='Importar Boletos', 
            command=self.BarraProgresso,
            font=('Arial', 24), 
            height=75, 
            width=175,
            fg_color='Red', 
            border_color='Black',
            hover_color="Green", 
            border_width=1
        )
        self.botao_importar.place(relx=0.8, rely=0.7, anchor='center')

        # Cria o botão para enviar boletos
        self.botao_enviar = ctk.CTkButton(
            self.home, 
            text='Enviar Boletos', 
            command=self.BotaoEnviar,
            font=('Arial', 24), 
            height=75, 
            width=175,
            fg_color='Blue', 
            border_color='Black', 
            hover_color="green", 
            border_width=1,
            state="disabled"  # Inicialmente desabilitado
        )
        self.botao_enviar.place(relx=0.2, rely=0.7, anchor='center')

        # Configura o protocolo de fechamento da janela
        self.home.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.home.resizable(True, True)  # Permite redimensionar a janela
        self.home.mainloop()  # Inicia o loop principal da interface

    # Função responsável por gerenciar o processo de importação de boletos
    # Esta função cria uma barra de progresso e um terminal de texto para fornecer feedback durante a importação
    def BarraProgresso(self):
        # Verifica se já há um processo em andamento
        if self.processo_em_andamento.is_set():
            ctk.CTkMessagebox(title="Aviso", message="Um processo já está em andamento. Por favor, aguarde.")
            return

        # Configura o estado do processo
        self.processo_em_andamento.set()
        self.processo_importacao_concluido.clear()
        self.botao_importar.configure(state="disabled")
        self.botao_enviar.configure(state="disabled")

        # Cria a barra de progresso (representada por um label neste caso)
        barra = ctk.CTkLabel(self.home, text='Importando boletos...', font=("Arial", 24))
        barra.place(relx=0.5, rely=0.5, anchor='center')

        # Cria o terminal de texto para exibir mensagens
        text_terminal = ctk.CTkTextbox(self.home, height=200, width=600)
        text_terminal.place(relx=0.5, rely=0.7, anchor='center')

        # Redireciona a saída padrão e de erro para o terminal de texto
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TextRedirect(text_terminal)
        sys.stderr = TextRedirect(text_terminal)

        def run():
            # Função para executar o processo de importação em uma thread separada
            try:
                boleto_manager = tp.BoletoManager()
                boleto_manager.processar_boletos()
                time.sleep(5)  # Simula um processo que leva algum tempo
            except Exception as e:
                logging.error(f"Erro durante o processamento de boletos: {str(e)}")
                logging.error(traceback.format_exc())
                self.home.after(0, lambda: barra.configure(text=f'Erro: {str(e)}'))
            finally:
                # Restaura a saída padrão e finaliza o processo
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                self.home.after(0, lambda: self.finalizar_importacao(barra, text_terminal))

        # Inicia a thread de importação
        threading.Thread(target=run).start()

    # Função responsável por gerenciar o botão/funcionalidade envio de boletos
    def BotaoEnviar(self):
        # Verifica se há um processo em andamento ou se os boletos foram importados
        if self.processo_em_andamento.is_set():
            ctk.CTkMessagebox(title="Aviso", message="Um processo já está em andamento. Por favor, aguarde.")
            return

        if not self.processo_importacao_concluido.is_set():
            ctk.CTkMessagebox(title="Aviso", message="Por favor, importe os boletos primeiro.")
            return

        # Configura o estado do processo
        self.processo_em_andamento.set()
        self.botao_enviar.configure(state="disabled")
        self.botao_importar.configure(state="disabled")

        # Cria a barra de progresso e o terminal de texto
        barra = ctk.CTkLabel(self.home, text='Enviando boletos...', font=("Arial", 24))
        barra.place(relx=0.5, rely=0.5, anchor='center')
        text_terminal = ctk.CTkTextbox(self.home, height=200, width=600)
        text_terminal.place(relx=0.5, rely=0.7, anchor='center')

        # Redireciona a saída padrão e de erro
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TextRedirect(text_terminal)
        sys.stderr = TextRedirect(text_terminal)

        def run():
            # Função para executar o processo de envio em uma thread separada
            try:
                api.EnvioMensagem(api.token, api.arquivo)
                self.home.after(0, lambda: barra.configure(text='Envio Concluído'))
                time.sleep(5)  # Simula um processo que leva algum tempo
            except Exception as e:
                logging.error(f"Erro durante o envio de mensagens: {str(e)}")
                logging.error(traceback.format_exc())
                self.home.after(0, lambda: barra.configure(text=f'Erro: {str(e)}'))
            finally:
                # Restaura a saída padrão e finaliza o processo
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                self.home.after(0, lambda: self.finalizar_envio(barra, text_terminal))

        # Inicia a thread de envio
        threading.Thread(target=run).start()

    # Função responsável por finalizar o processo de importação
    # Esta função remove os widgets de progresso e reativa os botões
    def finalizar_importacao(self, barra, text_terminal):
        # Remove os widgets de progresso se ainda existirem
        if barra and barra.winfo_exists():
            barra.destroy()
        if text_terminal and text_terminal.winfo_exists():
            text_terminal.destroy()
        
        # Atualiza o estado do processo
        self.processo_importacao_concluido.set()
        self.processo_em_andamento.clear()
        
        # Reativa os botões
        self.botao_enviar.configure(state="normal")
        self.botao_importar.configure(state="normal")
        
        # Exibe mensagem de sucesso
        ctk.CTkMessagebox(title="Sucesso", message="Importação de boletos concluída com sucesso!")

    # Função responsável por finalizar o processo de envio
    # Esta função é chamada quando o envio de mensagens é concluído
    def finalizar_envio(self, barra, text_terminal):
        # Remove os widgets de progresso se ainda existirem
        if barra and barra.winfo_exists():
            barra.destroy()
        if text_terminal and text_terminal.winfo_exists():
            text_terminal.destroy()
        
        # Atualiza o estado do processo
        self.processo_em_andamento.clear()
        
        # Reativa os botões
        self.botao_enviar.configure(state="normal")
        self.botao_importar.configure(state="normal")
        
        # Exibe mensagem de sucesso
        ctk.CTkMessagebox(title="Sucesso", message="Envio de boletos concluído com sucesso!")

    # Função chamada quando a janela principal é fechada
    # Esta função garante que o loop principal seja encerrado corretamente
    def on_closing(self):
        logging.info("Aplicação sendo fechada")
        self.home.quit()  # Encerra o loop principal da interface

# Ponto de entrada do programa
if __name__ == "__main__":
    try:
        sistema = SistemaDisparo()  # Cria uma instância do sistema
        sistema.login()  # Inicia o sistema com a tela de login
    except Exception as e:
        # Captura e registra qualquer erro crítico que possa ocorrer
        logging.critical(f"Erro crítico na aplicação: {str(e)}")
        logging.critical(traceback.format_exc())
        ctk.CTkMessagebox(title="Erro Crítico", message=f"Ocorreu um erro crítico: {str(e)}\nPor favor, verifique os logs.")
