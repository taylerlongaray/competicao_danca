import pandas as pd
import streamlit as st

# Configuração inicial da página
st.set_page_config(page_title="Competição de Dança", layout="wide")

# Inicializando os dados na sessão
if "votos" not in st.session_state:
  st.session_state.votos = []

if "revelado" not in st.session_state:
  st.session_state.revelado = False

if "jurado_logado" not in st.session_state:
  st.session_state.jurado_logado = None

# Categorias organizadas por Condutores e Conduzidas
categorias = {
    "Aprendendo a Voar": {
        "Condutores": ["Fernando"],
        "Conduzidas": ["Juliana"],
    },
    "Prata": {"Condutores": ["Marcos"], "Conduzidas": ["Elena"]},
    "Ouro": {"Condutores": ["Diego"], "Conduzidas": ["Carla"]},
    "Platina": {"Condutores": ["Bruno"], "Conduzidas": ["Beatriz"]},
    "Diamante": {
        "Condutores": ["Alan", "Léo", "William", "Maick", "Luan", "Henrique"],
        "Conduzidas": ["Marluce", "Sidiane", "Sah", "Cléo", "Viih", "Carol"],
    },
}

# Critérios oficiais detalhados por categoria
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

st.sidebar.title("Navegação")
modo = st.sidebar.radio(
    "Escolha o Painel:",
    ["Painel do Jurado", "Painel da Organização", "Telão (Público)"],
)

# ---------------------------------------------------------
# 1. PAINEL DO JURADO (Competidores em ordem alfabética)
# ---------------------------------------------------------
if modo == "Painel do Jurado":
  st.title("📱 Painel de Votação do Jurado")

  if st.session_state.jurado_logado is None:
    st.info("🔒 Insira suas credenciais de jurado para acessar o painel.")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
      login_selecionado = st.selectbox(
          "Selecione o seu usuário:", ["Selecione..."] + list(senhas_jurados.keys())
      )
    with col2:
      senha_digitada = st.text_input(
          "Senha:", type="password", key="senha_login_jurado"
      )
    with col3:
      st.write("")
      st.write("")
      if st.button("Entrar", type="primary"):
        if login_selecionado != "Selecione...":
          if senha_digitada == senhas_jurados[login_selecionado]:
            st.session_state.jurado_logado = login_selecionado
            st.rerun()
          else:
            st.error("❌ Senha incorreta!")
        else:
          st.error("Selecione um jurado.")
  else:
    col_info, col_sair = st.columns([3, 1])
    with col_info:
      st.success(f"Logado com sucesso como: **{st.session_state.jurado_logado}**")
    with col_sair:
      if st.button("Sair (Logout)"):
        st.session_state.jurado_logado = None
        st.rerun()

    st.divider()

    categoria_escolhida = st.selectbox(
        "Escolha a Categoria:", list(categorias.keys())
    )
    tipo_selecionado = st.radio(
        "Selecione o Grupo:", ["Condutor", "Conduzida"], horizontal=True
    )

    # Competidores ordenados alfabeticamente apenas para o jurado
    if tipo_selecionado == "Condutor":
      papel_escolhido = "Condutores"
      competidores_ordenados = sorted(categorias[categoria_escolhida]["Condutores"])
      competidor_escolhido = st.selectbox(
          "Selecionar Condutor:", competidores_ordenados
      )
    else:
      papel_escolhido = "Conduzidas"
      competidores_ordenados = sorted(categorias[categoria_escolhida]["Conduzidas"])
      competidor_escolhido = st.selectbox(
          "Selecionar Conduzida:", competidores_ordenados
      )

    st.divider()
    st.subheader(
        f"📋 Avaliação de Todos os Critérios para: {competidor_escolhido}"
        f" ({tipo_selecionado})"
    )

    notas_jurado = {}
    justificativas_jurado = {}

    for criterio_nome, descricao in criterios_por_categoria[
        categoria_escolhida
    ].items():
      st.markdown(f"### 🔹 {criterio_nome}")
      st.info(f"💡 **O que avaliar:** {descricao}")

      chave_base = f"{st.session_state.jurado_logado}_{categoria_escolhida}_{papel_escolhido}_{competidor_escolhido}_{criterio_nome}"

      nota_str = st.text_input(
          f"Digite a nota para {criterio_nome} (0 a 10):",
          value="5.0",
          key=f"input_{chave_base}",
      )
      try:
        nota_val = float(nota_str.replace(",", "."))
      except ValueError:
        nota_val = 0.0

      justificativas_jurado[criterio_nome] = st.text_area(
          f"Justificativa para {criterio_nome} (Opcional):",
          key=f"just_{chave_base}",
      )
      notas_jurado[criterio_nome] = nota_val
      st.write("")

    if st.button("Enviar Todas as Notas", type="primary"):
      for criterio_nome, nota_val in notas_jurado.items():
        novo_voto = {
            "jurado": st.session_state.jurado_logado,
            "categoria": categoria_escolhida,
            "papel": papel_escolhido,
            "competidor": competidor_escolhido,
            "criterio": criterio_nome,
            "nota": nota_val,
            "justificativa": justificativas_jurado[criterio_nome],
        }
        st.session_state.votos.append(novo_voto)

      st.success(
          f"Todas as notas foram enviadas com sucesso por"
          f" {st.session_state.jurado_logado} para {competidor_escolhido}!"
      )

# ---------------------------------------------------------
# 2. PAINEL DA ORGANIZAÇÃO
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
      st.subheader("🔍 Todas as Notas e Justificativas Reais")
      st.dataframe(df_votos, use_container_width=True)
  elif senha_digitada != "":
    st.error("❌ Senha incorreta!")

# ---------------------------------------------------------
# 3. TELÃO / PÚBLICO (Ranking ordenado do maior ao menor)
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
        "💡 As abas abaixo estão separadas por categoria. Aguardando o envio"
        " dos votos!"
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
            "papel",
            "competidor",
            "criterio",
            "nota",
            "justificativa",
        ]
    )

  for i, categoria_nome in enumerate(nomes_abas):
    with abas[i]:
      st.subheader(f"📊 Categoria: {categoria_nome}")
      df_cat = df_votos[df_votos["categoria"] == categoria_nome]

      if df_cat.empty:
        st.info("Nenhum voto registrado ainda para esta categoria.")
      else:
        sub_abas = st.tabs(["Condutores", "Conduzidas"])
        papeis = ["Condutores", "Conduzidas"]

        for j, papel_nome in enumerate(papeis):
          with sub_abas[j]:
            st.markdown(f"#### Divisão: {papel_nome}")
            df_papel = df_cat[df_cat["papel"] == papel_nome]

            if df_papel.empty:
              st.info(f"Sem votos para {papel_nome} nesta categoria ainda.")
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
                ranking.columns = ["Competidor", "Média Geral"]
                # Ranking ordenado da maior para a menor nota
                ranking = ranking.sort_values(
                    by="Média Geral", ascending=False
                ).reset_index(drop=True)
                ranking.index = ranking.index + 1

                st.markdown("##### 🏆 Ranking de Classificação")
                st.dataframe(ranking, use_container_width=True)
              else:
                st.warning("Aguardando mais votos para o ranking parcial.")

              st.markdown("##### 📝 Histórico de Notas")
              # Apenas notas (sem justificativas) na visão pública do telão
              df_exibicao_papel = df_papel[
                  ["jurado", "categoria", "papel", "competidor", "criterio", "nota"]
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