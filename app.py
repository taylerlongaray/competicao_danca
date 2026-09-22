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

if "rascunho_votos" not in st.session_state:
    st.session_state.rascunho_votos = []

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

configuracao_jurados = {
    "adri": {
        "nome": "Adri Santos",
        "senha": "6153",
        "permissoes": [
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Aprendendo a Voar", "papel": "Condutores", "criterios": ["Conexão e entrega na dança"]},
            {"categoria": "Diamante", "papel": "Condutores", "criterios": ["Conexão e Resposta"]}
        ]
    },
    "alan": {
        "nome": "Alan Demarch",
        "senha": "7391",
        "permissoes": [
            {"categoria": "Platina", "papel": "Condutores", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Ouro", "papel": "Condutores", "criterios": ["Musicalidade/Criatividade"]}
        ]
    },
    "alex": {
        "nome": "Alex Alves",
        "senha": "4827",
        "permissoes": "TODAS_GLOBAL",
        "criterio_global": "Jurado de Avaliação Global / Referência"
    },
    "bel": {
        "nome": "Bel Amaro",
        "senha": "2648",
        "permissoes": [
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Movimentos característicos e sambado"]}
        ]
    },
    "cassiano/luan": {
        "nome": "Cassiano Fontana / Luan Ruduit",
        "senha": "8516",
        "permissoes": [
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Movimentos característicos e sambado"]}
        ]
    },
    "claudia": {
        "nome": "Claudia Papke",
        "senha": "5274",
        "permissoes": [
            {"categoria": "Aprendendo a Voar", "papel": "Conduzidas", "criterios": ["Conexão e entrega na dança"]},
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Técnica e Conexão"]},
            {"categoria": "Diamante", "papel": "Conduzidas", "criterios": ["Conexão e Resposta"]}
        ]
    },
    "cleo": {
        "nome": "Cléo Santanna",
        "senha": "6835",
        "permissoes": [
            {"categoria": "Platina", "papel": "Conduzidas", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Ouro", "papel": "Conduzidas", "criterios": ["Musicalidade/Criatividade"]}
        ]
    },
    "daiani": {
        "nome": "Daiani Rodrigues",
        "senha": "9146",
        "permissoes": [
            {"categoria": "Diamante", "papel": "Conduzidas", "criterios": ["Técnica e finalização"]},
            {"categoria": "Platina", "papel": "Conduzidas", "criterios": ["Técnica e finalização"]},
            {"categoria": "Ouro", "papel": "Conduzidas", "criterios": ["Conexão e resposta"]}
        ]
    },
    "joel": {
        "nome": "Joel Trevisan",
        "senha": "3572",
        "permissoes": [
            {"categoria": "Aprendendo a Voar", "papel": "Condutores", "criterios": ["Fundamentos e qualidade base"]},
            {"categoria": "Ouro", "papel": "Condutores", "criterios": ["Movimentos característicos e sambado"]}
        ]
    },
    "lika": {
        "nome": "Lika",
        "senha": "7461",
        "permissoes": [
            {"categoria": "Ouro", "papel": "Conduzidas", "criterios": ["Movimentos característicos e sambado"]},
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Musicalidade/Criatividade"]}
        ]
    },
    "maick": {
        "nome": "Maick Martins",
        "senha": "2385",
        "permissoes": [
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Técnica e Conexão"]}
        ]
    },
    "nilson": {
        "nome": "Nilson Leivas",
        "senha": "8614",
        "permissoes": [
            {"categoria": "Diamante", "papel": "Conduzidas", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Platina", "papel": "Conduzidas", "criterios": ["Conexão e Resposta"]},
            {"categoria": "Ouro", "papel": "Condutores", "criterios": ["Conexão e resposta"]}
        ]
    },
    "wagner": {
        "nome": "Wagner Camargo",
        "senha": "4296",
        "permissoes": [
            {"categoria": "Diamante", "papel": "Condutores", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Platina", "papel": "Condutores", "criterios": ["Técnica e finalização"]}
        ]
    },
    "william": {
        "nome": "William Ferreira",
        "senha": "5738",
        "permissoes": [
            {"categoria": "Platina", "papel": "Condutores", "criterios": ["Conexão e Resposta"]},
            {"categoria": "Aprendendo a Voar", "papel": "Conduzidas", "criterios": ["Fundamentos e qualidade base"]}
        ]
    }
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
    for voto in st.session_state.rascunho_votos:
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

    st.session_state.rascunho_votos.append({
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
    for voto in st.session_state.rascunho_votos:
        if (
            voto["jurado"] == jurado
            and voto["categoria"] == categoria
            and voto["fase"] == fase
            and voto["papel"] == papel
            and voto["competidor"] == competidor
            and voto["criterio"] == criterio
        ):
            return voto["nota"]
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

.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(12, 9, 7, 0.95) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 8px !important;
    color: #f3e5ab !important;
}
.stSelectbox div[data-baseweb="select"] span {
    color: #f3e5ab !important;
    font-family: 'Cinzel', 'Georgia', serif !important;
    font-weight: 600 !important;
}
.stSelectbox svg {
    fill: #e5c158 !important;
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
                usuario_limpo = login_digitado.strip().lower()
                if usuario_limpo in configuracao_jurados:
                    if senha_digitada == configuracao_jurados[usuario_limpo]["senha"]:
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
        dados_jurado = configuracao_jurados.get(st.session_state.jurado_logado, {"nome": st.session_state.jurado_logado, "permissoes": "TODAS"})
        nome_jurado = dados_jurado["nome"]
        permissoes_jurado = dados_jurado["permissoes"]

        if st.session_state.categoria_selecionada is None:
            logout_param = (
                "view=jurado&logout=true" if link_jurado_exclusivo else "logout=true"
            )

            st.markdown(
                f'<div style="position: fixed; top: 40px; right: 12px; z-index: 99999;"><a href="?{logout_param}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center;">← Sair</a></div>',
                unsafe_allow_html=True,
            )

            view_param = "view=jurado&" if link_jurado_exclusivo else ""
            jurado_param = f"jurado={st.session_state.jurado_logado}&"

            cats_info_todas = [
                ("Diamante", "diamante.png", "💎"),
                ("Platina", "platina.png", "🥈"),
                ("Ouro", "ouro.png", "🥇"),
                ("Prata", "prata.png", "🥈"),
                ("Aprendendo a Voar", "asas.png", "🕊️"),
            ]

            if isinstance(permissoes_jurado, str):
                cats_info = cats_info_todas
            else:
                categorias_permitidas = {p["categoria"] for p in permissoes_jurado}
                cats_info = [c for c in cats_info_todas if c[0] in categorias_permitidas]

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

            if isinstance(permissoes_jurado, str):
                papeis_permitidos_categoria = ["Condutores", "Conduzidas"]
            else:
                papeis_permitidos_categoria = [p["papel"] for p in permissoes_jurado if p["categoria"] == categoria_escolhida]

            with st.expander("⚙ Ajustar fase e grupo"):
                col_fase, col_grupo = st.columns(2)
                with col_fase:
                    nova_fase = st.selectbox(
                        "Fase / Etapa",
                        fases_disponiveis,
                        index=fases_disponiveis.index(st.session_state.fase_atual),
                    )
                with col_grupo:
                    if len(papeis_permitidos_categoria) == 1:
                        papel_unico = papeis_permitidos_categoria[0]
                        nova_grupo = "Condutor" if papel_unico == "Condutores" else "Conduzida"
                        st.markdown(f"<div style='font-size:11px; color:#e5c158; padding-top:15px;'>Grupo: <b>{nova_grupo}</b></div>", unsafe_allow_html=True)
                    else:
                        nova_grupo = st.radio(
                            "Grupo",
                            ["Condutor" if p == "Condutores" else "Conduzida" for p in papeis_permitidos_categoria],
                            horizontal=True,
                        )

                if (
                    nova_fase != st.session_state.fase_atual
                    or nova_grupo != st.session_state.grupo_atual
                ):
                    st.session_state.fase_atual = nova_fase
                    st.session_state.grupo_atual = nova_grupo
                    st.session_state.idx_comp = 0
                    st.session_state.idx_crit = 0
                    # Limpa a tela de revisão se trocar de grupo/fase
                    rev_key = f"revisao_ativa_{st.session_state.jurado_logado}_{categoria_escolhida}_{nova_fase}_{nova_grupo}"
                    if rev_key in st.session_state:
                        del st.session_state[rev_key]
                    st.rerun()

            fase_escolhida = st.session_state.fase_atual
            tipo_selecionado = st.session_state.grupo_atual
            papel_escolhido = (
                "Condutores" if tipo_selecionado == "Condutor" else "Conduzidas"
            )

            # Chave de revisão específica para este jurado, categoria, fase e papel
            revisao_key = f"revisao_ativa_{st.session_state.jurado_logado}_{categoria_escolhida}_{fase_escolhida}_{papel_escolhido}"

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

            st.markdown(
                f"""<div class="jj-card jj-banner" style="margin-bottom: 6px; padding: 6px 10px;"><div class="jj-banner-left" style="gap: 8px;"><div class="jj-banner-icon">{icone_html}</div><div><div class="jj-label">Categoria</div><div class="jj-categoria">{categoria_escolhida.upper()}</div></div></div><div class="jj-banner-right" style="padding-left: 8px;"><div class="jj-fase">{fase_titulo}</div><div class="jj-musica">{fase_sub}</div></div></div>""",
                unsafe_allow_html=True,
            )

            # Se o jurado já concluiu todos os competidores, exibe a tela de revisão/confirmação final
            if st.session_state.get(revisao_key, False):
                st.markdown(
                    f"""<div class="jj-card jj-avaliando" style="padding: 15px; text-align: center; margin-bottom: 10px;">
                        <div class="jj-label" style="color: #e5c158; font-size: 11px;">Avaliação Concluída!</div>
                        <div class="jj-nome" style="font-size: 21px; margin: 8px 0;">Resumo dos seus rascunhos</div>
                        <p style="color: #ded2b4; font-size: 11px; margin-bottom: 10px;">Você avaliou todos os competidores de <b>{papel_escolhido}</b> ({categoria_escolhida}). Reveja abaixo ou envie diretamente para o telão:</p>
                    </div>""",
                    unsafe_allow_html=True,
                )

                # Mostrar tabela de rascunhos deste jurado para esta categoria/fase/papel
                rascunhos_atuais = [
                    v for v in st.session_state.rascunho_votos
                    if v["jurado"] == st.session_state.jurado_logado
                    and v["categoria"] == categoria_escolhida
                    and v["fase"] == fase_escolhida
                    and v["papel"] == papel_escolhido
                ]

                if rascunhos_atuais:
                    df_rasc = pd.DataFrame(rascunhos_atuais)[["competidor", "criterio", "nota", "justificativa"]]
                    df_rasc.columns = ["Participante", "Critério", "Nota", "Comentário"]
                    st.dataframe(df_rasc, use_container_width=True, hide_index=True)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️ REVISAR NOTAS", use_container_width=True):
                        st.session_state[revisao_key] = False
                        st.session_state.idx_comp = 0
                        st.session_state.idx_crit = 0
                        st.rerun()
                with col_btn2:
                    if st.button("🚀 ENVIAR TUDO AO TELÃO", type="primary", use_container_width=True):
                        # Transfere os rascunhos para os votos oficiais do telão
                        for v_rasc in rascunhos_atuais:
                            encontrado = False
                            for v_oficial in st.session_state.votos:
                                if (
                                    v_oficial["jurado"] == v_rasc["jurado"] and
                                    v_oficial["categoria"] == v_rasc["categoria"] and
                                    v_oficial["fase"] == v_rasc["fase"] and
                                    v_oficial["papel"] == v_rasc["papel"] and
                                    v_oficial["competidor"] == v_rasc["competidor"] and
                                    v_oficial["criterio"] == v_rasc["criterio"]
                                ):
                                    v_oficial["nota"] = v_rasc["nota"]
                                    v_oficial["justificativa"] = v_rasc["justificativa"]
                                    encontrado = True
                                    break
                            if not encontrado:
                                st.session_state.votos.append(v_rasc.copy())
                        
                        st.success("✨ Notas enviadas com sucesso para o Telão!")
                        st.balloons()
            else:
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

                    st.markdown(
                        f"""<div class="jj-card jj-avaliando" style="margin-bottom: 4px; padding: 6px 10px;">
                            <div class="jj-label">Selecionar Competidor</div>
                            <span class="jj-badge" style="padding: 2px 10px; font-size: 8px; margin-top: 2px;">{tipo_selecionado.upper()}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                    competidor_escolhido = st.selectbox(
                        "Competidor",
                        options=competidores_ordenados,
                        index=st.session_state.idx_comp,
                        key="select_competidor_movel",
                        label_visibility="collapsed"
                    )

                    novo_idx = competidores_ordenados.index(competidor_escolhido)
                    if novo_idx != st.session_state.idx_comp:
                        st.session_state.idx_comp = novo_idx
                        st.session_state.idx_crit = 0
                        st.rerun()

                    st.markdown(
                        f"""<div class="jj-card jj-avaliando" style="margin-bottom: 6px; padding: 8px 10px; background: linear-gradient(135deg, rgba(20, 15, 10, 0.98) 0%, rgba(40, 30, 18, 0.98) 100%);">
                            <div class="jj-label" style="color: #e5c158;">Estado Atual</div>
                            <div class="jj-nome" style="font-size: 19px; margin: 2px 0;">Avaliando {competidor_escolhido}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                    if permissoes_jurado == "TODAS_GLOBAL":
                        criterios = {dados_jurado["criterio_global"]: "Avaliação global e de referência da dança do participante."}
                    else:
                        criterios_permitidos_nomes = []
                        for p in permissoes_jurado:
                            if p["categoria"] == categoria_escolhida and p["papel"] == papel_escolhido:
                                criterios_permitidos_nomes.extend(p["criterios"])
                        
                        todos_crit_cat = criterios_por_categoria[categoria_escolhida]
                        criterios = {k: v for k, v in todos_crit_cat.items() if k in criterios_permitidos_nomes}

                    if not criterios:
                        st.warning(f"⚠️ Não possui critérios atribuídos para avaliar {papel_escolhido} na categoria {categoria_escolhida}.")
                        st.stop()

                    lista_criterios = list(criterios.items())
                    total_crit = len(lista_criterios)

                    if st.session_state.idx_crit >= total_crit:
                        st.session_state.idx_crit = 0

                    criterio_nome, criterio_desc = lista_criterios[st.session_state.idx_crit]

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

                    st.markdown(
                        """<style>
                        .st-key-coment_card { 
                            background: linear-gradient(135deg, rgba(14, 10, 7, 0.94) 0%, rgba(26, 18, 11, 0.96) 100%); 
                            border: 1px solid rgba(212, 175, 55, 0.45); 
                            border-radius: 10px; 
                            box-shadow: 0 4px 12px rgba(0,0,0,0.6); 
                            padding: 8px 10px 10px 10px; 
                            margin-bottom: 6px; 
                        } 
                        .st-key-coment_card textarea { 
                            background-color: rgba(10, 7, 5, 0.92) !important; 
                            border: 1px solid rgba(212, 175, 55, 0.35) !important; 
                            border-radius: 6px !important; 
                            color: #f3e5ab !important; 
                            font-size: 12px !important; 
                            height: 45px !important; 
                            margin-bottom: 0px !important;
                        } 
                        .st-key-coment_card textarea::placeholder { 
                            color: rgba(243, 229, 171, 0.35) !important; 
                        }
                        .st-key-coment_card p {
                            margin: 0 !important;
                            padding: 0 !important;
                        }
                        </style>""",
                        unsafe_allow_html=True,
                    )

                    chave_comentario = f"coment_{chave_base}"
                    
                    with st.container(key="coment_card"):
                        st.markdown(
                            '<div class="jj-secao-label" style="margin-bottom: 4px;">Comentários:</div>',
                            unsafe_allow_html=True,
                        )
                        comentario = st.text_area(
                            "COMENTÁRIOS",
                            key=chave_comentario,
                            placeholder="Deixe seu comentário aqui...",
                            max_chars=300,
                            height=45,
                            label_visibility="collapsed",
                        )
                        st.markdown(
                            f"<div style='text-align:right; color:#8d7a52; font-size:9px; margin-top:-8px;'>{len(comentario)}/300</div>",
                            unsafe_allow_html=True,
                        )

                    if st.button(
                        "➤  GUARDAR E PRÓXIMO",
                        type="primary",
                        use_container_width=True,
                        key=f"enviar_{chave_base}",
                    ):
                        nota_limpa = nota_digitada_str.strip()
                        nota_normalizada = nota_limpa.replace(",", ".")
                        if not nota_limpa:
                            st.error("❌ Digite uma nota antes de continuar.")
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

                                    # Verifica se é o último critério do último competidor
                                    is_ultimo_criterio = (st.session_state.idx_crit + 1 >= total_crit)
                                    is_ultimo_competidor = (st.session_state.idx_comp + 1 >= total_comp)

                                    if is_ultimo_criterio and is_ultimo_competidor:
                                        # Chegou ao fim de todos os competidores desta categoria/papel! Ativa a revisão
                                        st.session_state[revisao_key] = True
                                        st.toast(f"🎉 Avaliação de {papel_escolhido} concluída! Revise suas notas.")
                                    elif is_ultimo_criterio:
                                        st.session_state.idx_crit = 0
                                        st.session_state.idx_comp += 1
                                        st.toast(f"✨ Avançando para o próximo competidor...")
                                    else:
                                        st.session_state.idx_crit += 1
                                        st.toast(f"✨ Próximo critério...")
                                    
                                    st.rerun()
                            except ValueError:
                                st.error("❌ Digite um valor numérico válido para a nota.")

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
            st.warning("Ainda não há votos enviados ao telão.")
        else:
            df_votos = pd.DataFrame(st.session_state.votos)
            st.markdown("### Auditoria Completa de Notas Oficiais")
            st.dataframe(df_votos, use_container_width=True)
    elif senha_digitada != "":
        st.error("❌ Senha incorreta!")

else:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h1 style='font-family: "Cinzel", Georgia, serif; color: #e5c158; font-size: 32px; letter-spacing: 3px; margin-bottom: 0;'>JACK & JILL</h1>
            <h3 style='font-family: "Cinzel", Georgia, serif; color: #f3e5ab; font-size: 18px; letter-spacing: 2px; margin-top: 5px;'>NOITE NAS ARÁBIAS — TELÃO</h3>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown("### Controle do Telão")
        revelar_tudo = st.checkbox("Revelar Notas e Resultados Finais", value=st.session_state.revelado)
        st.session_state.revelado = revelar_tudo

    if not st.session_state.votos:
        st.info("💡 Aguardando o envio oficial dos votos pelos jurados. Os resultados aparecerão aqui em tempo real.")
    else:
        df_votos = pd.DataFrame(st.session_state.votos)
        
        nomes_abas = list(categorias.keys())
        abas = st.tabs([f"💎 {c}" if c=="Diamante" else f"🥈 {c}" if c=="Platina" else f"🥇 {c}" if c=="Ouro" else f"🥈 {c}" if c=="Prata" else f"🕊️ {c}" for c in nomes_abas])

        for i, categoria_nome in enumerate(nomes_abas):
            with abas[i]:
                st.markdown(f"<h2 style='text-align: center; color: #e5c158; font-family: Cinzel, Georgia, serif; letter-spacing: 2px; margin: 20px 0;'>RESULTADO — {categoria_nome.upper()}</h2>", unsafe_allow_html=True)
                
                df_cat = df_votos[df_votos["categoria"] == categoria_nome]
                if df_cat.empty:
                    st.info(f"Nenhum voto confirmado ainda para a categoria {categoria_nome}.")
                    continue

                fases_da_cat = fases_por_categoria[categoria_nome]
                
                if len(fases_da_cat) > 1:
                    col_fase1, col_fase2 = st.columns(2)
                    fases_cols = [(fases_da_cat[0], col_fase1), (fases_da_cat[1], col_fase2)]
                else:
                    fases_cols = [(fases_da_cat[0], st.container())]

                for fase_nome, container_fase in fases_cols:
                    with container_fase:
                        fase_titulo, fase_sub = formatar_fase(fase_nome)
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(20,15,10,0.95) 0%, rgba(40,30,18,0.95) 100%); border: 1px solid rgba(212,175,55,0.6); border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 15px;">
                                <div style="font-family: Cinzel, Georgia, serif; color: #f3e5ab; font-size: 15px; font-weight: bold; letter-spacing: 1px;">— {fase_titulo} —</div>
                                <div style="color: #b39b6b; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase;">{fase_sub}</div>
                            </div>
                        """, unsafe_allow_html=True)

                        df_fase = df_cat[df_cat["fase"] == fase_nome]
                        
                        c_cond, c_condurz = st.columns(2)
                        papeis_info = [("Condutores", c_cond), ("Conduzidas", c_condurz)]
                        
                        for papel_nome, col_papel in papeis_info:
                            with col_papel:
                                st.markdown(f"<h4 style='text-align: center; color: #e5c158; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;'>{papel_nome}</h4>", unsafe_allow_html=True)
                                
                                df_papel = df_fase[df_fase["papel"] == papel_nome]
                                if df_papel.empty:
                                    st.markdown("<p style='text-align: center; color: #8d7a52; font-size: 10px;'>Aguardando envio...</p>", unsafe_allow_html=True)
                                else:
                                    df_notas_jurado = df_papel.groupby(["competidor", "jurado"])["nota"].mean().reset_index()
                                    pivot_df = df_notas_jurado.pivot(index="competidor", columns="jurado", values="nota").reset_index()
                                    
                                    jurados_cols = [c for c in pivot_df.columns if c != "competidor"]
                                    mapping_jurados = {j: f"J{idx+1}" for idx, j in enumerate(sorted(jurados_cols))}
                                    pivot_df = pivot_df.rename(columns=mapping_jurados)
                                    j_cols_renomeadas = list(mapping_jurados.values())
                                    
                                    pivot_df["TOTAL"] = pivot_df[j_cols_renomeadas].sum(axis=1)
                                    
                                    pivot_df = pivot_df.sort_values(by="TOTAL", ascending=False).reset_index(drop=True)
                                    pivot_df.index = pivot_df.index + 1
                                    pivot_df.index.name = "#"
                                    pivot_df = pivot_df.reset_index()
                                    
                                    pivot_df["CLASS."] = [f"{idx}º" for idx in pivot_df.index]
                                    pivot_df = pivot_df.rename(columns={"competidor": "PARTICIPANTE"})
                                    
                                    cols_finais = ["#", "PARTICIPANTE"] + j_cols_renomeadas + ["TOTAL", "CLASS."]
                                    cols_finais_existentes = [c for c in cols_finais if c in pivot_df.columns]
                                    
                                    tabela_exibicao = pivot_df[cols_finais_existentes]
                                    
                                    for col in j_cols_renomeadas + ["TOTAL"]:
                                        if col in tabela_exibicao.columns:
                                            tabela_exibicao[col] = tabela_exibicao[col].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "-")

                                    st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)

                if categoria_nome in ["Platina", "Diamante"]:
                    st.markdown("---")
                    st.markdown("<h3 style='text-align: center; color: #e5c158; font-family: Cinzel, Georgia, serif; font-size: 16px;'>🌟 Classificação Geral Acumulada (Fase 1 + Fase 2)</h3>", unsafe_allow_html=True)
                    df_cat_geral = df_cat.copy()
                    if not df_cat_geral.empty:
                        g_cond, g_condurz = st.columns(2)
                        for g_idx, (g_papel, col_g) in enumerate([("Condutores", g_cond), ("Conduzidas", g_condurz)]):
                            with col_g:
                                st.markdown(f"<h4 style='text-align: center; color: #f3e5ab; font-size: 11px; text-transform: uppercase;'>Geral - {g_papel}</h4>", unsafe_allow_html=True)
                                df_g = df_cat_geral[df_cat_geral["papel"] == g_papel]
                                if not df_g.empty:
                                    fase_means = df_g.groupby(["competidor", "fase"])["nota"].mean().reset_index()
                                    total_score = fase_means.groupby("competidor")["nota"].sum().reset_index()
                                    total_score.columns = ["PARTICIPANTE", "PONTUAÇÃO TOTAL"]
                                    total_score = total_score.sort_values(by="PONTUAÇÃO TOTAL", ascending=False).reset_index(drop=True)
                                    total_score.index = total_score.index + 1
                                    total_score.index.name = "#"
                                    total_score = total_score.reset_index()
                                    total_score["CLASS."] = [f"{idx}º" for idx in total_score.index]
                                    total_score["PONTUAÇÃO TOTAL"] = total_score["PONTUAÇÃO TOTAL"].apply(lambda x: f"{x:.1f}")
                                    
                                    st.dataframe(total_score[["#", "PARTICIPANTE", "PONTUAÇÃO TOTAL", "CLASS."]], use_container_width=True, hide_index=True)
                                else:
                                    st.markdown("<p style='text-align: center; color: #8d7a52; font-size: 10px;'>Aguardando votos em ambas as fases.</p>", unsafe_allow_html=True)