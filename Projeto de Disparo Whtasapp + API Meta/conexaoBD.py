import pyodbc

server = '192.xxx.xx.xxx'
database = 'Sistema UAU'
username = '###'
password = '####'
conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'

def conectar_banco():
    try:
        conn = pyodbc.connect(conn_string)
        print('✅ Conexão bem-sucedida!')
        return conn
    except Exception as e:
        print(f'❌ Erro na conexão: {e}')
        return None


conexao = conectar_banco()
cursor = conexao.cursor() if conexao else None
