import json as json
import pamdas as pd

# ===========CARREGAR DADOS=======
perfil = json.load(open ('/data/perfil_investidor.json'))
trasacoes = pd.read_csv('data/trasecoes.csv')
historico = pd.read_csv('data/historico_atendimento.csv')
produtos = json.load(open('data/produtos_financeiros.json'))
