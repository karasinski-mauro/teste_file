import streamlit as st
import random
import json
import pandas as pd
import altair as alt

# Inicializar controle de estados (verifique todas as variáveis antes de usá-las)
if "finalizou_anterior" not in st.session_state:
    st.session_state.finalizou_anterior = False
if "respondidas_ids" not in st.session_state:
    st.session_state.respondidas_ids = []
if "questoes_erradas" not in st.session_state:
    st.session_state.questoes_erradas = []
if "simulado_finalizado" not in st.session_state:
    st.session_state.simulado_finalizado = False  # Inicialize como False
if "respondeu_alguma" not in st.session_state:
    st.session_state.respondeu_alguma = False
if "bloco_questoes" not in st.session_state:
    st.session_state.bloco_questoes = []
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "acertos" not in st.session_state:
    st.session_state.acertos = 0
if "total_questoes" not in st.session_state:
    st.session_state.total_questoes = 0
if "tentativa" not in st.session_state:
    st.session_state.tentativa = 1

# Função para carregar questões
def load_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Carregar questões
questoes_codigo_conduta = load_questions("questoes_codigo_conduta.json")
questoes_plano_diretor = load_questions("questoes_plano_diretor.json")
questoes_estatuto = load_questions("questoes_estatuto.json")
questoes_lgpd = load_questions("questoes_lgpd.json")

simulados = {
    "Código de Conduta": questoes_codigo_conduta,
    "Plano Diretor da Embrapa": questoes_plano_diretor,
    "Estatuto da Embrapa": questoes_estatuto,
    "Lei Geral de Proteção de Dados": questoes_lgpd
}

st.sidebar.title("🔍 Menu Principal")
aba_selecionada = st.sidebar.radio("Escolha uma opção:", ["📝 Simulado", "📊 Dashboard de Desempenho"])

if aba_selecionada == "📝 Simulado":
    opcoes_simulado = ["Aleatório"] + list(simulados.keys())
    
    categoria_anterior = st.session_state.get("categoria_atual", None)

    # Permitir a seleção de categoria após finalização
    bloqueado = st.session_state.respondeu_alguma and not st.session_state.simulado_finalizado

    if bloqueado:
        st.sidebar.selectbox("Simulado em andamento (bloqueado):", [st.session_state.categoria_atual], disabled=True)
        escolha_simulado = st.session_state.categoria_atual
    else:
        escolha_simulado = st.sidebar.selectbox(
            "Selecione o Simulado:",
            opcoes_simulado,
            index=opcoes_simulado.index(categoria_anterior) if categoria_anterior in opcoes_simulado else 0
        )
        if categoria_anterior and escolha_simulado != categoria_anterior:
            for k in ["questoes", "indice", "acertos", "resposta_confirmada", "simulado_finalizado", "finalizou_anterior", "respondeu_alguma", "bloco_questoes"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.categoria_atual = escolha_simulado
            # Evite usar o st.experimental_rerun() aqui, pois pode causar loops inesperados

    # Inicializando variáveis de estado se necessário
    if "questoes" not in st.session_state:
        st.session_state.questoes = []
        st.session_state.indice = 0
        st.session_state.acertos = 0
        st.session_state.resposta_confirmada = False
        st.session_state.questoes_erradas = []
        st.session_state.respondeu_alguma = False
        st.session_state.total_questoes = 0
        st.session_state.tentativa = 1
        st.session_state.categoria_atual = escolha_simulado

    categoria = st.session_state.categoria_atual
    lista_questoes = simulados[categoria] if categoria != "Aleatório" else [q for sub in simulados.values() for q in sub]
    respondidas = st.session_state.respondidas_ids
    restantes = [q for q in lista_questoes if q["Questão"] not in respondidas]

    # Verifica se há questões restantes para novo bloco
    if not st.session_state.simulado_finalizado and not st.session_state.bloco_questoes:
        if len(restantes) == 0:
            st.session_state.simulado_finalizado = True
            st.warning(f"✅ Todas as questões da categoria **{categoria}** foram respondidas! Você completou esta categoria.")
        else:
            novas = random.sample(restantes, min(6, len(restantes)))
            for q in novas:
                q = q.copy()
                q["categoria"] = categoria if categoria != "Aleatório" else next(k for k, v in simulados.items() if q in v)
                st.session_state.questoes.append(q)
                st.session_state.bloco_questoes.append(q)

    st.title("📚 Simulado Concurso Embrapa")
    total_categoria = len(simulados[categoria]) if categoria != "Aleatório" else sum(len(v) for v in simulados.values())
    total_respondidas = len(st.session_state.respondidas_ids)
    st.markdown(f"**📌 Progresso geral: {total_respondidas}/{total_categoria} questões respondidas.**")
    
    questoes = st.session_state.questoes
    indice = st.session_state.indice

    # 🔒 Impede avanço se não há mais questões
    if total_respondidas >= total_categoria:
        st.success(f"🎉 Você respondeu todas as {total_categoria} questões da categoria **{categoria}**.")
        if st.button("🔁 Iniciar novo simulado"):
            # Reinicia variáveis sem fazer rerun
            st.session_state.finalizou_anterior = False
            st.session_state.simulado_finalizado = False
            st.session_state.resposta_confirmada = False
            st.session_state.acertos = 0
            st.session_state.questoes_erradas = []
            st.session_state.bloco_questoes = []
            st.session_state.respondeu_alguma = False
            st.session_state.finalizou_anterior = True
            st.session_state.indice = 0
            st.session_state.tentativa += 1
            st.session_state.categoria_atual = escolha_simulado
            # Não usamos o rerun aqui; evitamos ciclos infinitos
            st.experimental_rerun()

        st.stop()

    fim_do_bloco = (indice % 6 == 0 and indice != 0) or (indice == len(st.session_state.questoes))
    if fim_do_bloco and not st.session_state.simulado_finalizado:
        st.session_state.simulado_finalizado = True
        st.session_state.finalizou_anterior = True
        st.session_state.resposta_confirmada = False
        st.session_state.respondeu_alguma = False

    if st.session_state.simulado_finalizado:
        st.header("📊 Resultado do Bloco")
        bloco_inicio = max(0, st.session_state.indice - (st.session_state.indice % 6 or 6))
        bloco_final = st.session_state.questoes[bloco_inicio:st.session_state.indice]
        bloco_erradas = [q for q in bloco_final if q in st.session_state.questoes_erradas]
        bloco_acertos = len(bloco_final) - len(bloco_erradas)

        st.success(f"Você acertou {bloco_acertos} de {len(bloco_final)} questões neste bloco.")

        if bloco_acertos == len(bloco_final) and len(bloco_final) > 0:
            st.success("🎉 Parabéns! Você acertou todas as questões!")
            st.balloons()
        elif bloco_erradas:
            st.subheader("❌ Questões que você errou:")
            for i, questao in enumerate(bloco_erradas, 1):
                st.markdown(f"**{i}. {questao['pergunta']}**")
                st.write(f"Resposta correta: **{questao['resposta']}**")
                st.info(questao['explicacao'])

        if st.button("🔁 Iniciar novo simulado", key="btn_unico_novo_simulado"):
            st.session_state.finalizou_anterior = False
            st.session_state.simulado_finalizado = False
            st.session_state.resposta_confirmada = False
            st.session_state.acertos = 0
            st.session_state.questoes_erradas = []
            st.session_state.bloco_questoes = []
            st.session_state.respondeu_alguma = False
            st.session_state.finalizou_anterior = True
            st.session_state.indice = 0
            st.session_state.tentativa += 1

            respondidas = st.session_state.respondidas_ids
            lista_questoes = simulados[categoria] if categoria != "Aleatório" else [q for sub in simulados.values() for q in sub]
            restantes = [q for q in lista_questoes if q["Questão"] not in respondidas]

            if restantes:
                novas = random.sample(restantes, min(6, len(restantes)))
                for q in novas:
                    q = q.copy()
                    q["categoria"] = categoria if categoria != "Aleatório" else next(k for k, v in simulados.items() if q in v)
                    st.session_state.questoes.append(q)
                    st.session_state.bloco_questoes.append(q)
                st.experimental_rerun()
            else:
                st.success(f"🎉 Todas as questões da categoria **{categoria}** foram respondidas!")

    elif indice < len(questoes):
        questao_atual = questoes[indice]
        categoria = questao_atual["categoria"]
        st.markdown(f"<h2 style='font-size: 24px; font-weight: bold;'>📝 Categoria da Questão: {categoria}</h2>", unsafe_allow_html=True)
        st.subheader(f"Questão {(indice % 6) + 1} de 6")
        st.markdown(f"<p style='font-size:18px;'>{questao_atual['pergunta']}</p>", unsafe_allow_html=True)

        if not st.session_state.resposta_confirmada:
            resposta_usuario = st.radio("Escolha sua resposta:", ["Certo", "Errado"], key=f"resp_{indice}")
            if st.button("Confirmar Resposta"):
                st.session_state.resposta_confirmada = True
                st.session_state.resposta_usuario = resposta_usuario
                st.session_state.respondeu_alguma = True
                st.session_state.respondidas_ids.append(questao_atual["Questão"])

                if resposta_usuario == questao_atual["resposta"]:
                    st.session_state.acertos += 1
                else:
                    st.session_state.questoes_erradas.append(questao_atual)

                if "historico" not in st.session_state:
                    st.session_state.historico = []

                st.session_state.historico.append({
                    "Simulado": st.session_state.categoria_atual,
                    "Categoria": str(categoria),
                    "Tentativa": st.session_state.tentativa,
                    "Acertos": st.session_state.acertos,
                    "Total_Respondidas": indice + 1,
                    "Erros": (indice + 1) - st.session_state.acertos
                })
                st.experimental_rerun()
        else:
            resposta_correta = questao_atual["resposta"]
            resposta_usuario = st.session_state.resposta_usuario

            st.radio("Sua resposta:", ["Certo", "Errado"], index=["Certo", "Errado"].index(resposta_usuario), disabled=True)

            if resposta_usuario == resposta_correta:
                st.success("✔ Resposta correta!")
            else:
                st.error(f"❌ Resposta errada! A resposta correta é: **{resposta_correta}**")
            st.info(questao_atual["explicacao"])

            if st.button("➡ Próxima Questão"):
                st.session_state.indice += 1
                st.session_state.resposta_confirmada = False
                st.session_state.bloco_questoes = []
                st.experimental_rerun()

elif aba_selecionada == "📊 Dashboard de Desempenho":
    st.title("📊 Dashboard de Desempenho")

    if "historico" in st.session_state and st.session_state.historico:
        df = pd.DataFrame(st.session_state.historico)
        df["Taxa_Erros"] = (df["Erros"] / df["Total_Respondidas"]) * 100
        taxa_total = df["Erros"].sum() / df["Total_Respondidas"].sum() * 100

        if taxa_total > 50:
            st.error(f"🚨 Sua taxa de erro é de **{taxa_total:.1f}%**. Reforce os estudos!")
        elif taxa_total > 30:
            st.warning(f"⚠ Sua taxa de erro está em **{taxa_total:.1f}%**. Atenção aos pontos fracos.")
        else:
            st.success(f"🎯 Excelente! Taxa de erro de apenas **{taxa_total:.1f}%**.")

        chart = alt.Chart(df).mark_arc().encode(
            theta="Taxa_Erros:Q",
            color="Categoria:N",
            tooltip=["Categoria", "Taxa_Erros"]
        ).properties(title="Distribuição de Erros por Categoria")

        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Nenhum resultado salvo ainda. Faça um simulado para ver seu desempenho.")
