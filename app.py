import pandas as pd
import streamlit as st

# Configuração inicial da página
st.set_page_config(page_title="Competição de Dança", layout="wide")

# Inicializando os dados na sessão
if "votos" not in st.session_state:
  st.session_state.votos = []

if "revelado" not in st.session_state:
  st.session_state.revelado = False

# Categorias ordenadas exatamente na ordem solicitada
categorias = {
    "Aprendendo a Voar": ["Fernando"],
    "Prata": ["Elena"],
    "Ouro": ["Carla", "Diego"],
    "Platina": ["Bruno"],
    "Diamante": ["Ana"],
}

# Critérios oficiais detalhados por categoria (sem a numeração no título)
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

jurados = ["Jurado 1", "Jurado 2", "Jurado 3"]

# Menu lateral
st.sidebar.title("Navegação")
modo = st.sidebar.radio(
    "Escolha o Painel:",
    ["Painel do Jurado", "Painel da Organização", "Telão (Público)"],
)

# ---------------------------------------------------------
# 1. PAINEL DO JURADO (Votação em todos os critérios da categoria)
# ---------------------------------------------------------
if modo == "Painel do Jurado":
  st.title("📱 Painel de Votação do Jurado")

  # 1. Categoria primeiro
  categoria_escolhida = st.selectbox(
      "Escolha a Categoria:", list(categorias.keys())
  )

  # 2. Identificação do Jurado
  jurado_atual = st.selectbox("Identifique-se (Jurado):", jurados)

  # 3. Competidor da categoria
  competidores_da_categoria = categorias[categoria_escolhida]
  competidor_escolhido = st.selectbox(
      "Escolha o Competidor:", competidores_da_categoria
  )

  st.divider()
  st.subheader(
      f"📋 Avaliação de Todos os Critérios para: {competidor_escolhido}"
  )

  # Dicionários temporários para capturar as notas de cada critério
  notas_jurado = {}
  justificativas_jurado = {}

  # Loop por cada critério oficial da categoria escolhida
  for criterio_nome, descricao in criterios_por_categoria[
      categoria_escolhida
  ].items():
    st.markdown(f"### 🔹 {criterio_nome}")
    st.info(f"💡 **O que avaliar:** {descricao}")

    notas_jurado[criterio_nome] = st.slider(
        f"Nota para {criterio_nome} (0 a 10):",
        0.0,
        10.0,
        5.0,
        0.1,
        key=f"slider_{criterio_nome}",
    )
    justificativas_jurado[criterio_nome] = st.text_area(
        f"Justificativa para {criterio_nome} (Opcional):",
        key=f"just_{criterio_nome}",
    )
    st.write("")

  if st.button("Enviar Todas as Notas", type="primary"):
    # Salva uma linha de voto para cada critério avaliado
    for criterio_nome, nota_val in notas_jurado.items():
      novo_voto = {
          "jurado": jurado_atual,
          "categoria": categoria_escolhida,
          "competidor": competidor_escolhido,
          "criterio": criterio_nome,
          "nota": nota_val,
          "justificativa": justificativas_jurado[criterio_nome],
      }
      st.session_state.votos.append(novo_voto)

    st.success(
        f"Todas as notas foram enviadas com sucesso para {competidor_escolhido}"
        f" ({categoria_escolhida})!"
    )

# ---------------------------------------------------------
# 2. PAINEL DA ORGANIZAÇÃO (Protegido por Senha)
# ---------------------------------------------------------
elif modo == "Painel da Organização":
  st.title("📋 Painel da Organização (Área Restrita)")

  senha_digitada = st.text_input(
      "Digite a senha de acesso da organização:", type="password"
  )
  SENHA_MESTRE = "danca123"

  if senha_digitada == SENHA_MESTRE:
    st.success("Acesso autorizado!")

    if not st.session_state.votos:
      st.warning("Ainda não há votos registrados na competição.")
    else:
      df_votos = pd.DataFrame(st.session_state.votos)
      st.subheader("🔍 Todas as Notas e Justificativas")
      st.dataframe(df_votos, use_container_width=True)

  elif senha_digitada != "":
    st.error("❌ Senha incorreta!")

# ---------------------------------------------------------
# 3. TELÃO / PÚBLICO
# ---------------------------------------------------------
else:
  st.title("🏆 Telão da Competição por Categorias")

  st.sidebar.divider()
  st.sidebar.subheader("Controle do Telão")
  revelar_tudo = st.sidebar.checkbox(
      "Revelar Últimas Notas e Resultados", value=st.session_state.revelado
  )
  st.session_state.revelado = revelar_tudo

  if not st.session_state.votos:
    st.info(
        "💡 As abas abaixo já estão separadas por categoria. Aguardando o"
        " envio do primeiro voto para preencher os rankings!"
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
            "competidor",
            "criterio",
            "nota",
            "justificativa",
        ]
    )

  for i, categoria_nome in enumerate(nomes_abas):
    with abas[i]:
      st.subheader(f"📊 Categoria: {categoria_nome}")
      competidores_da_categoria = categorias[categoria_nome]

      df_cat = df_votos[df_votos["competidor"].isin(competidores_da_categoria)]

      if df_cat.empty:
        st.info(
            "Nenhum voto registrado ainda para os competidores desta"
            f" categoria: {', '.join(competidores_da_categoria)}"
        )
      else:
        if not st.session_state.revelado:
          indices_para_ignorar = []
          for comp in df_cat["competidor"].unique():
            temp_df = df_cat[df_cat["competidor"] == comp]
            if not temp_df.empty:
              indices_para_ignorar.append(temp_df.index[-1])
          df_calculo = df_cat.drop(indices_para_ignorar)
        else:
          df_calculo = df_cat.copy()

        if not df_calculo.empty:
          ranking = (
              df_calculo.groupby("competidor")["nota"].mean().reset_index()
          )
          ranking.columns = ["Competidor", "Média Geral"]
          ranking = ranking.sort_values(
              by="Média Geral", ascending=False
          ).reset_index(drop=True)
          ranking.index = ranking.index + 1

          st.markdown("### Ranking da Categoria")
          st.dataframe(ranking, use_container_width=True)
        else:
          st.warning("Aguardando mais votos para formar o ranking parcial.")

        st.markdown("### Histórico de Notas desta Categoria")
        df_exibicao_cat = df_cat.copy()
        if not st.session_state.revelado:
          indices_para_mascarar = []
          for comp in df_exibicao_cat["competidor"].unique():
            temp_df = df_exibicao_cat[df_exibicao_cat["competidor"] == comp]
            if not temp_df.empty:
              indices_para_mascarar.append(temp_df.index[-1])

          df_exibicao_cat["nota"] = df_exibicao_cat["nota"].astype(str)
          df_exibicao_cat.loc[indices_para_mascarar, "nota"] = (
              "🔒 [Oculta para Suspense]"
          )
          df_exibicao_cat.loc[indices_para_mascarar, "justificativa"] = (
              "🔒 [Oculta]"
          )

        st.dataframe(df_exibicao_cat, use_container_width=True)