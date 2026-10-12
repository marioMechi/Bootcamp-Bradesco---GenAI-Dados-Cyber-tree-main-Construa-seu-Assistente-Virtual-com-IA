import json as json
from pathlib import Path

import pandas as pd
import requests as request
import streamlit as st 

# ==========CONFIGURAÇÕES=========
OLLAMA_URL = 'http://localhost:11434/api/chat'
MODELO = 'gpt-oss'
LIMITE_TOKENS_RESPOSTA = 1024
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

# ===========CARREGAR DADOS=======
perfil = json.loads((DATA_DIR / 'perfil_investidor.json').read_text(encoding='utf-8'))
transacoes = pd.read_csv(DATA_DIR / 'transacoes.csv')
historico = pd.read_csv(DATA_DIR / 'historico_atendimento.csv')
produtos = json.loads((DATA_DIR / 'produtos_financeiros.json').read_text(encoding='utf-8'))

# ==========MONTAR CONTEXTO========
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']} 
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES: 
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ==========SYSTEM PROMPT========
SYSTEM_PROMPT = f"""
Você é o Ivo um agente de investimento de renda fixa para iniciantes.

Exemplo de estrutura:
Você é um agente financeiro inteligente especializado em renda fixa
Seu objetivo é calcular quais investimentos de renda fixa são mais rentáveis para os iniciantes.

REGRAS:
1. Responda perguntas gerais de educação financeira usando seu conhecimento; a base do cliente serve para personalizar, não para limitar o assunto.
2. Use os dados fornecidos e os valores informados pelo usuário como fatos de entrada; não diga que faltam dados quando for possível explicar a regra, fórmula ou ponto de equilíbrio.
3. Não invente cotações atuais. Se uma taxa variável atual não estiver disponível, sinalize isso e compare com uma fórmula ou limiar usando os números fornecidos.
4. Diferencie estimativas de valores confirmados e informe brevemente as premissas importantes, como prazo, impostos e taxas.
5. Em comparações, considere rentabilidade líquida, liquidez, risco e tributação; conclua conforme o objetivo e perfil do cliente, sem afirmar que um produto é sempre melhor.
6. Para pessoa física, a poupança é isenta de IR e IOF. Não invente exceções a essa regra.
7. Em CDB, IR incide sobre o rendimento conforme o prazo; até 180 dias, use 22,5%. IOF só incide em resgates antes de 30 dias.
8. Responda em português claro, em até 80 palavras. Use no máximo três frases curtas, sem tabela ou lista.
9. Se faltarem cotações atuais, dê a conclusão condicional e diga qual taxa atual deve ser consultada; não encerre apenas dizendo que faltam dados.
10. Para comparar poupança com CDB usando taxas anuais aproximadas, calcule o CDI de equilíbrio como taxa anual da poupança ÷ (1 − alíquota de IR). Exemplo: 8,34% ÷ (1 − 0,225) ≈ 10,76% a.a.; acima disso, o CDB de 100% do CDI tende a render mais líquido, antes de considerar IOF em resgates com menos de 30 dias.
11. Não invente nem cite fontes específicas como se tivesse consultado dados em tempo real.
12. Escreva fórmulas em texto simples e legível, por exemplo: "CDI de equilíbrio = 8,34% dividido por (1 - 0,225), aproximadamente 10,76% ao ano". Não use notação LaTeX, comandos matemáticos, barras invertidas ou subscritos.
"""

# ==========CHAMAR OLLAMA=========
def perguntar(msg):
    prompt = f"""
    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""
    r = request.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "think": "low",
            "stream": False,
            "options": {"num_predict": LIMITE_TOKENS_RESPOSTA},
        },
        timeout=300,
    )
    r.raise_for_status()
    payload = r.json()
    try:
        resposta = payload["message"]["content"]
        motivo_finalizacao = payload.get("done_reason")
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("O Ollama retornou uma resposta em formato inesperado.") from exc
    if not resposta.strip():
        raise ValueError("O Ollama não gerou texto para a resposta.")
    return resposta, motivo_finalizacao

# ==========INTERFACE=========
st.title("Assistente de Investimentos - Ivo")

if pergunta := st.chat_input("Digite sua pergunta sobre investimentos:"):
    st.chat_message("user").write(pergunta)
    with st.spinner("Aguarde enquanto o Ivo processa sua pergunta..."):
        try:
            resposta, motivo_finalizacao = perguntar(pergunta)
        except request.RequestException as exc:
            st.error(f"Não foi possível obter uma resposta do Ollama: {exc}")
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.chat_message("assistant").write(resposta)
            if motivo_finalizacao == "length":
                st.warning(
                    "A resposta atingiu o limite de tokens e pode estar incompleta. "
                    "Tente fazer uma pergunta mais específica."
                )