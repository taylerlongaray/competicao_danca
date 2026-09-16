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

  # Define os candidatos específicos baseados no tipo de tela
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
    return f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(5, 4, 3, 0.05), rgba(5, 4, 3, 0.10)), url("data:image/{mime};base64,{encoded}");
            background-size: cover;
            background-position: top center !important;
            background-attachment: fixed;
            color: #f3e5ab;
            font-family: 'Helvetica Neue', sans-serif;
        }}
        </style>
        """
  else:
    return """
        <style>
        .stApp {
            background-color: #090706;
            color: #f3e5ab;
        }
        </style>
        """


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

if "competidor_index" not in st.session_state:
  st.session_state.competidor_index = 0

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


if link_jurado_exclusivo:
  modo = "Painel do Jurado"
  st.markdown(
      """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        </style>
        """,
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
    st.markdown(
        obter_fundo_css("votacao"), unsafe_allow_html=True
    )  # Usa o fundo específico da votação
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
        padding-top: 1rem !important;
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
        background: linear-gradient(135deg, rgba(15, 11, 7, 0.92) 0%, rgba(30, 21, 12, 0.96) 100%) !important;
        border: 1px solid rgba(212, 175, 55, 0.45) !important;
        border-radius: 12px !important;
        padding: 25px 20px 20px 20px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.7) !important;
    }

    .stTextInput div[data-baseweb="input"] {
        background-color: rgba(10, 8, 7, 0.9) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput div[data-baseweb="input"]:focus-within {
        border: 1px solid rgba(212, 175, 55, 1.0) !important;
        box-shadow: 0 0 8px rgba(212, 175, 55, 0.3) !important;
    }

    .stTextInput input {
        color: #f3e5ab !important;
        background-color: transparent !important;
        padding: 10px 15px !important;
        font-size: 13px !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(243, 229, 171, 0.4) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(70,55,30,0.95) 50%, rgba(40,30,18,0.95) 100%) !important;
        border: 1px solid rgba(212, 175, 55, 0.6) !important;
        border-radius: 8px !important;
        color: #f3e5ab !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.6) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(180deg, rgba(80,60,30,1) 0%, rgba(140,115,60,1) 50%, rgba(80,60,30,1) 100%) !important;
        border: 1px solid rgba(212, 175, 55, 1.0) !important;
        color: #ffffff !important;
    }

    div[data-testid="stAlert"] {
        background-color: rgba(20, 15, 10, 0.95) !important;
        border: 1px solid rgba(212, 175, 55, 0.6) !important;
        color: #f3e5ab !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"] p {
        color: #f3e5ab !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(14, 10, 8, 0.96);
        border-right: 1px solid rgba(212, 175, 55, 0.15);
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
          placeholder="👤   Usuário",
          label_visibility="collapsed",
      )
      senha_digitada = st.text_input(
          "Senha",
          type="password",
          key="senha_login_jurado",
          placeholder="🔒   Senha",
          label_visibility="collapsed",
      )
      st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
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

      # Botão de Logout fixo no topo direito
      st.markdown(
          f"""
          <a href="?{logout_param}" style="
              position: fixed;
              top: 35px;
              right: 18px;
              z-index: 99999;
              background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(70,55,30,0.95) 100%);
              color: #f3e5ab;
              text-decoration: none;
              padding: 7px 12px;
              border-radius: 6px;
              border: 1px solid rgba(212,175,55,0.6);
              font-size: 11px;
              font-weight: 600;
              text-transform: uppercase;
              letter-spacing: 1px;
              box-shadow: 0 4px 10px rgba(0,0,0,0.6);
          ">Sair da Conta</a>
          """,
          unsafe_allow_html=True,
      )

      st.markdown('<div style="height: 205px;"></div>', unsafe_allow_html=True)

      nome_jurado = st.session_state.jurado_logado
      st.markdown(
          f"""
          <div style="text-align: center; margin-bottom: 2px;">
              <div class="saudacao-jurado">Olá, {nome_jurado}!</div>
              <p style="color: #f3e5ab; font-family: 'Helvetica Neue', sans-serif; font-size: 11px; opacity: 0.9; position: relative; top: 15px; margin-bottom: 12px;">Selecione a categoria que você irá avaliar:</p>
          </div>
          """,
          unsafe_allow_html=True,
      )

      st.markdown(
          """
          <style>
          .category-card {
              display: flex;
              align-items: center;
              justify-content: space-between;
              background: linear-gradient(135deg, rgba(15, 11, 7, 0.90) 0%, rgba(30, 21, 12, 0.95) 100%);
              border: 1px solid rgba(212, 175, 55, 0.45);
              border-radius: 8px !important;
              padding: 8px 16px !important;
              margin-bottom: 8px !important;
              text-decoration: none !important;
              box-shadow: 0 4px 10px rgba(0, 0, 0, 0.7);
              transition: all 0.3s ease;
          }
          .category-card:hover {
              border-color: rgba(212, 175, 55, 1.0);
              background: linear-gradient(135deg, rgba(25, 18, 12, 0.95) 0%, rgba(45, 33, 19, 0.98) 100%);
          }
          .card-left {
              display: flex;
              align-items: center;
              gap: 15px;
          }
          .card-icon {
              width: 28px !important; 
              height: 28px !important;
              object-fit: contain;
          }
          .card-title {
              color: #f3e5ab;
              font-family: 'Georgia', serif;
              font-size: 13px !important; 
              font-weight: 600;
              letter-spacing: 2px;
          }
          .card-arrow {
              color: #d4af37;
              font-size: 16px !important;
          }
          </style>
          """,
          unsafe_allow_html=True,
      )

      cats_info = [
          ("Diamante", "diamante.png", "💎"),
          ("Platina", "platina.png", "🥈"),
          ("Ouro", "ouro.png", "🥇"),
          ("Prata", "prata.png", "🥈"),
          ("Aprendendo a Voar", "asas.png", "🕊️"),
      ]

      view_param = "view=jurado&" if link_jurado_exclusivo else ""
      jurado_param = f"jurado={st.session_state.jurado_logado}&"

      for cat_nome, icone_path, emoji_fallback in cats_info:
        img_b64 = img_to_base64(
            os.path.join(os.path.dirname(__file__), icone_path)
        )
        if img_b64:
          icon_html = f'<img src="{img_b64}" class="card-icon"/>'
        else:
          icon_html = f'<span style="font-size: 24px;">{emoji_fallback}</span>'

        target_url = f"?{view_param}{jurado_param}cat={cat_nome}"

        st.markdown(
            f"""
                <a href="{target_url}" class="category-card">
                    <div class="card-left">
                        {icon_html}
                        <span class="card-title">{cat_nome.upper()}</span>
                    </div>
                    <span class="card-arrow">›</span>
                </a>
                """,
            unsafe_allow_html=True,
        )

    else:
      categoria_escolhida = st.session_state.categoria_selecionada

      col_btn_1, col_btn_2 = st.columns(2)
      with col_btn_1:
        if st.button("← SAIR", use_container_width=True):
          st.session_state.jurado_logado = None
          st.session_state.categoria_selecionada = None
          st.query_params.clear()
          if link_jurado_exclusivo:
            st.query_params["view"] = "jurado"
          st.rerun()
      with col_btn_2:
        if st.button("⇄ TROCAR CATEGORIA", use_container_width=True):
          st.session_state.categoria_selecionada = None
          if "cat" in st.query_params:
            del st.query_params["cat"]
          st.rerun()

      st.markdown("<br>", unsafe_allow_html=True)

      fases_disponiveis = fases_por_categoria[categoria_escolhida]
      if len(fases_disponiveis) > 1:
        fase_escolhida = st.selectbox(
            "Fase / Etapa", fases_disponiveis, label_visibility="collapsed"
        )
      else:
        fase_escolhida = fases_disponiveis[0]

      st.markdown(
          f"""
          <div style="
              background: linear-gradient(135deg, rgba(20, 15, 10, 0.95) 0%, rgba(35, 25, 15, 0.95) 100%);
              border: 1px solid rgba(212, 175, 55, 0.6);
              border-radius: 12px;
              padding: 15px 20px;
              margin-bottom: 20px;
              display: flex;
              justify-content: space-between;
              align-items: center;
              box-shadow: 0 4px 15px rgba(0,0,0,0.6);
          ">
              <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="font-size: 28px;">💎</span>
                  <div>
                      <div style="font-size: 10px; color: #b39b6b; letter-spacing: 2px; text-transform: uppercase;">Categoria</div>
                      <div style="font-family: 'Georgia', serif; font-size: 18px; color: #e5c158; font-weight: bold; letter-spacing: 1px;">{categoria_escolhida.upper()}</div>
                  </div>
              </div>
              <div style="text-align: right;">
                  <div style="font-family: 'Georgia', serif; font-size: 14px; color: #e5c158; font-weight: bold;">{fase_escolhida.upper()}</div>
              </div>
          </div>
          """,
          unsafe_allow_html=True,
      )

      tipo_selecionado = st.radio(
          "Grupo",
          ["Condutor", "Conduzida"],
          horizontal=True,
          label_visibility="collapsed",
      )

      precisa_filtrar_classificados = (
          fase_escolhida == "Fase Final"
          and categoria_escolhida in ["Prata", "Ouro"]
      )

      if tipo_selecionado == "Condutor":
        papel_escolhido = "Condutores"
        if precisa_filtrar_classificados:
          competidores_qualificados = obter_classificados(
              categoria_escolhida, papel_escolhido
          )
        else:
          competidores_qualificados = categorias[categoria_escolhida][
              "Condutores"
          ]
      else:
        papel_escolhido = "Conduzidas"
        if precisa_filtrar_classificados:
          competidores_qualificados = obter_classificados(
              categoria_escolhida, papel_escolhido
          )
        else:
          competidores_qualificados = categorias[categoria_escolhida][
              "Conduzidas"
          ]

      if competidores_qualificados:
        competidores_ordenados = sorted(competidores_qualificados)

        if st.session_state.competidor_index >= len(competidores_ordenados):
          st.session_state.competidor_index = 0

        current_comp = competidores_ordenados[st.session_state.competidor_index]

        col_prev, col_name, col_next = st.columns([1, 5, 1])
        with col_prev:
          if st.button("〈", use_container_width=True, key="btn_prev_comp"):
            if st.session_state.competidor_index > 0:
              st.session_state.competidor_index -= 1
            else:
              st.session_state.competidor_index = (
                  len(competidores_ordenados) - 1
              )
            st.rerun()
        with col_name:
          st.markdown(
              f"""
              <div style="
                  background: linear-gradient(135deg, rgba(20, 15, 10, 0.95) 0%, rgba(35, 25, 15, 0.95) 100%);
                  border: 1px solid rgba(212, 175, 55, 0.5);
                  border-radius: 12px;
                  padding: 12px;
                  text-align: center;
                  box-shadow: 0 4px 15px rgba(0,0,0,0.6);
              ">
                  <div style="font-size: 10px; color: #b39b6b; letter-spacing: 2px; text-transform: uppercase;">Avaliando</div>
                  <div style="font-family: 'Georgia', serif; font-size: 22px; color: #e5c158; font-weight: bold; margin: 2px 0;">{current_comp}</div>
                  <div style="display: inline-block; background: rgba(212,175,55,0.15); border: 1px solid rgba(212,175,55,0.4); padding: 2px 10px; border-radius: 20px; font-size: 10px; color: #f3e5ab; text-transform: uppercase; letter-spacing: 1px;">{tipo_selecionado} ({st.session_state.competidor_index + 1}/{len(competidores_ordenados)})</div>
              </div>
              """,
              unsafe_allow_html=True,
          )
        with col_next:
          if st.button("〉", use_container_width=True, key="btn_next_comp"):
            if (
                st.session_state.competidor_index
                < len(competidores_ordenados) - 1
            ):
              st.session_state.competidor_index += 1
            else:
              st.session_state.competidor_index = 0
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        criterios = criterios_por_categoria[categoria_escolhida]
        total_criterios = len(criterios)

        notas_jurado = {}
        justificativas_jurado = {}

        for idx, (criterio_nome, descricao) in enumerate(criterios.items(), 1):
          st.markdown(
              f"""
              <div style="
                  background: linear-gradient(135deg, rgba(20, 15, 10, 0.95) 0%, rgba(35, 25, 15, 0.95) 100%);
                  border: 1px solid rgba(212, 175, 55, 0.5);
                  border-radius: 12px;
                  padding: 18px;
                  margin-bottom: 15px;
                  box-shadow: 0 4px 15px rgba(0,0,0,0.6);
              ">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                      <div style="display: flex; align-items: center; gap: 10px;">
                          <span style="font-size: 18px;">🎵</span>
                          <span style="font-size: 11px; color: #b39b6b; letter-spacing: 1.5px; text-transform: uppercase;">Critério {idx} / {total_criterios}</span>
                      </div>
                  </div>
                  <div style="font-family: 'Georgia', serif; font-size: 16px; color: #e5c158; font-weight: bold; margin-bottom: 6px;">{criterio_nome}</div>
                  <div style="font-size: 12px; color: #d4af37; opacity: 0.9; line-height: 1.4; margin-bottom: 12px;"><b>O que avaliar:</b> {descricao}</div>
              """,
              unsafe_allow_html=True,
          )

          chave_base = f"{st.session_state.jurado_logado}_{categoria_escolhida}_{fase_escolhida}_{papel_escolhido}_{current_comp}_{criterio_nome}"

          col_nota_input, col_just_input = st.columns([1, 2])
          with col_nota_input:
            nota_str = st.text_input(
                f"Nota (0 a 10) - {criterio_nome}",
                value="5.0",
                key=f"input_{chave_base}",
            )
            try:
              nota_val = float(nota_str.replace(",", "."))
            except ValueError:
              nota_val = 0.0
            notas_jurado[criterio_nome] = nota_val

          with col_just_input:
            justificativas_jurado[criterio_nome] = st.text_area(
                "Comentários (Opcional)",
                key=f"just_{chave_base}",
                height=70,
                placeholder="Deixe seu comentário aqui...",
            )
          st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✈️ ENVIAR AVALIAÇÃO", type="primary", use_container_width=True):
          for criterio_nome, nota_val in notas_jurado.items():
            novo_voto = {
                "jurado": st.session_state.jurado_logado,
                "categoria": categoria_escolhida,
                "fase": fase_escolhida,
                "papel": papel_escolhido,
                "competidor": current_comp,
                "criterio": criterio_nome,
                "nota": nota_val,
                "justificativa": justificativas_jurado[criterio_nome],
            }
            st.session_state.votos.append(novo_voto)
          st.success(
              f"✨ Avaliação enviada com sucesso para **{current_comp}**"
              f" ({fase_escolhida})!"
          )
      else:
        st.warning(
            f"⚠️ A Fase Classificatória para {papel_escolhido} em"
            f" {categoria_escolhida} ainda não possui votos suficientes para"
            " definir automaticamente os classificados da Fase Final."
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