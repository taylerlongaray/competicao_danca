import streamlit as st
import pandas as pd

# Configuração inicial da página
st.set_page_config(page_title="Competição de Dança", layout="wide")

# Inicializando os dados na sessão
if "votos" not in st.session_state:
    st.session_state.votos = []

if "revelado" not in st.session_state:
    st.session_state.revelado = False

# Listas oficiais
competidores = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fernando"]
jurados = ["Jurado 1", "Jurado 2", "Jurado 3"]

# Menu lateral
st.sidebar.title("Navegação")
modo = st.sidebar.radio("Escolha o Painel:", [
    "Painel do Jurado", 
    "Painel da Organização", 
    "Telão (Público)"
])

# ---------------------------------------------------------
# 1. PAINEL DO JURADO
# ---------------------------------------------------------
if modo == "Painel do Jurado":
    st.title("📱 Painel de Votação do Jurado")
    
    jurado_atual = st.selectbox("Identifique-se (Jurado):", jurados)
    competidor_escolhido = st.selectbox("Escolha o Competidor:", competidores)
    
    criterio = st.selectbox("Critério:", ["Sincronismo", "Figurino", "Ritmo e Musicalidade"])
    nota = st.slider("Nota (0 a 10):", 0.0, 10.0, 5.0, 0.5)
    justificativa = st.text_area("Justificativa (Opcional):")
    
    if st.button("Enviar Nota", type="primary"):
        novo_voto = {
            "jurado": jurado_atual,
            "competidor": competidor_escolhido,
            "criterio": criterio,
            "nota": nota,
            "justificativa": justificativa
        }
        st.session_state.votos.append(novo_voto)
        st.success(f"Nota enviada com sucesso para {competidor_escolhido}!")

# ---------------------------------------------------------
# 2. PAINEL DA ORGANIZAÇÃO (Protegido por Senha)
# ---------------------------------------------------------
elif modo == "Painel da Organização":
    st.title("📋 Painel da Organização (Área Restrita)")
    
    # Campo de senha para bloquear o acesso de curiosos/jurados
    senha_digitada = st.text_input("Digite a senha de acesso da organização:", type="password")
    
    # Defina aqui a senha que você quiser passar para a organização:
    SENHA_MESTRE = "danca123" 
    
    if senha_digitada == SENHA_MESTRE:
        st.success("Acesso autorizado!")
        st.info("💡 Esta tela exibe todas as notas reais e justificativas completas.")
        
        if not st.session_state.votos:
            st.warning("Ainda não há votos registrados na competição.")
        else:
            df_votos = pd.DataFrame(st.session_state.votos)
            
            st.subheader("🔍 Todas as Notas e Justificativas")
            st.dataframe(df_votos, use_container_width=True)
            
            st.subheader("👥 Status dos Jurados")
            jurados_votaram = df_votos["jurado"].unique()
            col1, col2 = st.columns(2)
            with col1:
                st.write("✅ **Já votaram:**", list(jurados_votaram))
            with col2:
                pendentes = [j for j in jurados if j not in jurados_votaram]
                st.write("⏳ **Ainda não votaram:**", pendentes if pendentes else "Todos já votaram!")
                
    elif senha_digitada == "":
        st.info("🔒 Digite a senha correta acima para desbloquear o painel da organização.")
    else:
        st.error("❌ Senha incorreta! Apenas a organização possui acesso a este painel.")

# ---------------------------------------------------------
# 3. TELÃO / PÚBLICO (Com Suspense e Ranking)
# ---------------------------------------------------------
else:
    st.title("🏆 Telão da Competição (Público)")
    
    if not st.session_state.votos:
        st.info("Aguardando o início das avaliações...")
    else:
        df_votos = pd.DataFrame(st.session_state.votos)
        
        # Controle de suspense na barra lateral (também pode ser protegido por senha se quiser, mas aqui fica livre para o telão)
        st.sidebar.divider()
        st.sidebar.subheader("Controle do Telão")
        revelar_tudo = st.sidebar.checkbox("Revelar Últimas Notas e Resultados", value=st.session_state.revelado)
        st.session_state.revelado = revelar_tudo
        
        # --- RANKING DO PÚBLICO ---
        st.subheader("📊 Ranking Parcial")
        
        if not st.session_state.revelado:
            indices_para_ignorar = []
            for comp in df_votos["competidor"].unique():
                temp_df = df_votos[df_votos["competidor"] == comp]
                if not temp_df.empty:
                    indices_para_ignorar.append(temp_df.index[-1])
            df_calculo = df_votos.drop(indices_para_ignorar)
            st.caption("🔒 *As médias atuais excluem a última nota de cada competidor para manter o suspense do público.*")
        else:
            df_calculo = df_votos.copy()
            st.caption("🔓 *Notas reveladas! Resultado final da competição.*")

        if not df_calculo.empty:
            ranking = df_calculo.groupby("competidor")["nota"].mean().reset_index()
            ranking.columns = ["Competidor", "Média"]
            ranking = ranking.sort_values(by="Média", ascending=False).reset_index(drop=True)
            ranking.index = ranking.index + 1
            st.dataframe(ranking, use_container_width=True)
        else:
            st.warning("Aguardando mais votos para formar o ranking.")

        st.divider()

        # --- TABELA VISÍVEL AO PÚBLICO (Com Suspense) ---
        st.subheader("📝 Histórico de Notas (Visão do Público)")
        df_exibicao = df_votos.copy()
        
        if not st.session_state.revelado:
            indices_para_mascarar = []
            for comp in df_exibicao["competidor"].unique():
                temp_df = df_exibicao[df_exibicao["competidor"] == comp]
                if not temp_df.empty:
                    indices_para_mascarar.append(temp_df.index[-1])
            
            df_exibicao["nota"] = df_exibicao["nota"].astype(str)
            df_exibicao.loc[indices_para_mascarar, "nota"] = "🔒 [Oculta para Suspense]"
            df_exibicao.loc[indices_para_mascarar, "justificativa"] = "🔒 [Oculta]"

        st.dataframe(df_exibicao, use_container_width=True)