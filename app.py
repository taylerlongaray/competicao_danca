import base64
import json
import os
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Jack & Jill - Noite nas Arábias",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# FORÇAR FUNDO ESCURO GLOBAL NO CSS PARA QUALQUER TEMA DE NAVEGADOR
st.markdown("""
<style>
    body, .stApp {
        background-color: #090706 !important;
        color: #f3e5ab !important;
    }
</style>
""", unsafe_allow_html=True)

ARQUIVO_VOTOS = "votos.json"
ARQUIVO_CONFIG_TELAO = "config_telao.json"

opcoes_menu_telao = [
    "Diamante",
    "Platina",
    "Ouro - Fase Classificatória",
    "Ouro - Fase Final",
    "Prata - Fase Classificatória",
    "Prata - Fase Final",
    "Aprendendo a Voar"
]


def carregar_votos():
    if os.path.exists(ARQUIVO_VOTOS):
        try:
            with open(ARQUIVO_VOTOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def salvar_votos(votos):
    try:
        with open(ARQUIVO_VOTOS, "w", encoding="utf-8") as f:
            json.dump(votos, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def carregar_config_telao():
    if os.path.exists(ARQUIVO_CONFIG_TELAO):
        try:
            with open(ARQUIVO_CONFIG_TELAO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {op: False for op in opcoes_menu_telao}


def salvar_config_telao(config):
    try:
        with open(ARQUIVO_CONFIG_TELAO, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def obter_fundo_css(tipo_tela):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    candidatos = []
    if tipo_tela == "votacao":
        candidatos = [
            "fundo_votacao.png",
            "fundo_votacao.jpg",
            "fundo_painel.png",
            "fundo_painel.jpg",
            "fundo.png",
            "fundo.jpg",
        ]
    elif tipo_tela == "telao":
        candidatos = [
            "fundo_telao.png",
            "fundo_telao.jpg",
            "fundo.png",
            "fundo.jpg",
            "fundo_painel.png",
            "fundo_painel.jpg",
        ]
    else:
        candidatos = [
            f"fundo_{tipo_tela}.png",
            f"fundo_{tipo_tela}.jpg",
            "fundo.png",
            "fundo.jpg",
        ]

    try:
        for arq in os.listdir(base_dir):
            if arq.lower().endswith((".png", ".jpg", ".jpeg")) and arq not in candidatos:
                candidatos.append(arq)
    except Exception:
        pass

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
        
        if tipo_tela == "telao":
            return f"""<style>.stApp {{ background-image: url("data:image/{mime};base64,{encoded}"); background-size: 100% 100% !important; background-position: center !important; background-repeat: no-repeat !important; background-attachment: fixed; color: #f3e5ab; font-family: 'Helvetica Neue', sans-serif; }}</style>"""
        else:
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


if "jurado_logado" not in st.session_state:
    st.session_state.jurado_logado = None

if "categoria_selecionada" not in st.session_state:
    st.session_state.categoria_selecionada = None

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
        "Condutores": ["Alan Demarch", "Léo Mello", "Henrique Vargas", "Luan Ruduit", "Maick Martins", "William Ferreira"],
        "Conduzidas": ["Caroline Guedes", "Cleo Santanna", "Marluce Dimare", "Sah Graziela", "Sidiane Correa", "Vih Alves"],
    },
    "Platina": {
        "Condutores": ["Alisson Lopes", "Anderson Oliveira", "Catriel Pereira", "Deivid Nascimento", "Douglas Clo", "Jean Pierre"],
        "Conduzidas": ["Cassi Pooch", "Estéfane Borges", "Fabiola Braga", "Fran Garcia", "Ingrid Hexcel", "Nanda Soares"],
    },
    "Ouro": {
        "Condutores": ["Ciro Lima", "E. Duarte", "Edilson", "Fabiano", "Isma Simões", "Jonatan Santos", "Jonatan Monteiro", "Lukas Nunes", "Paulo PC", "Rogerio Sorriso", "Ruan LW", "Everton Fernandes", "Jozemar", "Maicom"],
        "Conduzidas": [
            "Andreza Godoi",
            "Angélica",
            "Daia Lopes",
            "Franciely Lopes",
            "Giovanna Centeno",
            "Joice Alves",
            "Julia Graciela",
            "Juliana Ferraz",
            "Marcia Araujo",
            "Marya Costa",
            "Michele Longarai",
            "Nanda Ramos",
            "Thayh Martins",
            "Valesca Bordon",
        ],
    },
    "Prata": {
        "Condutores": [
            "Alisson Gregori",
            "Albieri Fagundes",
            "Antonio Vargas",
            "Cleiton",
            "Fernando Souza",
            "Iuri Martins",
            "Douglas",
            "Léo",
            "Marcão Meireles",
            "Michel",
            "Pablo",
            "Rogério Eich",
            "Rogério Ferreira",
            "Toni",
            "Toretto",
        ],
        "Conduzidas": [
            "Ana Cris Couto",
            "Daiane Soares",
            "Dienifer Steffen",
            "Franciele",
            "Ge",
            "Gili Costa",
            "Juliana",
            "Larissa Westphal",
            "Lidiana",
            "Lilica",
            "Lolo Ferreira",
            "Nathalia",
            "Paulynha Han",
            "Sabrina",
            "Shay",
        ],
    },
    "Aprendendo a Voar": {
        "Condutores": ["Anderson Prass", "Bruno Vanassi", "Eduardo Miranda", "Ezequiel Silveira", "Ivan Dutra", "Gilmar Gemelli", "Luis Carlos", "Talisson Silva"],
        "Conduzidas": ["Carla Sabio", "Elisangela Grund", "Nahuana Rolante", "Patrícia Pereira", "Paula Monteiro", "Raquel Oliveira", "Sheila Josiane", "Sylvana de Souza"],
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
            "Atenção ao parceiro, interação, sintonia, presence,"
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
    "demo": {
        "nome": "Jurado",
        "senha": "1234",
        "permissoes": "TODAS_GLOBAL",
        "criterio_global": "Avaliação Global e de Referência"
    },
    "adri": {
        "nome": "Adri Santos",
        "senha": "6153",
        "permissoes": [
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Criatividade e Musicalidade"]},
            {"categoria": "Aprendendo a Voar", "papel": "Condutores", "criterios": ["Conexão e Entrega na Dança"]},
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
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Movimentos Característicos e Sambado"]}
        ]
    },
    "cassiano": {
        "nome": "Cassiano Fontana",
        "senha": "8516",
        "permissoes": [
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Movimentos Característicos e Sambado"]}
        ]
    },
    "claudia": {
        "nome": "Claudia Papke",
        "senha": "5274",
        "permissoes": [
            {"categoria": "Aprendendo a Voar", "papel": "Conduzidas", "criterios": ["Conexão e Entrega na Dança"]},
            {"categoria": "Prata", "papel": "Conduzidas", "criterios": ["Conexão e Resposta"]},
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
            {"categoria": "Diamante", "papel": "Conduzidas", "criterios": ["Técnica e Finalização"]},
            {"categoria": "Platina", "papel": "Conduzidas", "criterios": ["Técnica e Finalização"]},
            {"categoria": "Ouro", "papel": "Conduzidas", "criterios": ["Conexão e Resposta"]}
        ]
    },
    "joel": {
        "nome": "Joel Trevisan",
        "senha": "3572",
        "permissoes": [
            {"categoria": "Aprendendo a Voar", "papel": "Condutores", "criterios": ["Fundamentos e Qualidade da Base"]},
            {"categoria": "Ouro", "papel": "Condutores", "criterios": ["Movimentos Característicos e Sambado"]}
        ]
    },
    "lika": {
        "nome": "Lika",
        "senha": "7461",
        "permissoes": [
            {"categoria": "Ouro", "papel": "Conduzidas", "criterios": ["Movimentos Característicos e Sambado"]},
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Criatividade e Musicalidade"]}
        ]
    },
    "maick": {
        "nome": "Maick Martins",
        "senha": "2385",
        "permissoes": [
            {"categoria": "Prata", "papel": "Condutores", "criterios": ["Conexão e Resposta"]}
        ]
    },
    "nilson": {
        "nome": "Nilson Leivas",
        "senha": "8614",
        "permissoes": [
            {"categoria": "Diamante", "papel": "Conduzidas", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Platina", "papel": "Conduzidas", "criterios": ["Conexão e Resposta"]},
            {"categoria": "Ouro", "papel": "Condutores", "criterios": ["Conexão e Resposta"]}
        ]
    },
    "wagner": {
        "nome": "Wagner Camargo",
        "senha": "4296",
        "permissoes": [
            {"categoria": "Diamante", "papel": "Condutores", "criterios": ["Musicalidade/Criatividade"]},
            {"categoria": "Platina", "papel": "Condutores", "criterios": ["Técnica e Finalização"]}
        ]
    },
    "william": {
        "nome": "William Ferreira",
        "senha": "5738",
        "permissoes": [
            {"categoria": "Platina", "papel": "Condutores", "criterios": ["Conexão e Resposta"]},
            {"categoria": "Aprendendo a Voar", "papel": "Conduzidas", "criterios": ["Fundamentos e Qualidade da Base"]}
        ]
    }
}


def obter_jurados_da_categoria_papel(cat, papel):
    jurados_validos = []
    for username, dados in configuracao_jurados.items():
        if username == "demo":
            continue
        perm = dados["permissoes"]
        if perm == "TODAS_GLOBAL":
            jurados_validos.append(dados["nome"])
        elif isinstance(perm, list):
            for p in perm:
                if p["categoria"] == cat and p["papel"] == papel:
                    jurados_validos.append(dados["nome"])
                    break
    
    jurados_ordenados = sorted(list(set(jurados_validos)), key=lambda x: (1 if "Alex" in x else 0, x))
    return jurados_ordenados


def obter_classificados(categoria, papel):
    votos_atuais = carregar_votos()
    if not votos_atuais:
        return []
    df = pd.DataFrame(votos_atuais)
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
    votos = carregar_votos()
    encontrado = False
    for voto in votos:
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
            encontrado = True
            break

    if not encontrado:
        votos.append({
            "jurado": jurado,
            "categoria": categoria,
            "fase": fase,
            "papel": papel,
            "competidor": competidor,
            "criterio": criterio,
            "nota": nota,
            "justificativa": justificativa,
        })
    salvar_votos(votos)


def buscar_nota_salva(jurado, categoria, fase, papel, competidor, criterio):
    votos = carregar_votos()
    for voto in votos:
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

    if st.session_state.jurado_logado is not None:
        modo = "Painel do Jurado"
    else:
        modo = st.sidebar.radio(
            "Navegação",
            ["Painel do Jurado", "Painel da Organização", "Telão (Público)"],
            label_visibility="collapsed",
        )

# LAYOUT DINÂMICO: ESTREITO (600px) PARA O JURADO, LARGURA TOTAL PARA ORGANIZAÇÃO E TELÃO
if modo == "Painel do Jurado":
    st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.session_state.jurado_logado is None:
        st.markdown(obter_fundo_css("login"), unsafe_allow_html=True)
    elif st.session_state.categoria_selecionada is None:
        st.markdown(obter_fundo_css("categorias"), unsafe_allow_html=True)
    else:
        st.markdown(obter_fundo_css("votacao"), unsafe_allow_html=True)
elif modo == "Telão (Público)":
    st.markdown(obter_fundo_css("telao"), unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .block-container {
        max-width: 100% !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(obter_fundo_css("painel"), unsafe_allow_html=True)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@600;700&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

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

.stTextInput div[data-baseweb="input"], .stTextArea textarea {
    background-color: rgba(12, 9, 7, 0.95) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 6px !important;
    color: #f3e5ab !important;
}

.stTextInput input, .stTextArea textarea {
    color: #f3e5ab !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #f3e5ab !important;
}

.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: rgba(243, 229, 171, 0.5) !important;
    -webkit-text-fill-color: rgba(243, 229, 171, 0.5) !important;
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
            if st.button("✧    LOGIN    ✧", type="primary", use_container_width=True):
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
                f'<div style="position: fixed; top: 40px; right: 12px; z-index: 9999;"><a href="?{logout_param}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center;">← Sair</a></div>',
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
                f"""<div style="position: fixed; top: 60%; left: 50%; transform: translate(-50%, -50%); width: 360px; max-width: 90vw; z-index: 9999;"><div style="text-align: center; margin-bottom: 12px;"><div class="saudacao-jurado">Olá, {nome_jurado}!</div><p style="color: #f3e5ab; font-family: 'Helvetica Neue', sans-serif; font-size: 11px; opacity: 0.9; margin-bottom: 12px;">Selecione a categoria que você irá avaliar:</p></div>{cards_html}</div><style>.category-card {{ display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, rgba(15, 11, 7, 0.92) 0%, rgba(30, 21, 12, 0.96) 100%); border: 1px solid rgba(212, 175, 55, 0.5); border-radius: 10px !important; padding: 9px 16px !important; margin-bottom: 8px !important; text-decoration: none !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7); transition: all 0.3s ease; }} .category-card:hover {{ border-color: rgba(212, 175, 55, 1.0); background: linear-gradient(135deg, rgba(25, 18, 12, 0.98) 0%, rgba(45, 33, 19, 1) 100%); }} .card-left {{ display: flex; align-items: center; gap: 15px; }} .card-icon {{ width: 26px !important; height: 26px !important; object-fit: contain; }} .card-title {{ color: #f3e5ab; font-family: 'Georgia', serif; font-size: 12px !important; font-weight: 600; letter-spacing: 2px; }} .card-arrow {{ color: #d4af37; font-size: 16px !important; }}</style>""",
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
                f"""<div style="position: fixed; top: 12px; left: 12px; right: 12px; z-index: 9999; display: flex; justify-content: space-between; align-items: center; pointer-events: none;"><a href="{logout_url}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center; pointer-events: auto;">← Sair</a><a href="{trocar_url}" style="background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(60,45,25,0.95) 100%); color: #f3e5ab; text-decoration: none; width: 95px; height: 38px; border-radius: 6px; border: 1px solid rgba(212,175,55,0.6); font-size: 8.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.15; pointer-events: auto;">Trocar<br>Categoria</a></div>""",
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

                                aviso_placeholder = st.empty()
                                aviso_placeholder.markdown(
                                    f"""
                                    <style>
                                    @keyframes scaleUp {{
                                        0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.8); }}
                                        100% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
                                    }}
                                    .jj-overlay-success {{
                                        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                                        background: rgba(5, 4, 3, 0.85); z-index: 99999998;
                                    }}
                                    .jj-popup-success {{
                                        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                        background: linear-gradient(135deg, rgba(20, 15, 10, 0.99) 0%, rgba(45, 33, 19, 0.99) 100%);
                                        border: 2px solid #d4af37; border-radius: 14px; padding: 25px 22px; text-align: center;
                                        width: 340px; max-width: 90vw; box-shadow: 0 10px 30px rgba(0,0,0,0.9); z-index: 99999999;
                                        animation: scaleUp 0.2s ease-out forwards;
                                    }}
                                    </style>
                                    <div class="jj-overlay-success"></div>
                                    <div class="jj-popup-success">
                                        <div style="font-size: 42px; margin-bottom: 8px; color: #d4af37;">✅</div>
                                        <div style="font-family: 'Cinzel', Georgia, serif; color: #f3e5ab; font-size: 16px; font-weight: bold; margin-bottom: 6px; letter-spacing: 1px;">AVALIAÇÃO ENVIADA!</div>
                                        <div style="color: #ded2b4; font-size: 12px; line-height: 1.4;">Avaliação de <b>{competidor_escolhido}</b><br>concluída com sucesso!</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                                time.sleep(1.2) 

                                if st.session_state.idx_crit + 1 < total_crit:
                                    st.session_state.idx_crit += 1
                                else:
                                    st.session_state.idx_crit = 0
                                    st.session_state.idx_comp = (
                                        st.session_state.idx_comp + 1
                                    ) % total_comp

                                st.rerun()
                        except ValueError:
                            st.error("❌ Digite um valor numérico válido para a nota.")

elif modo == "Painel da Organização":
    st.title("📋 Painel da Organização — Acompanhamento Geral")
    with st.container(border=True):
        senha_digitada = st.text_input(
            "Digite a senha de acesso da organização", type="password"
        )
    SENHA_MESTRE = "danca123"

    if senha_digitada == SENHA_MESTRE:
        st.success("🔓 Acesso autorizado!")
        
        # --- SECÇÃO DE CONTROLO REMOTO DO TELÃO (NOTAS SECRETAS DO ALEX) ---
        st.markdown("---")
        st.markdown("### 🔓 Controlo Remoto do Telão (Notas Secretas do Alex)")
        st.markdown("<p style='font-size: 12px; color: #b39b6b;'>Ative aqui para revelar ou ocultar a nota secreta do Alex no Telão em tempo real.</p>", unsafe_allow_html=True)
        
        config_telao_atual = carregar_config_telao()
        col_ctrl1, col_ctrl2 = st.columns(2)
        novas_config_telao = config_telao_atual.copy()
        
        for idx, op in enumerate(opcoes_menu_telao):
            val_atual = config_telao_atual.get(op, False)
            coluna_alvo = col_ctrl1 if idx % 2 == 0 else col_ctrl2
            with coluna_alvo:
                novas_config_telao[op] = st.checkbox(
                    f"🔓 Revelar: {op}",
                    value=val_atual,
                    key=f"rem_rev_{op}"
                )
                
        if novas_config_telao != config_telao_atual:
            salvar_config_telao(novas_config_telao)
            st.success("✨ Estado do telão atualizado com sucesso!")
            st.rerun()

        # BOTÕES DE AÇÃO RÁPIDA (ATUALIZAR E LIMPAR)
        st.markdown("---")
        col_btn_ref, col_btn_lim = st.columns([2, 1])
        with col_btn_ref:
            if st.button("🔄 ATUALIZAR DADOS DA TELA (BUSCAR NOVOS VOTOS)", type="primary", use_container_width=True):
                st.rerun()
        with col_btn_lim:
            if st.button("🗑️ APAGAR TUDO", type="secondary", use_container_width=True):
                salvar_votos([])
                st.success("Sistema limpo!")
                st.rerun()

        votos_atuais = carregar_votos()
        df_rel = pd.DataFrame(votos_atuais) if votos_atuais else pd.DataFrame(columns=["categoria", "fase", "competidor", "jurado", "criterio", "papel", "nota", "justificativa"])

        # --- SECÇÃO DE RELATÓRIOS POR ETAPA / FASE ---
        st.markdown("---")
        st.markdown("### 📥 Relatórios por Etapa / Fase Concluída")
        st.markdown("<p style='font-size: 12px; color: #b39b6b;'>Baixe o relatório detalhado de cada fase/etapa assim que ela terminar.</p>", unsafe_allow_html=True)
        
        if not df_rel.empty:
            cols_etapa = st.columns(3)
            idx_col = 0
            for cat_n in categorias.keys():
                fases_da_cat = fases_por_categoria[cat_n]
                for fase_n in fases_da_cat:
                    df_etapa_check = df_rel[(df_rel["categoria"] == cat_n) & (df_rel["fase"] == fase_n)]
                    with cols_etapa[idx_col % 3]:
                        if not df_etapa_check.empty:
                            html_etapa = f"""
                            <html><head><meta charset="utf-8">
                            <style>body{{font-family:Helvetica,Arial,sans-serif;color:#333;margin:20px;}}h1{{color:#b8860b;text-align:center;border-bottom:2px solid #b8860b;padding-bottom:10px;}}h2{{color:#555;margin-top:20px;border-bottom:1px solid #ccc;}}.card{{background:#fdfcf7;border:1px solid #e3d3a1;padding:10px;margin-bottom:8px;border-radius:6px;}}</style>
                            </head><body>
                            <h1>Relatório — {cat_n} ({fase_n})</h1>
                            """
                            for p_papel in df_etapa_check["papel"].unique():
                                html_etapa += f"<h2>Papel: {p_papel}</h2>"
                                df_papel_sub = df_etapa_check[df_etapa_check["papel"] == p_papel]
                                for comp_sub in df_papel_sub["competidor"].unique():
                                    html_etapa += f"<h3>Participante: {comp_sub}</h3>"
                                    df_comp_sub = df_papel_sub[df_papel_sub["competidor"] == comp_sub]
                                    for _, r_row in df_comp_sub.iterrows():
                                        j_nome = configuracao_jurados.get(r_row['jurado'], {}).get('nome', r_row['jurado'])
                                        just_txt = r_row['justificativa'] if r_row['justificativa'] else "Sem comentários."
                                        html_etapa += f"""<div class="card"><b>Jurado:</b> {j_nome} | <b>Critério:</b> {r_row['criterio']} | <b>Nota:</b> <b>{r_row['nota']}</b><br><i>Comentário:</i> "{just_txt}"</div>"""
                            html_etapa += "</body></html>"
                            
                            st.download_button(
                                label=f"📄 {cat_n} — {fase_n}",
                                data=html_etapa,
                                file_name=f"Relatorio_{cat_n.replace(' ', '_')}_{fase_n.replace(' ', '_').replace('(', '').replace(')', '')}.html",
                                mime="text/html",
                                key=f"dl_etapa_{cat_n}_{fase_n}"
                            )
                        else:
                            st.markdown(f"<div style='font-size:11px; color:#777; padding:8px;'>⏳ {cat_n} ({fase_n}): Sem votos</div>", unsafe_allow_html=True)
                    idx_col += 1
        else:
            st.info("Ainda não existem votos registados para gerar relatórios por etapa.")

        st.markdown("---")
        st.markdown("### 📊 Auditoria Detalhada por Categoria (Tabelas Largas para o Notebook)")
        
        categorias_lista = ["Diamante", "Platina", "Ouro", "Prata", "Aprendendo a Voar"]
        
        for cat_nome in categorias_lista:
            with st.expander(f"📁 Categoria: {cat_nome.upper()} (Ver Votos Detalhados)", expanded=False):
                df_cat_filtrado = df_rel[df_rel["categoria"] == cat_nome] if not df_rel.empty else pd.DataFrame()
                
                if not df_cat_filtrado.empty:
                    df_exibicao = df_cat_filtrado.copy()
                    df_exibicao["jurado"] = df_exibicao["jurado"].apply(lambda j: configuracao_jurados.get(j, {}).get("nome", j))
                    
                    st.dataframe(
                        df_exibicao[["fase", "papel", "competidor", "jurado", "criterio", "nota", "justificativa"]],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    html_cat_rel = f"""
                    <html>
                    <head>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Helvetica, Arial, sans-serif; color: #333; margin: 20px; }}
                        h1 {{ text-align: center; color: #b8860b; border-bottom: 2px solid #b8860b; padding-bottom: 10px; }}
                        h2 {{ color: #555; border-bottom: 1px solid #ccc; margin-top: 30px; padding-bottom: 5px; }}
                        h3 {{ color: #444; margin-top: 20px; }}
                        .voto-card {{ background: #fdfcf7; border: 1px solid #e3d3a1; padding: 10px 15px; margin-bottom: 10px; border-radius: 6px; }}
                        .meta {{ font-size: 12px; color: #666; margin-bottom: 4px; }}
                        .comentario {{ font-style: italic; color: #444; background: #fff; padding: 6px; border-left: 3px solid #b8860b; margin-top: 6px; }}
                    </style>
                    </head>
                    <body>
                    <h1>Relatório de Avaliações — Categoria: {cat_nome}</h1>
                    """
                    for fase in sorted(df_cat_filtrado["fase"].unique()):
                        html_cat_rel += f"<h2>Fase: {fase}</h2>"
                        df_fase = df_cat_filtrado[df_cat_filtrado["fase"] == fase]
                        for comp in sorted(df_fase["competidor"].unique()):
                            html_cat_rel += f"<h3>Participante: {comp}</h3>"
                            df_comp = df_fase[df_fase["competidor"] == comp]
                            for _, row in df_comp.iterrows():
                                jurado_nome = configuracao_jurados.get(row['jurado'], {}).get('nome', row['jurado'])
                                just = row['justificativa'] if row['justificativa'] else "Sem comentários registados."
                                html_cat_rel += f"""
                                <div class="voto-card">
                                    <div class="meta"><b>Jurado:</b> {jurado_nome} | <b>Critério:</b> {row['criterio']} | <b>Papel:</b> {row['papel']} | <b>Nota:</b> <b>{row['nota']}</b></div>
                                    <div class="comentario"><b>Comentário:</b> "{just}"</div>
                                </div>
                                """
                    html_cat_rel += "</body></html>"
                    
                    st.download_button(
                        label=f"📥 Baixar Relatório Completo da Categoria {cat_nome}",
                        data=html_cat_rel,
                        file_name=f"Relatorio_{cat_nome.replace(' ', '_')}.html",
                        mime="text/html",
                        key=f"btn_dl_{cat_nome}"
                    )
                else:
                    st.info(f"Nenhum voto registado ainda na categoria {cat_nome}.")

        st.markdown("---")
        st.markdown("### 📄 Relatório Geral Consolidado")
        
        if votos_atuais:
            html_relatorio = """
            <html>
            <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Helvetica, Arial, sans-serif; color: #333; margin: 20px; }
                h1 { text-align: center; color: #b8860b; border-bottom: 2px solid #b8860b; padding-bottom: 10px; }
                h2 { color: #555; border-bottom: 1px solid #ccc; margin-top: 30px; padding-bottom: 5px; }
                .voto-card { background: #fdfcf7; border: 1px solid #e3d3a1; padding: 10px 15px; margin-bottom: 10px; border-radius: 6px; }
                .meta { font-size: 12px; color: #666; margin-bottom: 4px; }
                .comentario { font-style: italic; color: #444; background: #fff; padding: 6px; border-left: 3px solid #b8860b; margin-top: 6px; }
            </style>
            </head>
            <body>
            <h1>Relatório de Avaliações — Jack & Jill: Noite nas Arábias</h1>
            """
            
            df_rel_all = pd.DataFrame(votos_atuais)
            for cat in sorted(df_rel_all["categoria"].unique()):
                html_relatorio += f"<h2>Categoria: {cat}</h2>"
                df_cat = df_rel_all[df_rel_all["categoria"] == cat]
                for fase in sorted(df_cat["fase"].unique()):
                    html_relatorio += f"<h3>Fase: {fase}</h3>"
                    df_fase = df_cat[df_cat["fase"] == fase]
                    for comp in sorted(df_fase["competidor"].unique()):
                        html_relatorio += f"<h4>Participante: {comp}</h4>"
                        df_comp = df_fase[df_fase["competidor"] == comp]
                        for _, row in df_comp.iterrows():
                            jurado_nome = configuracao_jurados.get(row['jurado'], {}).get('nome', row['jurado'])
                            just = row['justificativa'] if row['justificativa'] else "Sem comentários registados."
                            html_relatorio += f"""
                            <div class="voto-card">
                                <div class="meta"><b>Jurado:</b> {jurado_nome} | <b>Critério:</b> {row['criterio']} | <b>Papel:</b> {row['papel']} | <b>Nota:</b> <b>{row['nota']}</b></div>
                                <div class="comentario"><b>Comentário:</b> "{just}"</div>
                            </div>
                            """
            html_relatorio += "</body></html>"
            
            st.download_button(
                label="📥 Descarregar Relatório Completo Consolidado (HTML/PDF)",
                data=html_relatorio,
                file_name="Relatorio_Geral_JackAndJill.html",
                mime="text/html",
                type="primary"
            )
        else:
            st.info("Ainda não existem votos ou comentários registados para gerar o relatório.")
            
    elif senha_digitada != "":
        st.error("❌ Senha incorreta!")

else:
    # --- TELÃO (PÚBLICO) ---
    
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=2000, limit=None, key="refresh_telao")
    except ImportError:
        st.error("⚠️ Instale o pacote executando: pip install streamlit-autorefresh")

    components.html(
        """
        <script>
        const parentDoc = window.parent.document;
        let btn = parentDoc.getElementById('atalho-sidebar-telao');
        
        if (!btn) {
            btn = parentDoc.createElement('button');
            btn.id = 'atalho-sidebar-telao';
            btn.innerHTML = '☰ MENU';
            btn.title = 'Abrir Barra Lateral (Atalho: Alt + M)';
            
            Object.assign(btn.style, {
                position: 'fixed',
                top: '12px',
                left: '12px',
                zIndex: '9999999',
                padding: '8px 14px',
                background: 'rgba(15, 11, 7, 0.95)',
                color: '#d4af37',
                border: '1px solid #d4af37',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px',
                fontFamily: 'sans-serif',
                boxShadow: '0 4px 8px rgba(0,0,0,0.6)',
                transition: 'all 0.3s'
            });
            
            btn.onmouseover = () => { btn.style.background = '#d4af37'; btn.style.color = '#000'; };
            btn.onmouseout = () => { btn.style.background = 'rgba(15, 11, 7, 0.95)'; btn.style.color = '#d4af37'; };
            
            btn.onclick = function() {
                const sidebarToggle = parentDoc.querySelector('[data-testid="collapsedControl"]');
                if (sidebarToggle) {
                    sidebarToggle.click();
                } else {
                    const closeBtn = parentDoc.querySelector('section[data-testid="stSidebar"] button');
                    if (closeBtn) closeBtn.click();
                }
            };
            
            parentDoc.body.appendChild(btn);
        }
        
        function keyHandler(e) {
            if (e.altKey && e.key.toLowerCase() === 'm') {
                if (btn) btn.click();
            }
        }
        parentDoc.addEventListener('keydown', keyHandler);
        
        window.addEventListener('unload', function() {
            if (btn) btn.remove();
            parentDoc.removeEventListener('keydown', keyHandler);
        });
        </script>
        """,
        height=0,
        width=0
    )

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 5.5rem !important;
            padding-bottom: 4rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
            margin: 0 auto !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            z-index: 99999 !important;
        }
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            background-color: rgba(15, 11, 7, 0.9) !important;
            border: 1px solid rgba(212, 175, 55, 0.8) !important;
            border-radius: 6px !important;
            color: #f3e5ab !important;
            z-index: 999999 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.6) !important;
        }
        [data-testid="collapsedControl"] svg {
            fill: #f3e5ab !important;
        }
        [data-testid="stToolbar"], .stAppDeployButton, [data-testid="stDecoration"] {
            display: none !important;
        }
        .viewerBadge_container, [data-testid="stStatusWidget"], footer {
            display: none !important;
            visibility: hidden !important;
        }
        h2 {
            font-size: 20px !important;
            margin-top: -10px !important;
            margin-bottom: 15px !important;
            color: #e5c158 !important;
            font-family: 'Cinzel', Georgia, serif;
            text-align: center;
            letter-spacing: 2px;
        }
        h3 {
            font-size: 13px !important;
            margin-top: 2px !important;
            margin-bottom: 5px !important;
            color: #f3e5ab !important;
            font-family: 'Cinzel', Georgia, serif;
        }
        
        .tabela-dourada {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 11px;
            font-family: 'Helvetica Neue', sans-serif;
            color: #f3e5ab;
            background: linear-gradient(135deg, rgba(10, 7, 5, 0.90) 0%, rgba(20, 15, 10, 0.95) 100%);
            border: 1px solid rgba(212, 175, 55, 0.6);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.8);
        }
        .tabela-dourada thead {
            background-color: rgba(15, 11, 7, 1);
        }
        .tabela-dourada th {
            color: #e5c158;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: center !important;
            padding: 5px 3px;
            border-bottom: 2px solid #d4af37;
            line-height: 1.1;
        }
        .tabela-dourada td {
            text-align: center !important;
            padding: 4px 3px;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            white-space: nowrap !important;
        }
        .tabela-dourada td:nth-child(2) {
            font-size: 12.5px !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            text-align: left !important;
            padding-left: 8px !important;
            color: #ffffff !important;
            letter-spacing: 0.4px;
        }
        .tabela-dourada tbody tr:last-child td {
            border-bottom: none;
        }
        .tabela-dourada tbody tr:hover {
            background-color: rgba(212, 175, 55, 0.15);
        }

        .tabela-dourada-compacta {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 10px;
            font-family: 'Helvetica Neue', sans-serif;
            color: #f3e5ab;
            background: linear-gradient(135deg, rgba(10, 7, 5, 0.90) 0%, rgba(20, 15, 10, 0.95) 100%);
            border: 1px solid rgba(212, 175, 55, 0.6);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.8);
        }
        .tabela-dourada-compacta thead {
            background-color: rgba(15, 11, 7, 1);
        }
        .tabela-dourada-compacta th {
            color: #e5c158;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            text-align: center !important;
            padding: 4px 2px;
            border: 1px solid rgba(212, 175, 55, 0.4);
            line-height: 1.0;
        }
        .tabela-dourada-compacta td {
            text-align: center !important;
            padding: 4px 2px;
            border: 1px solid rgba(212, 175, 55, 0.2);
            white-space: nowrap !important;
        }
        .tabela-dourada-compacta .col-partic {
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 12px !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            text-align: left !important;
            padding-left: 6px !important;
            color: #ffffff !important;
            letter-spacing: 0.3px;
        }
        .tabela-dourada-compacta tbody tr:hover {
            background-color: rgba(212, 175, 55, 0.15);
        }

        .podio-1 {
            color: #ffd700 !important;
            font-weight: bold;
            text-shadow: 0 0 6px rgba(255, 215, 0, 0.6);
        }
        .podio-2 {
            color: #e0e0e0 !important;
            font-weight: bold;
            text-shadow: 0 0 4px rgba(224, 224, 224, 0.5);
        }
        .podio-3 {
            color: #cd7f32 !important;
            font-weight: bold;
            text-shadow: 0 0 4px rgba(205, 127, 50, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Seleção da Tabela no Telão")
        
        def formatar_icone_menu(c):
            if "Diamante" in c: return f"💎 {c}"
            if "Platina" in c: return f"🥈 {c}"
            if "Ouro" in c: return f"🥇 {c}"
            if "Prata" in c: return f"🥈 {c}"
            return f"🕊️ {c}"

        selecao_telao = st.radio(
            "Selecione a Categoria",
            opcoes_menu_telao,
            format_func=formatar_icone_menu,
            label_visibility="collapsed"
        )
        
        config_telao_atual = carregar_config_telao()
        status_revelado = config_telao_atual.get(selecao_telao, False)
        st.markdown("---")
        if status_revelado:
            st.markdown("<div style='text-align: center; color: #ffd700; font-size: 11px; font-weight: bold;'>🔓 Nota de Alex: REVELADA</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; color: #b39b6b; font-size: 11px;'>🔒 Nota de Alex: OCULTA</div>", unsafe_allow_html=True)

    revelado_atual = carregar_config_telao().get(selecao_telao, False)

    df_votos = pd.DataFrame(carregar_votos()) if carregar_votos() else pd.DataFrame(columns=["jurado", "categoria", "fase", "papel", "competidor", "criterio", "nota", "justificativa"])
    
    if "Ouro" in selecao_telao:
        categoria_nome = "Ouro"
        fases_da_cat = ["Fase Classificatória"] if "Classificatória" in selecao_telao else ["Fase Final"]
    elif "Prata" in selecao_telao:
        categoria_nome = "Prata"
        fases_da_cat = ["Fase Classificatória"] if "Classificatória" in selecao_telao else ["Fase Final"]
    else:
        categoria_nome = selecao_telao
        fases_da_cat = fases_por_categoria[categoria_nome]

    df_cat = df_votos[df_votos["categoria"] == categoria_nome] if not df_votos.empty else pd.DataFrame()

    st.markdown(f"<h2 style='text-align: center; color: #e5c158; font-family: Cinzel, Georgia, serif; letter-spacing: 2px;'>{selecao_telao.upper()} — RESULTADOS</h2>", unsafe_allow_html=True)
    
    def formatar_nome_jurado(nome):
        partes = nome.split(" ", 1)
        if len(partes) > 1:
            return f"{partes[0]}<br>{partes[1]}"
        return nome

    def formatar_classificacao_podio(idx):
        pos = idx + 1
        if pos == 1:
            return '<span class="podio-1">1º 🥇</span>'
        elif pos == 2:
            return '<span class="podio-2">2º 🥈</span>'
        elif pos == 3:
            return '<span class="podio-3">3º 🥉</span>'
        return f"{pos}º"

    def gerar_tabela_papel_fase(fase_nome, papel_nome, revelado_atual):
        jurados_aptos = obter_jurados_da_categoria_papel(categoria_nome, papel_nome)
        df_fase = df_cat[df_cat["fase"] == fase_nome] if not df_cat.empty else pd.DataFrame()
        
        if fase_nome == "Fase Final" and categoria_nome in ["Prata", "Ouro"]:
            comps = obter_classificados(categoria_nome, papel_nome)
            if not comps:
                comps = categorias[categoria_nome][papel_nome]
        else:
            comps = categorias[categoria_nome][papel_nome]

        df_base = pd.DataFrame({"competidor": comps})
        df_papel = df_fase[df_fase["papel"] == papel_nome] if not df_fase.empty else pd.DataFrame()

        if not df_papel.empty:
            df_notas_jurado = df_papel.groupby(["competidor", "jurado"])["nota"].mean().reset_index()
            df_notas_jurado["jurado_nome"] = df_notas_jurado["jurado"].apply(lambda j: configuracao_jurados.get(j, {}).get("nome", j))
            pivot_df = df_notas_jurado.pivot(index="competidor", columns="jurado_nome", values="nota").reset_index()
            pivot_df = pd.merge(df_base, pivot_df, on="competidor", how="left")
        else:
            pivot_df = df_base.copy()

        for j_col in jurados_aptos:
            if j_col not in pivot_df.columns:
                pivot_df[j_col] = None

        exist_j_cols = [j for j in jurados_aptos if j in pivot_df.columns]
        vis_cols = [j for j in exist_j_cols if "Alex" not in j]
        
        if not revelado_atual:
            pivot_df["TOTAL_RANKING"] = pivot_df[vis_cols].sum(axis=1, min_count=1)
            pivot_df["TOTAL"] = pivot_df[vis_cols].sum(axis=1, min_count=1)
        else:
            pivot_df["TOTAL_RANKING"] = pivot_df[exist_j_cols].sum(axis=1, min_count=1)
            pivot_df["TOTAL"] = pivot_df[exist_j_cols].sum(axis=1, min_count=1)

        pivot_df = pivot_df.sort_values(by="TOTAL_RANKING", ascending=False, na_position="last").reset_index(drop=True)

        pivot_df["CLASS."] = [formatar_classificacao_podio(idx) for idx in pivot_df.index]
        pivot_df["PARTICIPANTE"] = pivot_df["competidor"]

        renomeador = {j: formatar_nome_jurado(j) for j in jurados_aptos}
        pivot_df = pivot_df.rename(columns=renomeador)

        jurados_formatados = [formatar_nome_jurado(j) for j in jurados_aptos]
        cols_finais = ["CLASS.", "PARTICIPANTE"] + jurados_formatados + ["TOTAL"]
        cols_finais_existentes = [c for c in cols_finais if c in pivot_df.columns]
        tabela_exibicao = pivot_df[cols_finais_existentes].copy()

        for j in jurados_formatados:
            if j in tabela_exibicao.columns:
                if not revelado_atual and "Alex" in j:
                    tabela_exibicao[j] = tabela_exibicao[j].apply(lambda x: "🔒" if pd.notnull(x) and str(x) != "nan" else "-")
                else:
                    tabela_exibicao[j] = tabela_exibicao[j].apply(lambda x: f"{x:.1f}" if pd.notnull(x) and x != "" and str(x) != "nan" else "-")
        
        if "TOTAL" in tabela_exibicao.columns:
            tabela_exibicao["TOTAL"] = tabela_exibicao["TOTAL"].apply(lambda x: f"{x:.1f}" if pd.notnull(x) and x != 0 and str(x) != "nan" and str(x) != "0.0" else "-")

        return tabela_exibicao.to_html(index=False, classes="tabela-dourada", escape=False)

    def gerar_tabela_acumulada_diamante_platina_html(papel_nome, revelado_atual):
        jurados_aptos = obter_jurados_da_categoria_papel(categoria_nome, papel_nome)
        comps = categorias[categoria_nome][papel_nome]
        
        fase1_nome = "Fase 1 (Música 1)"
        fase2_nome = "Fase 2 (Música 2)"
        
        dados_tabela = {c: {j: {'f1': None, 'f2': None} for j in jurados_aptos} for c in comps}
        
        if not df_cat.empty:
            df_papel = df_cat[df_cat["papel"] == papel_nome]
            if not df_papel.empty:
                grouped = df_papel.groupby(["competidor", "fase", "jurado"])["nota"].mean().reset_index()
                for _, row in grouped.iterrows():
                    comp = row["competidor"]
                    fase = row["fase"]
                    jurado_username = row["jurado"]
                    jurado_nome_real = configuracao_jurados.get(jurado_username, {}).get("nome", jurado_username)
                    
                    if jurado_nome_real in jurados_aptos:
                        if comp in dados_tabela:
                            if fase1_nome in fase:
                                dados_tabela[comp][jurado_nome_real]['f1'] = row["nota"]
                            elif fase2_nome in fase:
                                dados_tabela[comp][jurado_nome_real]['f2'] = row["nota"]

        lista_linhas = []
        for comp in comps:
            totais_geral = []
            totais_visiveis = []
            
            for j in jurados_aptos:
                f1 = dados_tabela[comp][j]['f1']
                f2 = dados_tabela[comp][j]['f2']
                val_f1 = f1 if f1 is not None else 0
                val_f2 = f2 if f2 is not None else 0
                soma_j = val_f1 + val_f2
                
                totais_geral.append(soma_j)
                if "Alex" not in j:
                    totais_visiveis.append(soma_j)
                    
            tem_nota_geral = any(dados_tabela[comp][j]['f1'] is not None or dados_tabela[comp][j]['f2'] is not None for j in jurados_aptos)
            tem_nota_visivel = any(dados_tabela[comp][j]['f1'] is not None or dados_tabela[comp][j]['f2'] is not None for j in jurados_aptos if "Alex" not in j)

            total_completo = sum(totais_geral) if tem_nota_geral else -1
            total_visivel = sum(totais_visiveis) if tem_nota_visivel else -1
            
            if revelado_atual:
                total_exibicao = total_completo
                total_ord = total_completo
            else:
                total_exibicao = total_visivel
                total_ord = total_visivel

            lista_linhas.append({
                "competidor": comp,
                "dados": dados_tabela[comp],
                "total": total_exibicao,
                "total_ord": total_ord
            })
            
        lista_linhas.sort(key=lambda x: x["total_ord"], reverse=True)
        
        html = '<table class="tabela-dourada-compacta">'
        html += '<thead>'
        html += '<tr>'
        html += '<th rowspan="2">CLASS.</th>'
        html += '<th rowspan="2">PARTICIPANTE</th>'
        
        for j in jurados_aptos:
            nome_fmt = formatar_nome_jurado(j).replace("<br>", " ")
            html += f'<th colspan="2">{nome_fmt}</th>'
            
        html += '<th rowspan="2">TOTAL</th>'
        html += '</tr>'
        
        html += '<tr>'
        for _ in jurados_aptos:
            html += '<th>MÚSICA 1</th><th>MÚSICA 2</th>'
        html += '</tr>'
        html += '</thead>'
        
        html += '<tbody>'
        for idx, linha in enumerate(lista_linhas):
            class_str = formatar_classificacao_podio(idx)
            comp_nome = linha["competidor"]
            
            html += '<tr>'
            html += f'<td>{class_str}</td>'
            html += f'<td class="col-partic" title="{comp_nome}">{comp_nome}</td>'
            
            for j in jurados_aptos:
                f1 = linha["dados"][j]['f1']
                f2 = linha["dados"][j]['f2']
                
                if not revelado_atual and "Alex" in j:
                    str_f1 = "🔒" if f1 is not None else "-"
                    str_f2 = "🔒" if f2 is not None else "-"
                else:
                    str_f1 = f"{f1:.1f}" if f1 is not None else "-"
                    str_f2 = f"{f2:.1f}" if f2 is not None else "-"
                
                html += f'<td>{str_f1}</td>'
                html += f'<td>{str_f2}</td>'
            
            soma_real = 0
            tem_valida = False
            for j in jurados_aptos:
                f1 = linha["dados"][j]['f1']
                f2 = linha["dados"][j]['f2']
                if not revelado_atual and "Alex" in j:
                    continue
                if f1 is not None:
                    soma_real += f1
                    tem_valida = True
                if f2 is not None:
                    soma_real += f2
                    tem_valida = True

            str_total = f"{soma_real:.1f}" if tem_valida else "-"
            html += f'<td><b>{str_total}</b></td>'
            html += '</tr>'
            
        html += '</tbody>'
        html += '</table>'
        
        return html

    if categoria_nome in ["Diamante", "Platina"]:
        col_cond, col_condz = st.columns(2)

        with col_cond:
            st.markdown("<h3 style='text-align: center; color: #e5c158; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;'>Condutores</h3>", unsafe_allow_html=True)
            tabela_cond_html = gerar_tabela_acumulada_diamante_platina_html("Condutores", revelado_atual)
            st.markdown(tabela_cond_html, unsafe_allow_html=True)

        with col_condz:
            st.markdown("<h3 style='text-align: center; color: #e5c158; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;'>Conduzidas</h3>", unsafe_allow_html=True)
            tabela_condz_html = gerar_tabela_acumulada_diamante_platina_html("Conduzidas", revelado_atual)
            st.markdown(tabela_condz_html, unsafe_allow_html=True)

    else:
        for fase_nome in fases_da_cat:
            col_cond, col_condz = st.columns(2)

            with col_cond:
                st.markdown(f"<h3 style='text-align: center; color: #e5c158; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;'>Condutores — {fase_nome}</h3>", unsafe_allow_html=True)
                tabela_cond = gerar_tabela_papel_fase(fase_nome, "Condutores", revelado_atual)
                st.markdown(tabela_cond, unsafe_allow_html=True)

            with col_condz:
                st.markdown(f"<h3 style='text-align: center; color: #e5c158; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;'>Conduzidas — {fase_nome}</h3>", unsafe_allow_html=True)
                tabela_condz = gerar_tabela_papel_fase(fase_nome, "Conduzidas", revelado_atual)
                st.markdown(tabela_condz, unsafe_allow_html=True)