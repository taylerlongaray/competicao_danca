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
  candidatos = [
      f"fundo_{tipo_tela}.png",
      f"fundo_{tipo_tela}.jpg",
      "fundo_categorias.png",
      "fundo_categorias.jpg",
      "fundo_login.png",
      "fundo_login.jpg",
      "fundo.png",
      "fundo.jpg",
  ]

  img_encontrada = None
  for arquivo in candidatos:
    if os.path.exists(arquivo):
      img_encontrada = arquivo
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

try:
  qp = st.query_params
  if "jurado" in qp and not st.session_state.jurado_logado:
    st.session_state.jurado_logado = qp["jurado"]
  if "cat" in qp and not st.session_state.categoria_selecionada:
    st.session_state.categoria_selecionada = qp["cat"]
except Exception:
  pass

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

try:
  query_params = st.query_params
  link_jurado_exclusivo = query_params.get("view") == "jurado"
except Exception:
  link_jurado_exclusivo = False

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
    st.markdown(obter_fundo_css("painel"), unsafe_allow_html=True)
elif modo == "Telão (Público)":
  st.markdown(obter_fundo_css("telao"), unsafe_allow_html=True)
else:
  st.markdown(obter_fundo_css("painel"), unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        max-width: 650px !important;
        margin: 0 auto !important;
    }

    h1, h2, h3 {
        color: #e5c158 !important;
        font-family: 'Georgia', serif;
        text-align: center;
        letter-spacing: 1px;
    }

    div[data-testid="column"]:has(input[type="password"]) {
        max-width: 330px !important; 
        margin: 0 auto !important; 
        float: none !important;
        background-color: transparent !important; 
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 6px !important;
        padding: 30px 25px 25px 25px !important;
    }

    .stTextInput div[data-baseweb="input"] {
        background-color: rgba(10, 8, 7, 0.8) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        border-radius: 30px !important;
    }
    
    .stTextInput input {
        color: #f3e5ab !important;
        background-color: transparent !important;
        padding: 12px 20px !important;
        font-size: 14px !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(14, 10, 8, 0.96);
        border-right: 1px solid rgba(212, 175, 55, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

if modo == "Painel do Jurado":
  if st.session_state.jurado_logado is None:
    st.markdown('<div style="height: 43vh;"></div>', unsafe_allow_html=True)
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
      st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
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
      # =======================================================================
      # RESET DE ROLAGEM INTERNA DO STREAMLIT + ESPAÇADOR DE 20vh
      # =======================================================================
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
              padding: 10px 18px !important;
              margin-bottom: 10px !important;
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
          
          .stButton > button {
              background: linear-gradient(180deg, rgba(40,30,18,0.95) 0%, rgba(70,55,30,0.95) 50%, rgba(40,30,18,0.95) 100%) !important;
              border: 1px solid rgba(212, 175, 55, 0.5) !important;
              border-radius: 8px !important;
              color: #f3e5ab !important;
              text-transform: uppercase !important;
              letter-spacing: 2px !important;
              font-weight: 600 !important;
              padding: 10px 18px !important;
              width: 100% !important;
              margin-top: 5px !important;
              box-shadow: 0 4px 10px rgba(0, 0, 0, 0.6) !important;
          }
          .stButton > button:hover {
              border: 1px solid rgba(212, 175, 55, 1.0) !important;
          }
          </style>
          
          <script>
              // Força o container interno de scroll do Streamlit a voltar ao topo exato
              const container = document.querySelector('[data-testid="stAppViewContainer"]');
              if (container) {
                  container.scrollTop = 0;
              }
              window.scrollTo(0, 0);
          </script>
          """,
          unsafe_allow_html=True,
      )

      # Ajuste a altura aqui se quiser subir mais (ex: 15vh) ou descer (ex: 25vh)
      st.markdown('<div style="height: 20vh;"></div>', unsafe_allow_html=True)

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
        img_b64 = img_to_base64(icone_path)
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

      if st.button("Sair da Conta"):
        st.session_state.jurado_logado = None
        st.session_state.categoria_selecionada = None
        st.query_params.clear()
        if link_jurado_exclusivo:
          st.query_params["view"] = "jurado"
        st.rerun()

    else:
      categoria_escolhida = st.session_state.categoria_selecionada

      col_info, col_voltar = st.columns([2.5, 1.5])
      with col_info:
        st.success(
            f"✨ **{st.session_state.jurado_logado}** | Categoria:"
            f" **{categoria_escolhida}**"
        )
      with col_voltar:
        if st.button("⬅️ Trocar Categoria"):
          st.session_state.categoria_selecionada = None
          if "cat" in st.query_params:
            del st.query_params["cat"]
          st.rerun()

      st.markdown("---")

      fases_disponiveis = fases_por_categoria[categoria_escolhida]
      if len(fases_disponiveis) > 1:
        fase_escolhida = st.selectbox("Fase / Etapa", fases_disponiveis)
      else:
        fase_escolhida = fases_disponiveis[0]
        st.text_input("Fase / Etapa", value=fase_escolhida, disabled=True)

      st.markdown("##### Selecione o Grupo")
      tipo_selecionado = st.radio(
          "Grupo",
          ["Condutor", "Conduzida"],
          horizontal=True,
          label_visibility="collapsed",
      )

      if tipo_selecionado == "Condutor":
        papel_escolhido = "Condutores"
        competidores_ordenados = sorted(
            categorias[categoria_escolhida]["Condutores"]
        )
        competidor_escolhido = st.selectbox(
            "Condutor", competidores_ordenados, label_visibility="collapsed"
        )
      else:
        papel_escolhido = "Conduzidas"
        competidores_ordenados = sorted(
            categorias[categoria_escolhida]["Conduzidas"]
        )
        competidor_escolhido = st.selectbox(
            "Conduzida", competidores_ordenados, label_visibility="collapsed"
        )

      st.markdown("---")
      st.markdown(
          f"<h3>Avaliação para: {competidor_escolhido} ({tipo_selecionado}) —"
          f" <i>{fase_escolhida}</i></h3>",
          unsafe_allow_html=True,
      )

      notas_jurado = {}
      justificativas_jurado = {}

      for criterio_nome, descricao in criterios_por_categoria[
          categoria_escolhida
      ].items():
        with st.container(border=True):
          st.markdown(f"<h4>{criterio_nome}</h4>", unsafe_allow_html=True)
          st.info(f"💡 **O que avaliar:** {descricao}")

          chave_base = f"{st.session_state.jurado_logado}_{categoria_escolhida}_{fase_escolhida}_{papel_escolhido}_{competidor_escolhido}_{criterio_nome}"

          col_nota, col_just = st.columns([1, 2])
          with col_nota:
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

          with col_just:
            justificativas_jurado[criterio_nome] = st.text_area(
                "Justificativa (Opcional)",
                key=f"just_{chave_base}",
                height=70,
            )

      st.write("")
      if st.button("ENVIAR TODAS AS NOTAS", type="primary"):
        for criterio_nome, nota_val in notas_jurado.items():
          novo_voto = {
              "jurado": st.session_state.jurado_logado,
              "categoria": categoria_escolhida,
              "fase": fase_escolhida,
              "papel": papel_escolhido,
              "competidor": competidor_escolhido,
              "criterio": criterio_nome,
              "nota": nota_val,
              "justificativa": justificativas_jurado[criterio_nome],
          }
          st.session_state.votos.append(novo_voto)

        st.success(
            f"✨ Notas enviadas com sucesso por {st.session_state.jurado_logado}"
            f" para **{competidor_escolhido}** ({fase_escolhida})!"
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