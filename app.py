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

jurados = ["Jurado 1", "Jurado 2", "Jurado 3"]

# Menu lateral
st.sidebar.title("Navegação")
modo = st.sidebar.radio(
    "Escolha o Painel:",
    ["Painel do Jurado", "Painel da Organização", "Telão (Público)"],
)

# ---------------------------------------------------------
# 1. PAINEL DO JURADO (Com Seleção de Categoria)
# ---------------------------------------------------------
if modo == "Painel do Jurado":
  st.title("📱 Painel de Votação do Jurado")

  jurado_atual = st.selectbox("Identifique-se (Jurado):", jurados)

  # 1. Escolhe a Categoria primeiro
  categoria_escolhida = st.selectbox(
      "Escolha a Categoria:", list(categorias.keys())
  )

  # 2. Filtra os competidores apenas daquela categoria selecionada
  competidores_da_categoria = categorias[categoria_escolhida]
  competidor_escolhido = st.selectbox(
      "Escolha o Competidor:", competidores_da_categoria
  )

  criterio = st.selectbox(
      "Critério:", ["Sincronismo", "Figurino", "Ritmo e Musicalidade"]
  )
  nota = st.slider("Nota (0 a 10):", 0.0, 10.0, 5.0, 0.1)
  justificativa = st.text_area("Justificativa (Opcional):")

  if st.button("Enviar Nota", type="primary"):
    novo_voto = {
        "jurado": jurado_atual,
        "categoria": categoria_escolhida,
        "competidor": competidor_escolhido,
        "criterio": criterio,
        "nota": nota,
        "justificativa": justificativa,
    }
    st.session_state.votos.append(novo_voto)
    st.success(
        f"Nota enviada com sucesso para {competidor_escolhido} ({categoria_escolhida})!"
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
# 3. TELÃO / PÚBLICO (Com Abas por Categoria visíveis sempre)
# ---------------------------------------------------------
else:
  st.title("🏆 Telão da Competição por Categorias")

  # Controle de suspense na barra lateral
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

  # Criando as abas sempre visíveis na ordem exata definida no dicionário
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

  # Preenchendo cada aba com os dados específicos daquela categoria
  for i, categoria_nome in enumerate(nomes_abas):
    with abas[i]:
      st.subheader(f"📊 Categoria: {categoria_nome}")
      competidores_da_categoria = categorias[categoria_nome]

      df_cat = df_votos[df_votos["competidor"].isin(competidores_da_categoria)]

      if df_cat.empty:
        st.info(
            f"Nenhum voto registrado ainda para os competidores desta categoria:"
            f" {', '.join(competidores_da_categoria)}"
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
          ranking.columns = ["Competidor", "Média"]
          ranking = ranking.sort_values(by="Média", ascending=False).reset_index(
              drop=True
          )
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