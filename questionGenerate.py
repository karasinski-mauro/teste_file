import streamlit as st
import json
import os

# Nome do arquivo JSON para armazenar as questões
ARQUIVO = "banco_questoes.json"
IMG_DIR = "imagens_questoes"

# Criar diretório de imagens se não existir
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def carregar_questoes():
    """Carrega o banco de questões de um arquivo JSON."""
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_questoes(questoes):
    """Salva as questões em um arquivo JSON."""
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(questoes, f, indent=4, ensure_ascii=False)
    st.success("Banco de questões salvo com sucesso!")

def salvar_imagem(imagem):
    """Salva a imagem enviada e retorna o caminho."""
    if imagem is not None:
        caminho_imagem = os.path.join(IMG_DIR, imagem.name)
        with open(caminho_imagem, "wb") as f:
            f.write(imagem.getbuffer())
        return caminho_imagem
    return None

def main():
    st.title("Gerador de Banco de Questões")
    st.write("Crie e armazene questões para seu aplicativo de perguntas.")
    
    questoes = carregar_questoes()
    
    if "pergunta" not in st.session_state:
        st.session_state.pergunta = ""
    if "resposta" not in st.session_state:
        st.session_state.resposta = None
    if "explicacao" not in st.session_state:
        st.session_state.explicacao = ""
    if "imagem" not in st.session_state:
        st.session_state.imagem = None
    
    with st.form("nova_questao"):
        pergunta = st.text_area("Digite a pergunta:", value=st.session_state.pergunta, key="pergunta")
        resposta = st.radio("Selecione a resposta correta:", ["Certo", "Errado"], index=None, key="resposta")
        explicacao = st.text_area("Digite a explicação:", value=st.session_state.explicacao, key="explicacao")
        imagem = st.file_uploader("Envie uma imagem explicativa (opcional)", type=["png", "jpg", "jpeg"], key="imagem")
        confirmar = st.form_submit_button("Adicionar Questão")
    
    if confirmar:
        if pergunta and resposta and explicacao:
            caminho_imagem = salvar_imagem(imagem)
            nova_questao = {
                "pergunta": pergunta,
                "resposta": resposta,
                "explicacao": explicacao,
                "imagem": caminho_imagem if caminho_imagem else ""
            }
            questoes.append(nova_questao)
            salvar_questoes(questoes)
            
            st.session_state.pergunta = ""
            st.session_state.resposta = None
            st.session_state.explicacao = ""
            st.session_state.imagem = None
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos antes de adicionar a questão.")
    
    st.subheader("Questões cadastradas")
    if questoes:
        for i, questao in enumerate(questoes):
            with st.expander(f"Questão {i+1}"):
                st.write(f"**Pergunta:** {questao['pergunta']}")
                st.write(f"**Resposta:** {questao['resposta']}")
                st.write(f"**Explicação:** {questao['explicacao']}")
                if questao.get("imagem"):
                    st.image(questao["imagem"], caption="Imagem explicativa", use_column_width=True)
    else:
        st.info("Nenhuma questão cadastrada ainda.")
    
if __name__ == "__main__":
    main()
