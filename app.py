import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(
    page_title="WMS Lite",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# CONFIGURAÇÃO INICIAL
# =========================================================

st.title("📦 WMS Lite")
st.caption("Sistema simplificado para controle de estoque, recebimento, movimentações, picking e inventário.")

# =========================================================
# BANCO TEMPORÁRIO EM MEMÓRIA
# Futuramente substituiremos por banco de dados real.
# =========================================================

if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(
        columns=[
            "SKU",
            "Descrição",
            "Unidade",
            "Categoria",
            "Código de Barras",
            "Estoque Mínimo",
            "Controla Lote",
            "Controla Validade",
            "Status"
        ]
    )

if "localizacoes" not in st.session_state:
    st.session_state.localizacoes = pd.DataFrame(
        columns=[
            "Código",
            "Tipo",
            "Rua",
            "Coluna",
            "Nível",
            "Posição",
            "Status"
        ]
    )

if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame(
        columns=[
            "SKU",
            "Produto",
            "Localização",
            "Lote",
            "Validade",
            "Quantidade",
            "Status Estoque"
        ]
    )

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(
        columns=[
            "Data/Hora",
            "Tipo",
            "SKU",
            "Produto",
            "Origem",
            "Destino",
            "Quantidade",
            "Usuário",
            "Observação"
        ]
    )

if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame(
        columns=[
            "Data",
            "SKU",
            "Produto",
            "Localização",
            "Qtd Sistema",
            "Qtd Física",
            "Diferença",
            "Responsável",
            "Status"
        ]
    )

# =========================================================
# MENU LATERAL
# =========================================================

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Cadastro de Produtos",
        "Cadastro de Localizações",
        "Recebimento",
        "Consulta de Estoque",
        "Movimentação Interna",
        "Inventário",
        "Histórico de Movimentações"
    ]
)

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":
    st.header("📊 Dashboard Geral")

    total_skus = st.session_state.produtos["SKU"].nunique()
    total_localizacoes = st.session_state.localizacoes["Código"].nunique()

    if len(st.session_state.estoque) > 0:
        total_estoque = st.session_state.estoque["Quantidade"].sum()
    else:
        total_estoque = 0

    total_movimentacoes = len(st.session_state.movimentacoes)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("SKUs Cadastrados", total_skus)
    col2.metric("Localizações", total_localizacoes)
    col3.metric("Saldo Total em Estoque", total_estoque)
    col4.metric("Movimentações", total_movimentacoes)

    st.divider()

    st.subheader("Estoque Atual")

    if len(st.session_state.estoque) == 0:
        st.info("Ainda não há estoque registrado.")
    else:
        st.dataframe(st.session_state.estoque, use_container_width=True)

# =========================================================
# CADASTRO DE PRODUTOS
# =========================================================

elif menu == "Cadastro de Produtos":
    st.header("🏷️ Cadastro de Produtos")

    with st.form("form_produto"):
        col1, col2 = st.columns(2)

        with col1:
            sku = st.text_input("SKU")
            descricao = st.text_input("Descrição do Produto")
            unidade = st.selectbox("Unidade", ["UN", "CX", "KG", "LT", "MT", "PC"])
            categoria = st.text_input("Categoria")

        with col2:
            codigo_barras = st.text_input("Código de Barras")
            estoque_minimo = st.number_input("Estoque Mínimo", min_value=0, step=1)
            controla_lote = st.selectbox("Controla Lote?", ["Sim", "Não"])
            controla_validade = st.selectbox("Controla Validade?", ["Sim", "Não"])
            status = st.selectbox("Status", ["Ativo", "Inativo"])

        salvar = st.form_submit_button("Salvar Produto")

        if salvar:
            if sku == "" or descricao == "":
                st.error("Informe pelo menos o SKU e a descrição do produto.")
            else:
                novo_produto = pd.DataFrame(
                    [{
                        "SKU": sku,
                        "Descrição": descricao,
                        "Unidade": unidade,
                        "Categoria": categoria,
                        "Código de Barras": codigo_barras,
                        "Estoque Mínimo": estoque_minimo,
                        "Controla Lote": controla_lote,
                        "Controla Validade": controla_validade,
                        "Status": status
                    }]
                )

                st.session_state.produtos = pd.concat(
                    [st.session_state.produtos, novo_produto],
                    ignore_index=True
                )

                st.success("Produto cadastrado com sucesso.")

    st.subheader("Produtos Cadastrados")
    st.dataframe(st.session_state.produtos, use_container_width=True)

# =========================================================
# CADASTRO DE LOCALIZAÇÕES
# =========================================================

elif menu == "Cadastro de Localizações":
    st.header("📍 Cadastro de Localizações")

    with st.form("form_localizacao"):
        col1, col2 = st.columns(2)

        with col1:
            codigo = st.text_input("Código da Localização")
            tipo = st.selectbox(
                "Tipo",
                [
                    "Recebimento",
                    "Estoque",
                    "Picking",
                    "Expedição",
                    "Quarentena",
                    "Buffer"
                ]
            )
            rua = st.text_input("Rua")

        with col2:
            coluna = st.text_input("Coluna")
            nivel = st.text_input("Nível")
            posicao = st.text_input("Posição")
            status_local = st.selectbox("Status", ["Ativa", "Bloqueada", "Inativa"])

        salvar_local = st.form_submit_button("Salvar Localização")

        if salvar_local:
            if codigo == "":
                st.error("Informe o código da localização.")
            else:
                nova_localizacao = pd.DataFrame(
                    [{
                        "Código": codigo,
                        "Tipo": tipo,
                        "Rua": rua,
                        "Coluna": coluna,
                        "Nível": nivel,
                        "Posição": posicao,
                        "Status": status_local
                    }]
                )

                st.session_state.localizacoes = pd.concat(
                    [st.session_state.localizacoes, nova_localizacao],
                    ignore_index=True
                )

                st.success("Localização cadastrada com sucesso.")

    st.subheader("Localizações Cadastradas")
    st.dataframe(st.session_state.localizacoes, use_container_width=True)

# =========================================================
# RECEBIMENTO
# =========================================================

elif menu == "Recebimento":
    st.header("📥 Recebimento de Materiais")

    if len(st.session_state.produtos) == 0:
        st.warning("Cadastre pelo menos um produto antes de realizar recebimentos.")
    elif len(st.session_state.localizacoes) == 0:
        st.warning("Cadastre pelo menos uma localização antes de realizar recebimentos.")
    else:
        with st.form("form_recebimento"):
            col1, col2 = st.columns(2)

            with col1:
                sku_receb = st.selectbox(
                    "SKU",
                    st.session_state.produtos["SKU"].tolist()
                )

                produto_nome = st.session_state.produtos.loc[
                    st.session_state.produtos["SKU"] == sku_receb,
                    "Descrição"
                ].values[0]

                st.text_input("Produto", value=produto_nome, disabled=True)

                quantidade = st.number_input(
                    "Quantidade Recebida",
                    min_value=1,
                    step=1
                )

                lote = st.text_input("Lote")

            with col2:
                validade = st.date_input("Validade", value=date.today())

                local_destino = st.selectbox(
                    "Localização de Destino",
                    st.session_state.localizacoes["Código"].tolist()
                )

                status_estoque = st.selectbox(
                    "Status do Estoque",
                    ["Disponível", "Bloqueado", "Quarentena"]
                )

                usuario = st.text_input("Usuário / Operador")

            observacao = st.text_area("Observação")

            receber = st.form_submit_button("Confirmar Recebimento")

            if receber:
                novo_estoque = pd.DataFrame(
                    [{
                        "SKU": sku_receb,
                        "Produto": produto_nome,
                        "Localização": local_destino,
                        "Lote": lote,
                        "Validade": validade,
                        "Quantidade": quantidade,
                        "Status Estoque": status_estoque
                    }]
                )

                nova_movimentacao = pd.DataFrame(
                    [{
                        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Tipo": "Recebimento",
                        "SKU": sku_receb,
                        "Produto": produto_nome,
                        "Origem": "Doca / Recebimento",
                        "Destino": local_destino,
                        "Quantidade": quantidade,
                        "Usuário": usuario,
                        "Observação": observacao
                    }]
                )

                st.session_state.estoque = pd.concat(
                    [st.session_state.estoque, novo_estoque],
                    ignore_index=True
                )

                st.session_state.movimentacoes = pd.concat(
                    [st.session_state.movimentacoes, nova_movimentacao],
                    ignore_index=True
                )

                st.success("Recebimento registrado com sucesso.")

# =========================================================
# CONSULTA DE ESTOQUE
# =========================================================

elif menu == "Consulta de Estoque":
    st.header("🔎 Consulta de Estoque")

    if len(st.session_state.estoque) == 0:
        st.info("Ainda não há saldo em estoque.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_sku = st.text_input("Filtrar por SKU")

        with col2:
            filtro_local = st.text_input("Filtrar por Localização")

        with col3:
            filtro_status = st.selectbox(
                "Filtrar por Status",
                ["Todos", "Disponível", "Bloqueado", "Quarentena"]
            )

        df = st.session_state.estoque.copy()

        if filtro_sku:
            df = df[df["SKU"].str.contains(filtro_sku, case=False, na=False)]

        if filtro_local:
            df = df[df["Localização"].str.contains(filtro_local, case=False, na=False)]

        if filtro_status != "Todos":
            df = df[df["Status Estoque"] == filtro_status]

        st.dataframe(df, use_container_width=True)

# =========================================================
# MOVIMENTAÇÃO INTERNA
# =========================================================

elif menu == "Movimentação Interna":
    st.header("🔄 Movimentação Interna")

    if len(st.session_state.estoque) == 0:
        st.warning("Não há estoque disponível para movimentar.")
    else:
        with st.form("form_movimentacao"):
            col1, col2 = st.columns(2)

            with col1:
                sku_mov = st.selectbox(
                    "SKU",
                    st.session_state.estoque["SKU"].unique().tolist()
                )

                produto_mov = st.session_state.estoque.loc[
                    st.session_state.estoque["SKU"] == sku_mov,
                    "Produto"
                ].values[0]

                origem = st.selectbox(
                    "Localização de Origem",
                    st.session_state.estoque.loc[
                        st.session_state.estoque["SKU"] == sku_mov,
                        "Localização"
                    ].unique().tolist()
                )

            with col2:
                destino = st.selectbox(
                    "Localização de Destino",
                    st.session_state.localizacoes["Código"].tolist()
                )

                qtd_mov = st.number_input(
                    "Quantidade",
                    min_value=1,
                    step=1
                )

                usuario_mov = st.text_input("Usuário / Operador")

            obs_mov = st.text_area("Observação")

            movimentar = st.form_submit_button("Confirmar Movimentação")

            if movimentar:
                filtro = (
                    (st.session_state.estoque["SKU"] == sku_mov) &
                    (st.session_state.estoque["Localização"] == origem)
                )

                saldo_origem = st.session_state.estoque.loc[filtro, "Quantidade"].sum()

                if qtd_mov > saldo_origem:
                    st.error("Quantidade maior que o saldo disponível na origem.")
                else:
                    idx_origem = st.session_state.estoque.loc[filtro].index[0]
                    st.session_state.estoque.at[idx_origem, "Quantidade"] -= qtd_mov

                    novo_destino = pd.DataFrame(
                        [{
                            "SKU": sku_mov,
                            "Produto": produto_mov,
                            "Localização": destino,
                            "Lote": "",
                            "Validade": "",
                            "Quantidade": qtd_mov,
                            "Status Estoque": "Disponível"
                        }]
                    )

                    nova_mov = pd.DataFrame(
                        [{
                            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "Tipo": "Movimentação Interna",
                            "SKU": sku_mov,
                            "Produto": produto_mov,
                            "Origem": origem,
                            "Destino": destino,
                            "Quantidade": qtd_mov,
                            "Usuário": usuario_mov,
                            "Observação": obs_mov
                        }]
                    )

                    st.session_state.estoque = pd.concat(
                        [st.session_state.estoque, novo_destino],
                        ignore_index=True
                    )

                    st.session_state.movimentacoes = pd.concat(
                        [st.session_state.movimentacoes, nova_mov],
                        ignore_index=True
                    )

                    st.success("Movimentação realizada com sucesso.")

# =========================================================
# INVENTÁRIO
# =========================================================

elif menu == "Inventário":
    st.header("🧮 Inventário")

    if len(st.session_state.estoque) == 0:
        st.warning("Não há estoque para inventariar.")
    else:
        with st.form("form_inventario"):
            col1, col2 = st.columns(2)

            with col1:
                sku_inv = st.selectbox(
                    "SKU",
                    st.session_state.estoque["SKU"].unique().tolist()
                )

                produto_inv = st.session_state.estoque.loc[
                    st.session_state.estoque["SKU"] == sku_inv,
                    "Produto"
                ].values[0]

                local_inv = st.selectbox(
                    "Localização",
                    st.session_state.estoque.loc[
                        st.session_state.estoque["SKU"] == sku_inv,
                        "Localização"
                    ].unique().tolist()
                )

            with col2:
                filtro_inv = (
                    (st.session_state.estoque["SKU"] == sku_inv) &
                    (st.session_state.estoque["Localização"] == local_inv)
                )

                qtd_sistema = int(st.session_state.estoque.loc[filtro_inv, "Quantidade"].sum())

                st.number_input(
                    "Quantidade no Sistema",
                    value=qtd_sistema,
                    disabled=True
                )

                qtd_fisica = st.number_input(
                    "Quantidade Física",
                    min_value=0,
                    step=1
                )

                responsavel = st.text_input("Responsável pela Contagem")

            registrar_inv = st.form_submit_button("Registrar Inventário")

            if registrar_inv:
                diferenca = qtd_fisica - qtd_sistema

                novo_inv = pd.DataFrame(
                    [{
                        "Data": datetime.now().strftime("%d/%m/%Y"),
                        "SKU": sku_inv,
                        "Produto": produto_inv,
                        "Localização": local_inv,
                        "Qtd Sistema": qtd_sistema,
                        "Qtd Física": qtd_fisica,
                        "Diferença": diferenca,
                        "Responsável": responsavel,
                        "Status": "Pendente de Análise" if diferenca != 0 else "Sem Divergência"
                    }]
                )

                st.session_state.inventario = pd.concat(
                    [st.session_state.inventario, novo_inv],
                    ignore_index=True
                )

                st.success("Inventário registrado com sucesso.")

        st.subheader("Histórico de Inventário")
        st.dataframe(st.session_state.inventario, use_container_width=True)

# =========================================================
# HISTÓRICO DE MOVIMENTAÇÕES
# =========================================================

elif menu == "Histórico de Movimentações":
    st.header("📜 Histórico de Movimentações")

    if len(st.session_state.movimentacoes) == 0:
        st.info("Ainda não há movimentações registradas.")
    else:
        st.dataframe(st.session_state.movimentacoes, use_container_width=True)
