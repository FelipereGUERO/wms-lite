import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="WMS Lite",
    page_icon="📦",
    layout="wide"
)

# =========================
# TÍTULO DO SISTEMA
# =========================

st.title("📦 WMS Lite")
st.caption("Sistema básico para controle de estoque, recebimento, movimentações, picking e inventário.")

# =========================
# MENU LATERAL
# =========================

menu = st.sidebar.selectbox(
    "Menu principal",
    [
        "Dashboard",
        "Cadastro de Produtos",
        "Cadastro de Localizações",
        "Recebimento",
        "Consulta de Estoque",
        "Movimentação Interna",
        "Picking",
        "Expedição",
        "Inventário",
        "Relatórios"
    ]
)

# =========================
# BASE TEMPORÁRIA EM MEMÓRIA
# =========================
# Nesta primeira versão, os dados ficam temporários.
# Depois vamos evoluir para salvar em arquivos e, no futuro, banco de dados.

if "produtos" not in st.session_state:
    st.session_state.produtos = []

if "localizacoes" not in st.session_state:
    st.session_state.localizacoes = []

if "estoque" not in st.session_state:
    st.session_state.estoque = []

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = []


# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":
    st.header("Dashboard Geral")

    total_produtos = len(st.session_state.produtos)
    total_localizacoes = len(st.session_state.localizacoes)
    total_itens_estoque = len(st.session_state.estoque)

    quantidade_total = 0
    for item in st.session_state.estoque:
        quantidade_total += item["Quantidade"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Produtos cadastrados", total_produtos)
    col2.metric("Localizações cadastradas", total_localizacoes)
    col3.metric("Itens em estoque", total_itens_estoque)
    col4.metric("Quantidade total", quantidade_total)

    st.subheader("Últimas movimentações")

    if st.session_state.movimentacoes:
        df_mov = pd.DataFrame(st.session_state.movimentacoes)
        st.dataframe(df_mov, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada até o momento.")


# =========================
# CADASTRO DE PRODUTOS
# =========================

elif menu == "Cadastro de Produtos":
    st.header("Cadastro de Produtos")

    with st.form("form_produto"):
        sku = st.text_input("SKU / Código do Produto")
        descricao = st.text_input("Descrição")
        unidade = st.selectbox("Unidade de Medida", ["UN", "KG", "M", "CX", "PC"])
        categoria = st.text_input("Categoria / Família")
        estoque_minimo = st.number_input("Estoque mínimo", min_value=0, step=1)
        ativo = st.selectbox("Status", ["Ativo", "Inativo"])

        salvar = st.form_submit_button("Salvar produto")

        if salvar:
            if sku and descricao:
                produto = {
                    "SKU": sku,
                    "Descrição": descricao,
                    "Unidade": unidade,
                    "Categoria": categoria,
                    "Estoque mínimo": estoque_minimo,
                    "Status": ativo
                }

                st.session_state.produtos.append(produto)
                st.success("Produto cadastrado com sucesso.")
            else:
                st.warning("Preencha pelo menos o SKU e a descrição.")

    st.subheader("Produtos cadastrados")

    if st.session_state.produtos:
        df_produtos = pd.DataFrame(st.session_state.produtos)
        st.dataframe(df_produtos, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")


# =========================
# CADASTRO DE LOCALIZAÇÕES
# =========================

elif menu == "Cadastro de Localizações":
    st.header("Cadastro de Localizações")

    with st.form("form_localizacao"):
        codigo_local = st.text_input("Código da localização")
        tipo_local = st.selectbox(
            "Tipo de localização",
            ["Recebimento", "Estoque", "Picking", "Expedição", "Quarentena", "Buffer"]
        )
        corredor = st.text_input("Corredor")
        coluna = st.text_input("Coluna")
        nivel = st.text_input("Nível")
        status = st.selectbox("Status", ["Ativa", "Bloqueada", "Inativa"])

        salvar = st.form_submit_button("Salvar localização")

        if salvar:
            if codigo_local:
                localizacao = {
                    "Localização": codigo_local,
                    "Tipo": tipo_local,
                    "Corredor": corredor,
                    "Coluna": coluna,
                    "Nível": nivel,
                    "Status": status
                }

                st.session_state.localizacoes.append(localizacao)
                st.success("Localização cadastrada com sucesso.")
            else:
                st.warning("Informe o código da localização.")

    st.subheader("Localizações cadastradas")

    if st.session_state.localizacoes:
        df_locais = pd.DataFrame(st.session_state.localizacoes)
        st.dataframe(df_locais, use_container_width=True)
    else:
        st.info("Nenhuma localização cadastrada.")


# =========================
# RECEBIMENTO
# =========================

elif menu == "Recebimento":
    st.header("Recebimento de Materiais")

    produtos_disponiveis = [p["SKU"] for p in st.session_state.produtos]
    localizacoes_disponiveis = [l["Localização"] for l in st.session_state.localizacoes]

    if not produtos_disponiveis:
        st.warning("Cadastre pelo menos um produto antes de realizar o recebimento.")
    elif not localizacoes_disponiveis:
        st.warning("Cadastre pelo menos uma localização antes de realizar o recebimento.")
    else:
        with st.form("form_recebimento"):
            sku = st.selectbox("Produto / SKU", produtos_disponiveis)
            quantidade = st.number_input("Quantidade recebida", min_value=1, step=1)
            lote = st.text_input("Lote")
            validade = st.date_input("Data de validade")
            localizacao = st.selectbox("Localização de destino", localizacoes_disponiveis)
            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Confirmar recebimento")

            if salvar:
                entrada = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "SKU": sku,
                    "Quantidade": quantidade,
                    "Lote": lote,
                    "Validade": validade.strftime("%d/%m/%Y"),
                    "Localização": localizacao,
                    "Status": "Disponível"
                }

                movimento = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Tipo": "Recebimento",
                    "SKU": sku,
                    "Quantidade": quantidade,
                    "Origem": "Fornecedor",
                    "Destino": localizacao,
                    "Observação": observacao
                }

                st.session_state.estoque.append(entrada)
                st.session_state.movimentacoes.append(movimento)

                st.success("Recebimento registrado com sucesso.")


# =========================
# CONSULTA DE ESTOQUE
# =========================

elif menu == "Consulta de Estoque":
    st.header("Consulta de Estoque")

    if st.session_state.estoque:
        df_estoque = pd.DataFrame(st.session_state.estoque)

        filtro_sku = st.text_input("Filtrar por SKU")
        filtro_local = st.text_input("Filtrar por localização")

        df_filtrado = df_estoque.copy()

        if filtro_sku:
            df_filtrado = df_filtrado[df_filtrado["SKU"].str.contains(filtro_sku, case=False, na=False)]

        if filtro_local:
            df_filtrado = df_filtrado[df_filtrado["Localização"].str.contains(filtro_local, case=False, na=False)]

        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Nenhum estoque registrado.")


# =========================
# MOVIMENTAÇÃO INTERNA
# =========================

elif menu == "Movimentação Interna":
    st.header("Movimentação Interna")

    if not st.session_state.estoque:
        st.warning("Não há estoque disponível para movimentação.")
    else:
        df_estoque = pd.DataFrame(st.session_state.estoque)
        st.dataframe(df_estoque, use_container_width=True)

        with st.form("form_movimentacao"):
            indice_item = st.number_input("Número da linha do item a movimentar", min_value=0, step=1)
            destino = st.text_input("Nova localização de destino")
            observacao = st.text_area("Observação da movimentação")

            salvar = st.form_submit_button("Confirmar movimentação")

            if salvar:
                if indice_item < len(st.session_state.estoque):
                    origem = st.session_state.estoque[indice_item]["Localização"]
                    sku = st.session_state.estoque[indice_item]["SKU"]
                    quantidade = st.session_state.estoque[indice_item]["Quantidade"]

                    st.session_state.estoque[indice_item]["Localização"] = destino

                    movimento = {
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Tipo": "Movimentação Interna",
                        "SKU": sku,
                        "Quantidade": quantidade,
                        "Origem": origem,
                        "Destino": destino,
                        "Observação": observacao
                    }

                    st.session_state.movimentacoes.append(movimento)

                    st.success("Movimentação realizada com sucesso.")
                else:
                    st.error("Linha informada não encontrada.")


# =========================
# PICKING
# =========================

elif menu == "Picking":
    st.header("Picking / Separação")

    st.info("Módulo inicial de picking. Nas próximas etapas vamos incluir pedidos, ondas de separação e validação por código de barras.")

    if st.session_state.estoque:
        df_estoque = pd.DataFrame(st.session_state.estoque)
        st.dataframe(df_estoque, use_container_width=True)
    else:
        st.warning("Não há estoque disponível para picking.")


# =========================
# EXPEDIÇÃO
# =========================

elif menu == "Expedição":
    st.header("Expedição")

    st.info("Módulo inicial de expedição. Nas próximas etapas vamos incluir conferência final, transportadora e baixa de estoque.")


# =========================
# INVENTÁRIO
# =========================

elif menu == "Inventário":
    st.header("Inventário")

    if st.session_state.estoque:
        df_estoque = pd.DataFrame(st.session_state.estoque)
        st.dataframe(df_estoque, use_container_width=True)

        st.info("Nas próximas etapas vamos incluir contagem física, comparação com estoque sistêmico e ajuste aprovado.")
    else:
        st.warning("Nenhum estoque disponível para inventário.")


# =========================
# RELATÓRIOS
# =========================

elif menu == "Relatórios":
    st.header("Relatórios")

    if st.session_state.movimentacoes:
        df_mov = pd.DataFrame(st.session_state.movimentacoes)
        st.subheader("Relatório de Movimentações")
        st.dataframe(df_mov, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada.")
