import streamlit as st
import random
import json
import pandas as pd
import altair as alt

# --- Função para carregar as questões de um arquivo JSON ---
def load_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Carregar as questões a partir dos arquivos JSON ---
questoes_codigo_conduta = load_questions("questoes_codigo_conduta.json")
questoes_plano_diretor   = load_questions("questoes_plano_diretor.json")
questoes_estatuto        = load_questions("questoes_estatuto.json")
questoes_lgpd            = load_questions("questoes_lgpd.json")

# --- Mapeamento dos simulados ---
simulados = {
    "Código de Conduta": questoes_codigo_conduta,
    "Plano Diretor da Embrapa": questoes_plano_diretor,
    "Estatuto da Embrapa": questoes_estatuto,
    "Lei Geral de Proteção de Dados": questoes_lgpd
}

# --- Criando um MENU LATERAL ---
st.sidebar.title("🔍 Menu Principal")


# Opções de abas
aba_selecionada = st.sidebar.radio("Escolha uma opção:", ["📝 Simulado", "📊 Dashboard de Desempenho"])

if aba_selecionada == "📝 Simulado":
    opcoes_simulado = ["Aleatório"] + list(simulados.keys())
    escolha_simulado = st.sidebar.selectbox("Selecione o Simulado:", opcoes_simulado)

    # --- Se o usuário mudar a categoria, reinicia o simulado ---
    if "categoria_atual" not in st.session_state or st.session_state.categoria_atual != escolha_simulado:
        st.session_state.indice = 0
        st.session_state.acertos = 0
        st.session_state.resposta_confirmada = False
        st.session_state.categoria_atual = escolha_simulado
        st.session_state.tentativa = st.session_state.tentativa + 1 if "tentativa" in st.session_state else 1

        # Configura as questões baseadas na escolha
        if escolha_simulado == "Aleatório":
            questoes = []
            for categoria, lista_questoes in simulados.items():
                for q in lista_questoes:
                    nova_questao = q.copy()
                    nova_questao["categoria"] = categoria
                    questoes.append(nova_questao)
        else:
            questoes = simulados[escolha_simulado]
            for q in questoes:
                q["categoria"] = escolha_simulado  

        # Embaralha as questões e armazena na sessão
        st.session_state.questoes = random.sample(questoes, len(questoes))
        st.session_state.total_questoes = len(st.session_state.questoes)

    # --- Exibição do Simulado ---
    st.title("📚 Simulado Concurso Embrapa")
    st.write("Organizado por Mauro Alessandro Karasinski")

    indice = st.session_state.indice
    total_questoes = st.session_state.total_questoes
    questoes = st.session_state.questoes
    resposta_confirmada = st.session_state.resposta_confirmada

    if indice < total_questoes:
        categoria = questoes[indice]["categoria"]
        st.write(f"**📝 Categoria da Questão: {categoria}**")

        st.subheader(f"Questão {indice + 1} de {total_questoes}")

        # Exibir a questão com fonte maior
        st.markdown(f"<p style='font-size:18px;'>{questoes[indice]['pergunta']}</p>", unsafe_allow_html=True)

        if not resposta_confirmada:
            resposta_usuario = st.radio("Escolha sua resposta:", ["Certo", "Errado"], key=f"resp_{indice}")

            if st.button("Confirmar Resposta"):
                if resposta_usuario:
                    st.session_state.resposta_confirmada = True
                    st.session_state.resposta_usuario = resposta_usuario

                    if resposta_usuario == questoes[indice]["resposta"]:
                        st.session_state.acertos += 1

                    # 🔄 Atualizar desempenho automaticamente
                    if "historico" not in st.session_state:
                        st.session_state.historico = []

                    # Garantir que a contagem de questões respondidas seja feita corretamente
                    total_respondidas = indice + 1  

                    st.session_state.historico.append({
                        "Simulado": st.session_state.categoria_atual,
                        "Categoria": str(categoria),
                        "Tentativa": st.session_state.tentativa,
                        "Acertos": st.session_state.acertos,
                        "Total_Respondidas": total_respondidas,
                        "Erros": total_respondidas - st.session_state.acertos
                    })

                    st.rerun()

        else:
            resposta_correta = questoes[indice]["resposta"]
            resposta_usuario = st.session_state.resposta_usuario

            st.radio("Sua resposta:", ["Certo", "Errado"], index=["Certo", "Errado"].index(resposta_usuario), disabled=True)

            if resposta_usuario == resposta_correta:
                st.success("✔ Resposta correta!")
            else:
                st.error(f"❌ Resposta errada! A resposta correta é: **{resposta_correta}**")

            st.info(questoes[indice]["explicacao"])
            # Exibir imagem se existir
            if "imagem" in questoes[indice] and questoes[indice]["imagem"]:
                caminho_imagem = questoes[indice]["imagem"]
                
                # Tenta exibir a imagem do diretório local
                try:
                    st.image(caminho_imagem, caption="Imagem ilustrativa", use_column_width=True)
                except Exception as e:
                    st.write(f"Erro ao carregar a imagem: {e}")


            if st.button("➡ Próxima Questão"):
                st.session_state.indice += 1
                st.session_state.resposta_confirmada = False
                st.rerun()

# --- 📊 Dashboard de Desempenho ---
elif aba_selecionada == "📊 Dashboard de Desempenho":
    st.title("📊 Dashboard de Desempenho")

    if "historico" in st.session_state and st.session_state.historico:
        df_desempenho = pd.DataFrame(st.session_state.historico)

        # 🔹 Cálculo da taxa de erros (%)
        df_desempenho["Taxa_Erros"] = (df_desempenho["Erros"] / df_desempenho["Total_Respondidas"]) * 100

        # 🔥 Termômetro de desempenho
        taxa_erro_total = df_desempenho["Erros"].sum() / df_desempenho["Total_Respondidas"].sum() * 100

        if taxa_erro_total > 50:
            st.error(f"🚨 Atenção! Sua taxa de erro é de **{taxa_erro_total:.1f}%**. Você precisa revisar os conteúdos!")
        elif taxa_erro_total > 30:
            st.warning(f"⚠ Você está errando bastante ({taxa_erro_total:.1f}%). Vale a pena revisar alguns tópicos.")
        else:
            st.success(f"🎉 Excelente! Sua taxa de erro é de apenas **{taxa_erro_total:.1f}%**. Continue assim!")

        # 🥧 Gráfico de Pizza - Distribuição de Erros por Categoria
        chart_pizza_erros = alt.Chart(df_desempenho).mark_arc().encode(
            theta="Taxa_Erros:Q",
            color="Categoria:N",
            tooltip=["Categoria", "Taxa_Erros"]
        ).properties(title="Distribuição de Erros por Categoria")

        st.altair_chart(chart_pizza_erros, use_container_width=True)

    else:
        st.write("Nenhum resultado salvo ainda. Complete um simulado para visualizar seu desempenho.")

