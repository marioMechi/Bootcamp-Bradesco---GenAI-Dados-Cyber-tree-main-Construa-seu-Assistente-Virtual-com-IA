# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores para mostrar como o cliente vem usando seu dinheiro |
| `perfil_investidor.json` | JSON | Personalizar recomendações para cada tipo de cliente|
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil do cliente|
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente ver quanto o cliente pode investir|

> [!TIP]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Modifiquei os produtos financeiros para produtos com data atuais e adicionei investimentos de renda fixa.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

```python
import pandas as pd
import json
import os
 
# Ajuste este caminho para a pasta onde estão os arquivos
PASTA = "."  # ex: "./dados" ou "/home/usuario/dados"
 
 
def importar_csv(nome_arquivo, **kwargs):
    """Importa um arquivo CSV como DataFrame do pandas."""
    caminho = os.path.join(PASTA, nome_arquivo)
    try:
        df = pd.read_csv(caminho, **kwargs)
        print(f"[OK] {nome_arquivo}: {df.shape[0]} linhas, {df.shape[1]} colunas")
        return df
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return None
    except Exception as e:
        print(f"[ERRO] Falha ao importar {nome_arquivo}: {e}")
        return None
 
 
def importar_json(nome_arquivo):
    """Importa um arquivo JSON. Retorna dict/list (bruto) e, se possível, um DataFrame."""
    caminho = os.path.join(PASTA, nome_arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        print(f"[OK] {nome_arquivo} carregado ({type(dados).__name__})")
 
        # Tenta converter para DataFrame quando fizer sentido
        try:
            df = pd.json_normalize(dados)
        except Exception:
            df = None
 
        return dados, df
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"[ERRO] JSON inválido em {nome_arquivo}: {e}")
        return None, None
 
 
if __name__ == "__main__":
    # --- CSVs ---
    df_historico = importar_csv("historico_atendimento.csv")
    df_transacoes = importar_csv("transacoes.csv")
 
    # --- JSONs ---
    dados_perfil, df_perfil = importar_json("perfil_investidor.json")
    dados_produtos, df_produtos = importar_json("produtos_financeiros.json")
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?
```text
DADOS DO CLIENTE:
historico_atendimento.csv
PERFIL DO CLEINTE:
perfil_investidor.json
TRANSAÇÕES DO CLIENTE:
transacoes.csv
PRODUTOS OFERECIDOS:
produtos_financeiros.json
```

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
