import base64
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Jack & Jill - Noite nas Arábias",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)


def obter_fundo_css(tipo_tela):
  base_dir = os.path.dirname(os.path.abspath(__file__))

  if tipo_tela == "votacao":
    candidatos = [
        "fundo_votacao.png",
        "fundo_votacao.jpg",
        "fundo_painel.png",
        "fundo_painel.jpg",
        "fundo.png",
        "fundo.jpg",
    ]
  else:
    candidatos = [
        f"fundo_{tipo_tela}.png",
        f"fundo_{tipo_tela}.jpg",
        "fundo.png",
        "fundo.jpg",
    ]

  img_encontrada = None
  for arquivo in candidatos:
    caminho = os.path.join(base_dir, arquivo)
    if os.path.exists(caminho):
      img_encontrada = caminho
      break

  if img_encontrada:
    with open(img_encontrada, "rb") as f:
      data = f.read()
    encoded = base64.b64encode(data).decode()
    ext = img_encontrada.split(".")[-1].lower()
    mime = "png" if ext == "png" else "jpeg"
    return f"""<style>.stApp {{ background-image: linear-gradient(rgba(5, 4, 3, 0.10), rgba(5, 4, 3, 0.20)), url("data:image/{mime};base64,{encoded}"); background-size: cover; background-position: top center !important; background-attachment: fixed; color: #f3e5ab; font-family: 'Helvetica Neue', sans-serif; }}</style>"""
  else:
    return """<style>.stApp { background-color: #090706; color: #f3e5ab; }</style>"""


def img_to_base64(file_path):
  if os.path.exists(file_path):
    with open(file_path, "rb") as f:
      data = f.read()
    encoded = base64.b64encode(data).decode()
    ext = file_path.split(".")[-1].lower()
    mime = "png" if ext == "png" else "jpeg"
    return f"data:image/{mime};base64,{encoded}"
  return ""


if "votos" not in st.session_state:
  st.session_state.votos = []

if "revelado" not in st.session_state:
  st.session_state.revelado = False

if "jurado_logado" not in st.session_state:
  st.session_state.jurado_logado = None

if "categoria_selecionada" not in st.session_state:
  st.session_state.categoria_selecionada = None

# --- Estado da navegação da tela de votação ---
if "idx_comp" not in st.session_state:
  st.session_state.idx_comp = 0

if "idx_crit" not in st.session_state:
  st.session_state.idx_crit = 0

if "fase_atual" not in st.session_state:
  st.session_state.fase_atual = None

if "grupo_atual" not in st.session_state:
  st.session_state.grupo_atual = "Condutor"

try:
  qp = st.query_params
  link_jurado_exclusivo = qp.get("view") == "jurado"

  if "logout" in qp:
    st.session_state.jurado_logado = None
    st.session_state.categoria_selecionada = None
    st.query_params.clear()
    if link_jurado_exclusivo:
      st.query_params["view"] = "jurado"
    st.rerun()

  if "trocar_cat" in qp:
    st.session_state.categoria_selecionada = None
    st.session_state.fase_atual = None
    st.session_state.idx_comp = 0
    st.session_state.idx_crit = 0
    if "cat" in st.query_params:
      del st.query_params["cat"]
    if "trocar_cat" in st.query_params:
      del st.query_params["trocar_cat"]
    st.rerun()

  if "jurado" in qp and not st.session_state.jurado_logado:
    st.session_state.jurado_logado = qp["jurado"]
  if "cat" in qp and not st.session_state.categoria_selecionada:
    st.session_state.categoria_selecionada = qp["cat"]
except Exception:
  link_jurado_exclusivo = False

categorias = {
    "Diamante": {
        "Condutores": ["Alan", "Léo", "William", "Maick", "Luan", "Henrique"],
        "Conduzidas": ["Marluce", "Sidiane", "Sah", "Cléo", "Viih", "Carol"],
    },
    "Platina": {
        "Condutores": ["Jean", "Deivid", "Catriel", "Douglas Clo"],
        "Conduzidas": ["Fabi", "Tefynha", "Nanda", "Cassi"],
    },
    "Ouro": {
        "Condutores": ["Isma", "Jonatan Santos", "Ciro", "Lukas"],
        "Conduzidas": [
            "Joice",
            "Fran",
            "Daia",
            "Marcia",
            "Juliana",
            "Thaizete",
            "Andreza",
            "Julia",
            "Michele",
        ],
    },
    "Prata": {
        "Condutores": [
            "Marcão",
            "Léo",
            "Rogério F",
            "Cleiton",
            "Michel",
            "Alisson",
        ],
        "Conduzidas": [
            "Sabrina",
            "Lolo",
            "Nathalia",
            "Anachris",
            "Ge",
            "Daiane",
            "Lidiana",
            "Dienifer",
            "Shay",
            "Lilica",
        ],
    },
    "Aprendendo a Voar": {
        "Condutores": ["Bruno", "Ivan", "Luis"],
        "Conduzidas": ["Pati", "Sheila", "Michelle", "Carla"],
    },
}

fases_por_categoria = {
    "Aprendendo a Voar": ["Fase Única"],
    "Prata": ["Fase Classificatória", "Fase Final"],
    "Ouro": ["Fase Classificatória", "Fase Final"],
    "Platina": ["Fase 1 (Música 1)", "Fase 2 (Música 2)"],
    "Diamante": ["Fase 1 (Música 1)", "Fase 2 (Música 2)"],
}

criterios_por_categoria = {
    "Aprendendo a Voar": {
        "Conexão e Entrega na Dança": (
            "Atenção ao parceiro, interação, sintonia, presença,"
            " envolvimento e entrega."
        ),
        "Fundamentos e Qualidade da Base": (
            "Ritmo, postura, equilíbrio, condução e resposta, segurança e"
            " movimentos básicos. (Obs: O sambado não será exigido)."
        ),
    },
    "Prata": {
        "Conexão e Resposta": (
            "Conexão, comunicação corporal, condução, resposta, atenção e"
            " sintonia."
        ),
        "Movimentos Característicos e Sambado": (
            "Execução, variedade, segurança, fluidez, qualidade técnica e"
            " integração com a dança."
        ),
        "Criatividade e Musicalidade": (
            "Interpretação musical, ritmo, adaptação, criatividade e"
            " combinação de movimentos."
        ),
    },
    "Ouro": {
        "Conexão e Resposta": (
            "Qualidade da conexão, comunicação corporal, precisão, resposta,"
            " atenção, sintonia e naturalidade."
        ),
        "Movimentos Característicos e Sambado": (
            "Domínio, repertório, técnica, segurança, fluidez, criatividade e"
            " qualidade do sambado."
        ),
        "Criatividade e Musicalidade": (
            "Interpretação, percepção das variações musicais, ritmo, adaptação e"
            " criatividade."
        ),
    },
    "Platina": {
        "Musicalidade e Criatividade": (
            "Interpretação musical, variações, ritmo, criatividade,"
            " originalidade e construção da dança."
        ),
        "Técnica e Finalização": (
            "Postura, equilíbrio, controle corporal, precisão, segurança,"
            " fluidez, movimentos inerentes à dança e acabamento."
        ),
        "Conexão e Resposta": (
            "Clareza da condução, intenção, precisão, resposta, adaptação e"
            " naturalidade."
        ),
    },
    "Diamante": {
        "Musicalidade e Criatividade": (
            "Elevado nível de interpretação, percepção musical, criatividade,"
            " originalidade e soluções durante a dança."
        ),
        "Técnica e Finalização": (
            "Alto nível de exigência em postura, equilíbrio, controle,"
            " precisão, segurança, fluidez e acabamento."
        ),
        "Conexão e Resposta": (
            "Elevado domínio da comunicação corporal, condução, intenção,"
            " resposta, adaptação e naturalidade. (Nível mais elevado de"
            " exigência)."
        ),
    },
}

icones_categoria = {
    "Diamante": ("diamante.png", "💎"),
    "Platina": ("platina.png", "🥈"),
    "Ouro": ("ouro.png", "🥇"),
    "Prata": ("prata.png", "🥈"),
    "Aprendendo a Voar": ("asas.png", "🕊️"),
}

senhas_jurados = {
    "alisson (teste)": "1234",
    "Jurado 1": "1234",
    "Jurado 2": "1234",
    "Jurado 3": "1234",
    "Jurado de Referência": "1234",
}


def obter_classificados(categoria, papel):
  if not st.session_state.votos:
    return []
  df = pd.DataFrame(st.session_state.votos)
  if df.empty:
    return []

  df_class = df[
      (df["categoria"] == categoria)
      & (df["fase"] == "Fase Classificatória")
      & (df["papel"] == papel)
  ]
  if df_class.empty:
    return []

  limite = 8 if categoria == "Prata" else 7

  ranking = df_class.groupby("competidor")["nota"].mean().reset_index()
  ranking = ranking.sort_values(by="nota", ascending=False)
  return ranking.head(limite)["competidor"].tolist()


def formatar_fase(fase):
  if "(" in fase:
    principal, secundaria = fase.split("(", 1)
    return principal.strip().upper(), secundaria.replace(")", "").strip().upper()
  return fase.upper(), "ETAPA ÚNICA"


def registrar_voto(
    jurado,
    categoria,
    fase,
    papel,
    competidor,
    criterio,
    nota,
    justificativa,
):
  for voto in st.session_state.votos:
    if (
        voto["jurado"] == jurado
        and voto["categoria"] == categoria
        and voto["fase"] == fase
        and voto["papel"] == papel
        and voto["competidor"] == competidor
        and voto["criterio"] == criterio
    ):
      voto["nota"] = nota
      voto["justificativa"] = justificativa
      return

  st.session_state.votos.append({
      "jurado": jurado,
      "categoria": categoria,
      "fase": fase,
      "papel": papel,
      "competidor": competidor,
      "criterio": criterio,
      "nota": nota,
      "justificativa": justificativa,
  })


def buscar_nota_salva(jurado, categoria, fase, papel, competidor, criterio):
  for voto in st.session_state.votos:
    if (
        voto["jurado"] == jurado
        and voto["categoria"] == categoria
        and voto["fase"] == fase
        and voto["papel"] == papel
        and voto["competidor"] == competidor
        and voto["criterio"] == criterio
    ):
      return voto["nota"]
  return None


if link_jurado_exclusivo:
  modo = "Painel do Jurado"
  st.markdown(
      '<style>[data-testid="stSidebar"] { display: none !important; }</style>',
      unsafe_allow_html=True,
  )
else:
  st.sidebar.markdown(
      "<h2 style='text-align: center; color: #e5c158;'>✨ PASSION DANCE</h2>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown(
      "<p style='text-align: center; color: #b39b6b; font-size: 12px;'>JACK &"
      " JILL - NOITE NAS ARÁBIAS</p>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown("---")

  modo = st.sidebar.radio(
      "Navegação",
      ["Painel do Jurado", "Painel da Organização", "Telão (Público)"],
      label_visibility="collapsed",
  )

if modo == "Painel do Jurado":
  if st.session_state.jurado_logado is None:
    st.markdown(obter_fundo_css("login"), unsafe_allow_html=True)
  elif st.session_state.categoria_selecionada is None:
    st.markdown(obter_fundo_css("categorias"), unsafe_allow_html=True)
  else:
    st.markdown(obter_fundo_css("votacao"), unsafe_allow_html=True)
elif modo == "Telão (Público)":
  st.markdown(obter_fundo_css("telao"), unsafe_allow_html=True)
else:
  st.markdown(obter_fundo_css("painel"), unsafe_allow_html=True)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@600;700&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 600px !important;
    margin: 0 auto !important;
}

h1, h2, h3 {
    color: #e5c158 !important;
    font-family: 'Georgia', serif;
    text-align: center;
    letter-spacing: 1px;
}

.saudacao-jurado {
    font-family: 'Cinzel Decorative', 'Cinzel', serif !important;
    color: #f3e5ab !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    text-align: center;
    text-shadow: 0 2px 6px rgba(0,0,0,0.8);
    letter-spacing: 1.5px;
    margin-bottom: 2px;
}

div[data-testid="column"]:has(input[type="password"]) {
    max-width: 320px !important; 
    margin: 0 auto !important; 
    float: none !important;
    background: linear-gradient(135deg, rgba(15, 11, 7, 0.95) 0%, rgba(30, 21, 12, 0.98) 100%) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 12px !important;
    padding: 15px 15px 10px 15px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8) !important;
}

.stTextInput div[data-baseweb="input"] {
    background-color: rgba(12, 9, 7, 0.95) !important;
    border: 1px solid rgba(212, 175, 55, 0.45) !important;
    border-radius: 6px !important;
}

.stTextInput div[data-baseweb="input"]:focus-within {
    border: 1px solid rgba(212, 175, 55, 1.0) !important;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.4) !important;
}

.stTextInput input {
    color: #f3e5ab !important;
    background-color: transparent !important;
    padding: 6px 10px !important;
    font-size: 13px !important;
}

.stTextInput input::placeholder {
    color: rgba(243, 229, 171, 0.4) !important;
}

.stButton > button {
    background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(70,55,30,0.95) 100%) !important;
    border: 1px solid rgba(212, 175, 55, 0.6) !important;
    border-radius: 6px !important;
    color: #f3e5ab !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.6) !important;
    padding: 6px 10px !important;
    font-size: 11px !important;
}
.stButton > button:hover {
    background: linear-gradient(180deg, rgba(80,60,30,1) 0%, rgba(140,115,60,1) 100%) !important;
    border: 1px solid rgba(212, 175, 55, 1.0) !important;
    color: #ffffff !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #f2dda0 0%, #c9a24a 100%) !important;
    border: 1px solid #e5c158 !important;
    color: #1a1208 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25) !important;
    padding: 6px 10px !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #ffeeb8 0%, #d9b258 100%) !important;
    color: #1a1208 !important;
}

div[data-testid="stAlert"] {
    background-color: rgba(20, 15, 10, 0.95) !important;
    border: 1px solid rgba(212, 175, 55, 0.6) !important;
    color: #f3e5ab !important;
    border-radius: 6px !important;
}
div[data-testid="stAlert"] p {
    color: #f3e5ab !important;
}

[data-testid="stSidebar"] {
    background-color: rgba(14, 10, 8, 0.96);
    border-right: 1px solid rgba(212, 175, 55, 0.15);
}

.jj-card {
    background: linear-gradient(135deg, rgba(14, 10, 7, 0.94) 0%, rgba(26, 18, 11, 0.96) 100%);
    border: 1px solid rgba(212, 175, 55, 0.45);
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
    padding: 6px 10px;
    margin-bottom: 6px;
}

.jj-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}
.jj-banner-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.jj-banner-icon { font-size: 24px; line-height: 1; }
.jj-banner-icon img { width: 28px; height: 28px; object-fit: contain; }
.jj-label {
    color: #b39b6b;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1px;
}
.jj-categoria {
    font-family: 'Cinzel', 'Georgia', serif;
    color: #f3e5ab;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    line-height: 1.0;
}
.jj-banner-right {
    text-align: right;
    border-left: 1px solid rgba(212, 175, 55, 0.3);
    padding-left: 10px;
}
.jj-fase {
    font-family: 'Cinzel', 'Georgia', serif;
    color: #f3e5ab;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1px;
}
.jj-musica {
    color: #b39b6b;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.jj-avaliando { text-align: center; }
.jj-nome {
    font-family: 'Cinzel', 'Georgia', serif;
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    line-height: 1.0;
    margin: 2px 0 3px 0;
    text-shadow: 0 2px 6px rgba(0,0,0,0.8);
}
.jj-badge {
    display: inline-block;
    border: 1px solid rgba(212, 175, 55, 0.8);
    border-radius: 14px;
    padding: 2px 10px;
    color: #e5c158;
    font-size: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.jj-crit-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
}
.jj-crit-icon {
    width: 28px; height: 28px; min-width: 28px;
    border-radius: 50%;
    border: 1px solid rgba(212, 175, 55, 0.7);
    background: rgba(0,0,0,0.35);
    display: flex; align-items: center; justify-content: center;
    color: #e5c158; font-size: 14px;
}
.jj-contador {
    border: 1px solid rgba(212, 175, 55, 0.7);
    border-radius: 14px;
    padding: 2px 8px;
    color: #e5c158;
    font-size: 10px;
    white-space: nowrap;
}
.jj-crit-nome {
    font-family: 'Cinzel', 'Georgia', serif;
    color: #f3e5ab;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.1;
    margin-top: 1px;
}
.jj-divisor {
    border: none;
    border-top: 1px solid rgba(212, 175, 55, 0.25);
    margin: 4px 0 4px 0;
}
.jj-crit-desc {
    color: #ded2b4;
    font-size: 10px;
    line-height: 1.35;
}
.jj-crit-desc b { color: #e5c158; }

.jj-secao-label {
    color: #b39b6b;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.jj-footer {
    text-align: center;
    margin-top: 6px;
    padding-top: 4px;
    border-top: 1px solid rgba(212, 175, 55, 0.2);
}
.jj-footer-marca {
    color: #e5c158;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.jj-footer-sub {
    color: #8d7a52;
    font-size: 7px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 2px;
}

.stTextArea textarea {
    background-color: rgba(10, 7, 5, 0.9) !important;
    border: 1px solid rgba(212, 175, 55, 0.35) !important;
    border-radius: 6px !important;
    color: #f3e5ab !important;
    font-size: 12px !important;
    height: 45px !important;
}
.stTextArea textarea::placeholder { color: rgba(243, 229, 171, 0.35) !important; }

div[data-testid="stExpander"] {
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 6px !important;
    background: rgba(12, 9, 6, 0.85) !important;
    margin-bottom: 4px !important;
}
div[data-testid="stExpander"] summary p {
    color: #e5c158 !important;
    font-size: 10px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ========================================================================= */
/* CSS UNIVERSAL À PROVA DE FALHAS PARA MOBILE (COMPATÍVEL COM TODOS OS BROWSERS) */
/* ========================================================================= */
@media (max-width: 9999px) {
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        width: 100% !important;
        gap: 6px !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
        width: auto !important;
        padding: 0 !important;
    }

    /* BLOCOS COM EXATAMENTE 2 COLUNAS (Ex: Ajustar Fase/Grupo) */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(2),
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(2) ~ div {
        flex: 1 1 50% !important;
    }

    /* BLOCOS COM EXATAMENTE 3 COLUNAS (Ex: Navegação Anterior/Próximo) */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3),
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) ~ div:nth-child(3) {
        flex: 0 0 30px !important;
        max-width: 30px !important;
        min-width: 30px !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) ~ div:nth-child(2) {
        flex: 1 1 auto !important;
    }

    /* ESTILO ESPECÍFICO PARA OS BOTÕES DAS LATERAIS (Anterior/Próximo) */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) button,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) ~ div:nth-child(3) button {
        width: 30px !important;
        height: 30px !important;
        padding: 0 !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, rgba(20,15,10,0.95) 0%, rgba(40,30,20,0.95) 100%) !important;
    }
    
    /* Ajuste do texto ANT e PRÓX embaixo dos botões para não quebrar */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child:nth-last-child(3) ~ div:nth-child(3) p {
        margin-bottom: 0 !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if modo == "Painel do Jurado":
  if st.session_state.jurado_logado is None:
    st.markdown('<div style="height: 38vh;"></div>', unsafe_allow_html=True)
    col_esq, col_login, col_dir = st.columns([1, 10, 1])
    with col_login:
      login_digitado = st.text_input(
          "Usuário",
          key="login_usuario_jurado",
          placeholder="👤    Usuário",
          label_visibility="collapsed",
      )
      senha_digitada = st.text_input(
          "Senha",
          type="password",
          key="senha_login_jurado",
          placeholder="🔒    Senha",
          label_visibility="collapsed",
      )
      st.markdown('<div style="margin-top: 8px;"></div>', unsafe_allow_html=True)
      if st.button("✧  LOGIN  ✧", type="primary", use_container_width=True):
        usuario_limpo = login_digitado.strip()
        if usuario_limpo in senhas_jurados:
          if senha_digitada == senhas_jurados[usuario_limpo]:
            st.session_state.jurado_logado = usuario_limpo
            st.session_state.categoria_selecionada = None
            st.query_params["jurado"] = usuario_limpo
            if link_jurado_exclusivo:
              st.query_params["view"] = "jurado"
            st.rerun()
          else:
            st.error("❌ Senha incorreta!")
        else:
          st.error("❌ Usuário não encontrado.")
  else:
    if st.session_state.categoria_selecionada is None:
      logout_param = (
          "view=jurado&logout=true" if link_jurado_exclusivo else "logout=true"
      )

      st.markdown(
          f'<div style="position: fixed; top: 40px; right: 12px; z-index: 99999;"><a href="?{logout_param}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center;">← Sair</a></div>',
          unsafe_allow_html=True,
      )

      nome_jurado = st.session_state.jurado_logado
      view_param = "view=jurado&" if link_jurado_exclusivo else ""
      jurado_param = f"jurado={st.session_state.jurado_logado}&"

      cats_info = [
          ("Diamante", "diamante.png", "💎"),
          ("Platina", "platina.png", "🥈"),
          ("Ouro", "ouro.png", "🥇"),
          ("Prata", "prata.png", "🥈"),
          ("Aprendendo a Voar", "asas.png", "🕊️"),
      ]

      cards_html = ""
      for cat_nome, icone_path, emoji_fallback in cats_info:
        img_b64 = img_to_base64(
            os.path.join(os.path.dirname(__file__), icone_path)
        )
        if img_b64:
          icon_html = f'<img src="{img_b64}" class="card-icon"/>'
        else:
          icon_html = f'<span style="font-size: 24px;">{emoji_fallback}</span>'

        target_url = f"?{view_param}{jurado_param}cat={cat_nome}"
        cards_html += f'<a href="{target_url}" class="category-card"><div class="card-left">{icon_html}<span class="card-title">{cat_nome.upper()}</span></div><span class="card-arrow">›</span></a>'

      st.markdown(
          f"""<div style="position: fixed; top: 60%; left: 50%; transform: translate(-50%, -50%); width: 360px; max-width: 90vw; z-index: 99999;"><div style="text-align: center; margin-bottom: 12px;"><div class="saudacao-jurado">Olá, {nome_jurado}!</div><p style="color: #f3e5ab; font-family: 'Helvetica Neue', sans-serif; font-size: 11px; opacity: 0.9; margin-bottom: 12px;">Selecione a categoria que você irá avaliar:</p></div>{cards_html}</div><style>.category-card {{ display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, rgba(15, 11, 7, 0.92) 0%, rgba(30, 21, 12, 0.96) 100%); border: 1px solid rgba(212, 175, 55, 0.5); border-radius: 10px !important; padding: 9px 16px !important; margin-bottom: 8px !important; text-decoration: none !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7); transition: all 0.3s ease; }} .category-card:hover {{ border-color: rgba(212, 175, 55, 1.0); background: linear-gradient(135deg, rgba(25, 18, 12, 0.98) 0%, rgba(45, 33, 19, 1) 100%); }} .card-left {{ display: flex; align-items: center; gap: 15px; }} .card-icon {{ width: 26px !important; height: 26px !important; object-fit: contain; }} .card-title {{ color: #f3e5ab; font-family: 'Georgia', serif; font-size: 12px !important; font-weight: 600; letter-spacing: 2px; }} .card-arrow {{ color: #d4af37; font-size: 16px !important; }}</style>""",
          unsafe_allow_html=True,
      )
    else:
      categoria_escolhida = st.session_state.categoria_selecionada

      logout_url = (
          "?view=jurado&logout=true" if link_jurado_exclusivo else "?logout=true"
      )
      view_str = "view=jurado&" if link_jurado_exclusivo else ""
      jurado_str = f"jurado={st.session_state.jurado_logado}&"
      trocar_url = f"?{view_str}{jurado_str}trocar_cat=true"

      st.markdown(
          f"""<div style="position: fixed; top: 12px; left: 12px; right: 12px; z-index: 99999; display: flex; justify-content: space-between; align-items: center; pointer-events: none;"><a href="{logout_url}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center; pointer-events: auto;">← Sair</a><a href="{trocar_url}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 8.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.15; pointer-events: auto;">Trocar<br>Categoria</a></div>""",
          unsafe_allow_html=True,
      )

      fases_disponiveis = fases_por_categoria[categoria_escolhida]
      if st.session_state.fase_atual not in fases_disponiveis:
        st.session_state.fase_atual = fases_disponiveis[0]
        st.session_state.idx_comp = 0
        st.session_state.idx_crit = 0

      with st.expander("⚙ Ajustar fase e grupo"):
        col_fase, col_grupo = st.columns(2)
        with col_fase:
          nova_fase = st.selectbox(
              "Fase / Etapa",
              fases_disponiveis,
              index=fases_disponiveis.index(st.session_state.fase_atual),
          )
        with col_grupo:
          nova_grupo = st.radio(
              "Grupo",
              ["Condutor", "Conduzida"],
              horizontal=True,
              index=0 if st.session_state.grupo_atual == "Condutor" else 1,
          )

        if (
            nova_fase != st.session_state.fase_atual
            or nova_grupo != st.session_state.grupo_atual
        ):
          st.session_state.fase_atual = nova_fase
          st.session_state.grupo_atual = nova_grupo
          st.session_state.idx_comp = 0
          st.session_state.idx_crit = 0
          st.rerun()

      fase_escolhida = st.session_state.fase_atual
      tipo_selecionado = st.session_state.grupo_atual
      papel_escolhido = (
          "Condutores" if tipo_selecionado == "Condutor" else "Conduzidas"
      )

      arquivo_icone, emoji_icone = icones_categoria.get(
          categoria_escolhida, ("", "✦")
      )
      icone_b64 = img_to_base64(
          os.path.join(os.path.dirname(__file__), arquivo_icone)
      )
      if icone_b64:
        icone_html = f'<img src="{icone_b64}" style="width: 24px; height: 24px; object-fit: contain;"/>'
      else:
        icone_html = emoji_icone

      fase_titulo, fase_sub = formatar_fase(fase_escolhida)

      # Card 1: Banner da Categoria e Fase compacto
      st.markdown(
          f"""<div class="jj-card jj-banner" style="margin-bottom: 6px; padding: 6px 10px;"><div class="jj-banner-left" style="gap: 8px;"><div class="jj-banner-icon">{icone_html}</div><div><div class="jj-label">Categoria</div><div class="jj-categoria">{categoria_escolhida.upper()}</div></div></div><div class="jj-banner-right" style="padding-left: 8px;"><div class="jj-fase">{fase_titulo}</div><div class="jj-musica">{fase_sub}</div></div></div>""",
          unsafe_allow_html=True,
      )

      precisa_filtrar_classificados = (
          fase_escolhida == "Fase Final"
          and categoria_escolhida in ["Prata", "Ouro"]
      )

      if precisa_filtrar_classificados:
        competidores_qualificados = obter_classificados(
            categoria_escolhida, papel_escolhido
        )
      else:
        competidores_qualificados = categorias[categoria_escolhida][
            papel_escolhido
        ]

      if not competidores_qualificados:
        st.warning(
            f"⚠️ A Fase Classificatória para {papel_escolhido} em"
            f" {categoria_escolhida} ainda não possui votos suficientes para"
            " definir automaticamente os classificados da Fase Final."
        )
      else:
        competidores_ordenados = sorted(competidores_qualificados)
        total_comp = len(competidores_ordenados)

        if st.session_state.idx_comp >= total_comp:
          st.session_state.idx_comp = 0
        competidor_escolhido = competidores_ordenados[st.session_state.idx_comp]

        # Card 2: Competidor com botões Anterior/Próximo perfeitamente alinhados
        col_ant, col_nome, col_prox = st.columns([1, 4, 1])

        with col_ant:
          if st.button("‹", key="btn_anterior", use_container_width=True):
            st.session_state.idx_comp = (
                st.session_state.idx_comp - 1
            ) % total_comp
            st.session_state.idx_crit = 0
            st.rerun()

        with col_nome:
          st.markdown(
              f"""<div class="jj-card jj-avaliando" style="margin-bottom: 0; padding: 6px 8px;"><div class="jj-label">Avaliando</div><div class="jj-nome" style="font-size: 20px; margin: 1px 0 3px 0;">{competidor_escolhido}</div><span class="jj-badge" style="padding: 2px 10px; font-size: 8px;">{tipo_selecionado.upper()}</span></div>""",
              unsafe_allow_html=True,
          )

        with col_prox:
          if st.button("›", key="btn_proximo", use_container_width=True):
            st.session_state.idx_comp = (
                st.session_state.idx_comp + 1
            ) % total_comp
            st.session_state.idx_crit = 0
            st.rerun()

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        criterios = criterios_por_categoria[categoria_escolhida]
        lista_criterios = list(criterios.items())
        total_crit = len(lista_criterios)

        if st.session_state.idx_crit >= total_crit:
          st.session_state.idx_crit = 0

        criterio_nome, criterio_desc = lista_criterios[st.session_state.idx_crit]

        # Card 3: Critério compacto
        st.markdown(
            f"""<div class="jj-card" style="margin-bottom: 6px; padding: 8px 10px;"><div class="jj-crit-head"><div class="jj-crit-icon" style="width: 28px; height: 28px; min-width: 28px; font-size: 12px;">♪</div><div style="flex: 1; padding: 0 6px;"><div class="jj-label">Critério</div><div class="jj-crit-nome" style="font-size: 14px;">{criterio_nome}</div></div><div class="jj-contador" style="padding: 1px 6px; font-size: 9px;">{st.session_state.idx_crit + 1} / {total_crit}</div></div><hr class="jj-divisor" style="margin: 4px 0 4px 0;"/><div class="jj-crit-desc" style="font-size: 10px;"><b>O que avaliar:</b> {criterio_desc}</div></div>""",
            unsafe_allow_html=True,
        )

        chave_base = (
            f"{st.session_state.jurado_logado}|{categoria_escolhida}|"
            f"{fase_escolhida}|{papel_escolhido}|{competidor_escolhido}|"
            f"{criterio_nome}"
        )
        chave_nota_input = f"nota_input_{chave_base}"

        if chave_nota_input not in st.session_state:
          nota_salva = buscar_nota_salva(
              st.session_state.jurado_logado,
              categoria_escolhida,
              fase_escolhida,
              papel_escolhido,
              competidor_escolhido,
              criterio_nome,
          )
          st.session_state[chave_nota_input] = (
              str(nota_salva).replace(".", ",") if nota_salva is not None else ""
          )

        # Card 4: Sua Nota compacto
        st.markdown(
            """<style>.st-key-nota_card { background: linear-gradient(135deg, rgba(14, 10, 7, 0.94) 0%, rgba(26, 18, 11, 0.96) 100%); border: 1px solid rgba(212, 175, 55, 0.45); border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.6); padding: 6px 10px 8px 10px; margin-bottom: 6px; } .st-key-nota_card div[data-baseweb="input"] { background: rgba(10, 7, 5, 0.92) !important; border: 1px solid rgba(212, 175, 55, 0.55) !important; border-radius: 6px !important; min-height: 38px !important; } .st-key-nota_card div[data-baseweb="input"]:focus-within { border-color: rgba(212, 175, 55, 1) !important; box-shadow: 0 0 8px rgba(212, 175, 55, 0.25) !important; } .st-key-nota_card input { color: #f3e5ab !important; background: transparent !important; font-size: 15px !important; text-align: center !important; padding: 6px 10px !important; } .st-key-nota_card input::placeholder { color: rgba(243, 229, 171, 0.4) !important; }</style>""",
            unsafe_allow_html=True,
        )

        with st.container(key="nota_card"):  
          st.markdown(
              '<div class="jj-secao-label">Sua Nota</div>',
              unsafe_allow_html=True,
          )
          nota_digitada_str = st.text_input(
              "SUA NOTA",
              value=st.session_state[chave_nota_input],
              key=f"txt_nota_{chave_base}",
              placeholder="Digite sua nota de 1 a 10...",
              max_chars=5,
              label_visibility="collapsed",
          )

        # Card 5: Comentários compacto
        st.markdown(
            f'<div class="jj-card" style="margin-bottom: 6px; padding: 6px 10px;"><div class="jj-secao-label">Comentários (Opcional)</div>',
            unsafe_allow_html=True,
        )
        chave_comentario = f"coment_{chave_base}"
        comentario = st.text_area(
            "COMENTÁRIOS (OPCIONAL)",
            key=chave_comentario,
            placeholder="Deixe seu comentário aqui...",
            max_chars=300,
            height=45,
            label_visibility="collapsed",
        )
        st.markdown(
            f"<div style='text-align:right; color:#8d7a52; font-size:9px;"
            f" margin-top:1px;'>{len(comentario)}/300</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)

        # Botão Enviar Avaliação compacto
        if st.button(
            "➤  ENVIAR AVALIAÇÃO",
            type="primary",
            use_container_width=True,
            key=f"enviar_{chave_base}",
        ):
          nota_limpa = nota_digitada_str.strip()
          nota_normalizada = nota_limpa.replace(",", ".")
          if not nota_limpa:
            st.error("❌ Digite uma nota antes de enviar.")
          else:
            try:
              val_nota = float(nota_normalizada)
              if not (1 <= val_nota <= 10):
                st.error("❌ A nota deve ser entre 1 e 10.")
              else:
                registrar_voto(
                    st.session_state.jurado_logado,
                    categoria_escolhida,
                    fase_escolhida,
                    papel_escolhido,
                    competidor_escolhido,
                    criterio_nome,
                    val_nota,
                    comentario,
                )
                st.session_state[chave_nota_input] = nota_limpa.replace(".", ",")

                if st.session_state.idx_crit + 1 < total_crit:
                  st.session_state.idx_crit += 1
                  st.toast(
                      f"✨ Nota registrada para {competidor_escolhido} —"
                      f" {criterio_nome}"
                  )
                else:
                  st.session_state.idx_crit = 0
                  st.session_state.idx_comp = (
                      st.session_state.idx_comp + 1
                  ) % total_comp
                  st.toast(
                      f"🏅 Avaliação de {competidor_escolhido} concluída!"
                  )
                st.rerun()
            except ValueError:
              st.error("❌ Digite um valor numérico válido para a nota.")

        # Rodapé compacto
        st.markdown(
            """<div class="jj-footer" style="margin-top: 6px; padding-top: 4px;"><div style="color:#b39b6b; font-size:9px; margin-bottom: 1px;">✦</div><div class="jj-footer-marca" style="font-size: 9px; letter-spacing: 3px;">Passion Dance</div><div class="jj-footer-sub" style="font-size: 7px; letter-spacing: 1px;">Jack and Jill · Noite nas Arábias</div></div>""",
            unsafe_allow_html=True,
        )

elif modo == "Painel da Organização":
  st.title("📋 Painel da Organização")
  with st.container(border=True):
    senha_digitada = st.text_input(
        "Digite a senha de acesso da organização", type="password"
    )
  SENHA_MESTRE = "danca123"

  if senha_digitada == SENHA_MESTRE:
    st.success("🔓 Acesso autorizado!")
    if not st.session_state.votos:
      st.warning("Ainda não há votos registrados na competição.")
    else:
      df_votos = pd.DataFrame(st.session_state.votos)
      st.markdown("### Auditoria Completa de Notas e Justificativas")
      st.dataframe(df_votos, use_container_width=True)
  elif senha_digitada != "":
    st.error("❌ Senha incorreta!")

else:
  st.title("🏆 Telão da Competição — Noite nas Arábias")

  with st.sidebar:
    st.markdown("---")
    st.markdown("### Controle do Telão")
    revelar_tudo = st.checkbox(
        "Revelar Últimas Notas e Resultados", value=st.session_state.revelado
    )
    st.session_state.revelado = revelar_tudo

  if not st.session_state.votos:
    st.info(
        "💡 Aguardando o envio dos votos pelos jurados. As categorias aparecerão"
        " aqui."
    )

  nomes_abas = list(categorias.keys())
  abas = st.tabs(nomes_abas)

  if st.session_state.votos:
    df_votos = pd.DataFrame(st.session_state.votos)
  else:
    df_votos = pd.DataFrame(
        columns=[
            "jurado",
            "categoria",
            "fase",
            "papel",
            "competidor",
            "criterio",
            "nota",
            "justificativa",
        ]
    )

  for i, categoria_nome in enumerate(nomes_abas):
    with abas[i]:
      st.markdown(f"## 📊 Categoria: {categoria_nome}")
      df_cat = df_votos[df_votos["categoria"] == categoria_nome]

      if df_cat.empty:
        st.info("Nenhum voto registrado ainda para esta categoria.")
      else:
        fases_da_cat = fases_por_categoria[categoria_nome]

        if len(fases_da_cat) > 1:
          fase_abas = st.tabs(fases_da_cat)
          fases_iter = list(zip(fases_da_cat, fase_abas))
        else:
          fases_iter = [(fases_da_cat[0], None)]

        for fase_nome, fase_aba in iter(fases_iter):
          if fase_aba is not None:
            container = fase_aba
          else:
            container = st.container()

          with container:
            if len(fases_da_cat) > 1:
              st.markdown(f"### Etapa: {fase_nome}")

            df_fase = df_cat[df_cat["fase"] == fase_nome]
            sub_abas = st.tabs(["Condutores", "Conduzidas"])
            papeis = ["Condutores", "Conduzidas"]

            for j, papel_nome in enumerate(papeis):
              with sub_abas[j]:
                st.markdown(f"#### Divisão: {papel_nome}")
                df_papel = df_fase[df_fase["papel"] == papel_nome]

                if df_papel.empty:
                  st.info(
                      f"Sem votos para {papel_nome} nesta etapa/fase ainda."
                  )
                else:
                  if not st.session_state.revelado:
                    indices_para_ignorar = []
                    for comp in df_papel["competidor"].unique():
                      temp_df = df_papel[df_papel["competidor"] == comp]
                      if not temp_df.empty:
                        indices_para_ignorar.append(temp_df.index[-1])
                    df_calculo = df_papel.drop(indices_para_ignorar)
                  else:
                    df_calculo = df_papel.copy()

                  if not df_calculo.empty:
                    ranking = (
                        df_calculo.groupby("competidor")["nota"]
                        .mean()
                        .reset_index()
                    )
                    ranking.columns = ["Competidor", "Média da Etapa"]
                    ranking = ranking.sort_values(
                        by="Média da Etapa", ascending=False
                    ).reset_index(drop=True)
                    ranking.index = ranking.index + 1

                    st.markdown("##### 🏆 Ranking da Etapa")
                    st.dataframe(ranking, use_container_width=True)
                  else:
                    st.warning("Aguardando mais votos para o ranking parcial.")

                  st.markdown("##### 📝 Histórico de Notas da Etapa")
                  df_exibicao_papel = df_papel[
                      [
                          "jurado",
                          "categoria",
                          "fase",
                          "papel",
                          "competidor",
                          "criterio",
                          "nota",
                      ]
                  ].copy()

                  if not st.session_state.revelado:
                    indices_para_mascarar = []
                    for comp in df_exibicao_papel["competidor"].unique():
                      temp_df = df_exibicao_papel[
                          df_exibicao_papel["competidor"] == comp
                      ]
                      if not temp_df.empty:
                        indices_para_mascarar.append(temp_df.index[-1])

                    df_exibicao_papel["nota"] = df_exibicao_papel["nota"].astype(
                        str
                    )
                    df_exibicao_papel.loc[indices_para_mascarar, "nota"] = (
                        "🔒 [Nota Secreta Oculta]"
                    )

                  st.dataframe(df_exibicao_papel, use_container_width=True)

        if categoria_nome in ["Platina", "Diamante"]:
          st.divider()
          st.markdown(
              "### 🌟 Classificação Geral Acumulada (Fase 1 + Fase 2 Somadas)"
          )
          df_cat_geral = df_cat.copy()
          if not df_cat_geral.empty:
            sub_abas_geral = st.tabs(
                ["Condutores Geral", "Conduzidas Geral"]
            )
            for g_idx, g_papel in enumerate(["Condutores", "Conduzidas"]):
              with sub_abas_geral[g_idx]:
                df_g = df_cat_geral[df_cat_geral["papel"] == g_papel]
                if not df_g.empty:
                  fase_means = (
                      df_g.groupby(["competidor", "fase"])["nota"]
                      .mean()
                      .reset_index()
                  )
                  total_score = (
                      fase_means.groupby("competidor")["nota"]
                      .sum()
                      .reset_index()
                  )
                  total_score.columns = [
                      "Competidor",
                      "Pontuação Total Acumulada",
                  ]
                  total_score = total_score.sort_values(
                      by="Pontuação Total Acumulada", ascending=False
                  ).reset_index(drop=True)
                  total_score.index = total_score.index + 1
                  st.dataframe(total_score, use_container_width=True)
                else:
                  st.info("Aguardando votos em ambas as fases.")