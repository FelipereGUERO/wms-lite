import streamlit as st
import pandas as pd
from datetime import datetime, date

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="WMS Lite",
    page_icon="📦",
    layout="wide"
)

# =========================
# FUNÇÕES AUXILIARES
# =========================

def inicializar_dados():
    if "produtos" not in st.session_state:
        st.session_state.produtos = pd.DataFrame(columns=[
            "SKU",
            "Descrição",
            "Unidade",
            "Categoria",
            "Controla Lote",
            "Controla Validade",
            "Estoque Mínimo",
            "Status"
        ])

    if "localizacoes" not in st.session_state:
        st.session_state.localizacoes = pd.DataFrame(columns=[
            "Código",
            "Tipo",
            "Rua",
            "Coluna",
            "Nível",
            "Posição",
            "Status"
        ])

    if "estoque" not in st.session_state:
        st.session_state.estoque = pd.DataFrame(columns=[
            "SKU",
            "Descrição",
            "Localização",
            "Lote",
            "Validade",
            "Quantidade",
            "Status Estoque"
        ])

    if "movimentacoes" not in st.session_state:
        st.session_state.movimentacoes = pd.DataFrame(columns=[
            "Data/Hora",
            "Tipo",
            "SKU",
            "Descrição",
            "Origem",
            "Destino",
            "Quantidade",
            "Usuário",
            "Observação"
        ])

    if "pedidos" not in st.session_state:
        st.session_state.pedidos = pd.DataFrame(columns=[
            "Pedido",
            "Cliente / Destino",
            "SKU",
            "Descrição",
            "Quantidade",
            "Prioridade",
            "Status",
            "Data Criação",
            "Observação"
        ])


def registrar_movimentacao(tipo, sku, descricao, origem, destino, quantidade, usuario, observacao):
    nova_mov = {
        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Tipo": tipo,
        "SKU": sku,
        "Descrição": descricao,
        "Origem": origem,
        "Destino": destino,
        "Quantidade": quantidade,
        "Usuário": usuario,
        "Observação": observacao
    }

    st.session_state.movimentacoes = pd.concat(
        [st.session_state.movimentacoes, pd.DataFrame([nova_mov])],
        ignore_index=True
    )


def obter_descricao_produto(sku):
    produtos = st.session_state.produtos

    if produtos.empty:
        return ""

    resultado = produtos[produtos["SKU"] == sku]

    if resultado.empty:
        return ""

    return resultado.iloc[0]["Descrição"]


# =========================
# INICIALIZAÇÃO
# =========================

inicializar_dados()

# =========================
# CABEÇALHO
# =========================

st.title("📦 WMS Lite")
st.caption("Sistema simplificado para controle de estoque, movimentações, recebimento, picking e inventário.")

# =========================
# MENU LATERAL
# =========================

st.sidebar.title("Menu WMS Lite")

modulo = st.sidebar.radio(
    "Selecione o módulo:",
    [
        "Dashboard",
        "Cadastro de Produtos",
        "Cadastro de Localizações",
        "Recebimento",
        "Consulta de Estoque",
        "Movimentação Interna",
        "Ajustes de Estoque",
        "Pedidos / Ordens",        
        "Picking / Separação",
        "Expedição / Conferência",
        "Inventário",        
        "Histórico de Movimentações",
        "Exportar Dados"
    ]
)

st.sidebar.divider()
usuario_logado = st.sidebar.text_input("Usuário", value="operador")
st.sidebar.caption("Versão MVP 0.2")


# =========================
# DASHBOARD
# =========================

if modulo == "Dashboard":
    st.header("Dashboard Geral")

    total_skus = st.session_state.produtos["SKU"].nunique() if not st.session_state.produtos.empty else 0
    total_localizacoes = st.session_state.localizacoes["Código"].nunique() if not st.session_state.localizacoes.empty else 0
    total_estoque = st.session_state.estoque["Quantidade"].sum() if not st.session_state.estoque.empty else 0
    total_movimentacoes = len(st.session_state.movimentacoes)
    total_pedidos = len(st.session_state.pedidos)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("SKUs Cadastrados", total_skus)
    col2.metric("Localizações", total_localizacoes)
    col3.metric("Quantidade em Estoque", total_estoque)
    col4.metric("Movimentações", total_movimentacoes)
    col5.metric("Pedidos / Ordens", total_pedidos)

    st.divider()

    st.subheader("Resumo do Estoque")

    if st.session_state.estoque.empty:
        st.info("Ainda não existem itens em estoque.")
    else:
        estoque_resumo = st.session_state.estoque.groupby(
            ["SKU", "Descrição"], as_index=False
        )["Quantidade"].sum()

        st.dataframe(estoque_resumo, use_container_width=True)

    st.divider()

    st.subheader("Pedidos por Status")

    if st.session_state.pedidos.empty:
        st.info("Ainda não existem pedidos cadastrados.")
    else:
        pedidos_status = st.session_state.pedidos.groupby(
            ["Status"], as_index=False
        )["Pedido"].count()

        pedidos_status = pedidos_status.rename(columns={"Pedido": "Quantidade"})
        st.dataframe(pedidos_status, use_container_width=True)


# =========================
# CADASTRO DE PRODUTOS
# =========================

elif modulo == "Cadastro de Produtos":
    st.header("Cadastro de Produtos")

    with st.form("form_produto"):
        col1, col2 = st.columns(2)

        with col1:
            sku = st.text_input("SKU")
            descricao = st.text_input("Descrição")
            unidade = st.selectbox("Unidade", ["UN", "CX", "KG", "M", "L"])
            categoria = st.text_input("Categoria")

        with col2:
            controla_lote = st.selectbox("Controla Lote?", ["Sim", "Não"])
            controla_validade = st.selectbox("Controla Validade?", ["Sim", "Não"])
            estoque_minimo = st.number_input("Estoque Mínimo", min_value=0, step=1)
            status = st.selectbox("Status", ["Ativo", "Inativo"])

        salvar = st.form_submit_button("Salvar Produto")

        if salvar:
            if sku == "" or descricao == "":
                st.error("Preencha pelo menos SKU e Descrição.")
            else:
                novo_produto = {
                    "SKU": sku,
                    "Descrição": descricao,
                    "Unidade": unidade,
                    "Categoria": categoria,
                    "Controla Lote": controla_lote,
                    "Controla Validade": controla_validade,
                    "Estoque Mínimo": estoque_minimo,
                    "Status": status
                }

                st.session_state.produtos = pd.concat(
                    [st.session_state.produtos, pd.DataFrame([novo_produto])],
                    ignore_index=True
                )

                st.success("Produto cadastrado com sucesso.")

    st.subheader("Produtos Cadastrados")
    st.dataframe(st.session_state.produtos, use_container_width=True)


# =========================
# CADASTRO DE LOCALIZAÇÕES
# =========================

elif modulo == "Cadastro de Localizações":
    st.header("Cadastro de Localizações")

    with st.form("form_localizacao"):
        col1, col2 = st.columns(2)

        with col1:
            codigo = st.text_input("Código da Localização")
            tipo = st.selectbox("Tipo", [
                "Porta",
                "Recebimento",
                "Armazenagem",
                "Picking",
                "Quarentena",
                "Expedição",
                "Buffer"
            ])
            rua = st.text_input("Rua")

        with col2:
            coluna = st.text_input("Coluna")
            nivel = st.text_input("Nível")
            posicao = st.text_input("Posição")
            status_local = st.selectbox("Status", ["Ativa", "Inativa", "Bloqueada"])

        salvar_local = st.form_submit_button("Salvar Localização")

        if salvar_local:
            if codigo == "":
                st.error("Informe o código da localização.")
            else:
                nova_localizacao = {
                    "Código": codigo,
                    "Tipo": tipo,
                    "Rua": rua,
                    "Coluna": coluna,
                    "Nível": nivel,
                    "Posição": posicao,
                    "Status": status_local
                }

                st.session_state.localizacoes = pd.concat(
                    [st.session_state.localizacoes, pd.DataFrame([nova_localizacao])],
                    ignore_index=True
                )

                st.success("Localização cadastrada com sucesso.")

    st.subheader("Localizações Cadastradas")
    st.dataframe(st.session_state.localizacoes, use_container_width=True)


# =========================
# RECEBIMENTO
# =========================

elif modulo == "Recebimento":
    st.header("Recebimento de Materiais")

    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos antes de realizar recebimentos.")
    else:
        with st.form("form_recebimento"):
            sku_receb = st.selectbox("SKU", st.session_state.produtos["SKU"].tolist())
            descricao_receb = obter_descricao_produto(sku_receb)

            st.text_input("Descrição", value=descricao_receb, disabled=True)

            lote = st.text_input("Lote")
            validade = st.date_input("Validade", value=date.today())
            quantidade = st.number_input("Quantidade Recebida", min_value=1, step=1)

            localizacoes_disponiveis = st.session_state.localizacoes["Código"].tolist()

            if len(localizacoes_disponiveis) == 0:
                destino = st.text_input("Localização de Destino", value="RECEBIMENTO")
            else:
                destino = st.selectbox("Localização de Destino", localizacoes_disponiveis)

            status_estoque = st.selectbox("Status do Estoque", [
                "Disponível",
                "Quarentena",
                "Bloqueado"
            ])

            observacao = st.text_area("Observação")

            receber = st.form_submit_button("Confirmar Recebimento")

            if receber:
                novo_estoque = {
                    "SKU": sku_receb,
                    "Descrição": descricao_receb,
                    "Localização": destino,
                    "Lote": lote,
                    "Validade": validade.strftime("%d/%m/%Y"),
                    "Quantidade": quantidade,
                    "Status Estoque": status_estoque
                }

                st.session_state.estoque = pd.concat(
                    [st.session_state.estoque, pd.DataFrame([novo_estoque])],
                    ignore_index=True
                )

                registrar_movimentacao(
                    tipo="Recebimento",
                    sku=sku_receb,
                    descricao=descricao_receb,
                    origem="Fornecedor",
                    destino=destino,
                    quantidade=quantidade,
                    usuario=usuario_logado,
                    observacao=observacao
                )

                st.success("Recebimento registrado com sucesso.")


# =========================
# CONSULTA DE ESTOQUE
# =========================

elif modulo == "Consulta de Estoque":
    st.header("Consulta de Estoque")

    if st.session_state.estoque.empty:
        st.info("Ainda não existem registros de estoque.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_sku = st.text_input("Filtrar por SKU")

        with col2:
            filtro_local = st.text_input("Filtrar por Localização")

        with col3:
            filtro_status = st.selectbox("Filtrar por Status", [
                "Todos",
                "Disponível",
                "Quarentena",
                "Bloqueado"
            ])

        df = st.session_state.estoque.copy()

        if filtro_sku:
            df = df[df["SKU"].str.contains(filtro_sku, case=False, na=False)]

        if filtro_local:
            df = df[df["Localização"].str.contains(filtro_local, case=False, na=False)]

        if filtro_status != "Todos":
            df = df[df["Status Estoque"] == filtro_status]

        st.dataframe(df, use_container_width=True)

        st.subheader("Saldo por SKU")
        saldo_sku = df.groupby(["SKU", "Descrição"], as_index=False)["Quantidade"].sum()
        st.dataframe(saldo_sku, use_container_width=True)


# =========================
# MOVIMENTAÇÃO INTERNA
# =========================

elif modulo == "Movimentação Interna":
    st.header("Movimentação Interna")

    if st.session_state.estoque.empty:
        st.warning("Não há estoque disponível para movimentar.")
    else:
        with st.form("form_movimentacao"):
            sku_mov = st.selectbox("SKU para movimentar", st.session_state.estoque["SKU"].unique())
            descricao_mov = obter_descricao_produto(sku_mov)

            locais_origem = st.session_state.estoque[
                st.session_state.estoque["SKU"] == sku_mov
            ]["Localização"].unique()

            origem = st.selectbox("Localização de Origem", locais_origem)

            if st.session_state.localizacoes.empty:
                destino = st.text_input("Localização de Destino")
            else:
                destino = st.selectbox("Localização de Destino", st.session_state.localizacoes["Código"].tolist())

            quantidade_mov = st.number_input("Quantidade", min_value=1, step=1)
            observacao_mov = st.text_area("Observação")

            movimentar = st.form_submit_button("Confirmar Movimentação")

            if movimentar:
                saldo_origem = st.session_state.estoque[
                    (st.session_state.estoque["SKU"] == sku_mov) &
                    (st.session_state.estoque["Localização"] == origem)
                ]["Quantidade"].sum()

                if quantidade_mov > saldo_origem:
                    st.error("Quantidade maior que o saldo disponível na origem.")
                else:
                    indices = st.session_state.estoque[
                        (st.session_state.estoque["SKU"] == sku_mov) &
                        (st.session_state.estoque["Localização"] == origem)
                    ].index

                    qtd_restante = quantidade_mov

                    for idx in indices:
                        qtd_linha = st.session_state.estoque.at[idx, "Quantidade"]

                        if qtd_restante <= 0:
                            break

                        if qtd_linha <= qtd_restante:
                            qtd_restante -= qtd_linha
                            st.session_state.estoque.at[idx, "Quantidade"] = 0
                        else:
                            st.session_state.estoque.at[idx, "Quantidade"] = qtd_linha - qtd_restante
                            qtd_restante = 0

                    st.session_state.estoque = st.session_state.estoque[
                        st.session_state.estoque["Quantidade"] > 0
                    ]

                    novo_estoque_destino = {
                        "SKU": sku_mov,
                        "Descrição": descricao_mov,
                        "Localização": destino,
                        "Lote": "",
                        "Validade": "",
                        "Quantidade": quantidade_mov,
                        "Status Estoque": "Disponível"
                    }

                    st.session_state.estoque = pd.concat(
                        [st.session_state.estoque, pd.DataFrame([novo_estoque_destino])],
                        ignore_index=True
                    )

                    registrar_movimentacao(
                        tipo="Movimentação Interna",
                        sku=sku_mov,
                        descricao=descricao_mov,
                        origem=origem,
                        destino=destino,
                        quantidade=quantidade_mov,
                        usuario=usuario_logado,
                        observacao=observacao_mov
                    )

                    st.success("Movimentação realizada com sucesso.")

# =========================
# AJUSTES DE ESTOQUE
# =========================

elif modulo == "Ajustes de Estoque":
    st.header("Ajustes de Estoque")

    st.write(
        "Nesta área você pode realizar ajustes controlados de estoque, com motivo obrigatório e registro no histórico."
    )

    if st.session_state.estoque.empty:
        st.warning("Não há estoque disponível para ajuste.")
    else:
        df_ajuste = st.session_state.estoque.copy()

        df_ajuste["Opção"] = (
            df_ajuste.index.astype(str)
            + " | SKU: "
            + df_ajuste["SKU"].astype(str)
            + " | Local: "
            + df_ajuste["Localização"].astype(str)
            + " | Lote: "
            + df_ajuste["Lote"].astype(str)
            + " | Qtd: "
            + df_ajuste["Quantidade"].astype(str)
            + " | Status: "
            + df_ajuste["Status Estoque"].astype(str)
        )

        opcao_ajuste = st.selectbox(
            "Selecione o item de estoque para ajuste",
            df_ajuste["Opção"].tolist()
        )

        indice_estoque = int(opcao_ajuste.split(" | ")[0])

        item_estoque = st.session_state.estoque.loc[indice_estoque]

        sku_ajuste = item_estoque["SKU"]
        descricao_ajuste = item_estoque["Descrição"]
        local_ajuste = item_estoque["Localização"]
        lote_ajuste = item_estoque["Lote"]
        validade_ajuste = item_estoque["Validade"]
        quantidade_atual = int(item_estoque["Quantidade"])
        status_atual_estoque = item_estoque["Status Estoque"]

        st.divider()

        st.subheader("Dados do Item Selecionado")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input("SKU", value=sku_ajuste, disabled=True)
            st.text_input("Descrição", value=descricao_ajuste, disabled=True)

        with col2:
            st.text_input("Localização", value=local_ajuste, disabled=True)
            st.text_input("Lote", value=lote_ajuste, disabled=True)

        with col3:
            st.text_input("Validade", value=validade_ajuste, disabled=True)
            st.text_input("Quantidade Atual", value=str(quantidade_atual), disabled=True)

        st.divider()

        st.subheader("Registrar Ajuste")

        with st.form("form_ajuste_estoque"):
            col1, col2 = st.columns(2)

            with col1:
                tipo_ajuste = st.selectbox(
                    "Tipo de Ajuste",
                    [
                        "Entrada por Ajuste",
                        "Saída por Ajuste",
                        "Perda",
                        "Avaria",
                        "Erro Operacional",
                        "Amostra",
                        "Scrap",
                        "Reclassificação",
                        "Correção Autorizada"
                    ]
                )

                operacao_ajuste = st.selectbox(
                    "Operação",
                    [
                        "Somar quantidade ao saldo atual",
                        "Subtrair quantidade do saldo atual",
                        "Definir novo saldo final"
                    ]
                )

                quantidade_ajuste = st.number_input(
                    "Quantidade do Ajuste",
                    min_value=0,
                    step=1
                )

            with col2:
                novo_status_estoque = st.selectbox(
                    "Status do Estoque após Ajuste",
                    [
                        status_atual_estoque,
                        "Disponível",
                        "Quarentena",
                        "Bloqueado"
                    ]
                )

                aprovado_por = st.text_input("Aprovado por")

                motivo_ajuste = st.text_area("Motivo do Ajuste")

            confirmar_ajuste = st.form_submit_button("Confirmar Ajuste de Estoque")

            if confirmar_ajuste:
                if quantidade_ajuste <= 0 and operacao_ajuste != "Definir novo saldo final":
                    st.error("Informe uma quantidade maior que zero para o ajuste.")

                elif motivo_ajuste.strip() == "":
                    st.error("O motivo do ajuste é obrigatório.")

                elif aprovado_por.strip() == "":
                    st.error("Informe quem aprovou o ajuste.")

                else:
                    if operacao_ajuste == "Somar quantidade ao saldo atual":
                        nova_quantidade = quantidade_atual + quantidade_ajuste
                        diferenca = quantidade_ajuste

                    elif operacao_ajuste == "Subtrair quantidade do saldo atual":
                        if quantidade_ajuste > quantidade_atual:
                            st.error("A quantidade a subtrair não pode ser maior que o saldo atual.")
                            st.stop()

                        nova_quantidade = quantidade_atual - quantidade_ajuste
                        diferenca = quantidade_ajuste * -1

                    else:
                        nova_quantidade = quantidade_ajuste
                        diferenca = nova_quantidade - quantidade_atual

                    if nova_quantidade <= 0:
                        st.session_state.estoque = st.session_state.estoque.drop(index=indice_estoque)
                        st.session_state.estoque = st.session_state.estoque.reset_index(drop=True)
                    else:
                        st.session_state.estoque.at[indice_estoque, "Quantidade"] = nova_quantidade
                        st.session_state.estoque.at[indice_estoque, "Status Estoque"] = novo_status_estoque

                    registrar_movimentacao(
                        tipo=f"Ajuste de Estoque - {tipo_ajuste}",
                        sku=sku_ajuste,
                        descricao=descricao_ajuste,
                        origem=local_ajuste,
                        destino=local_ajuste,
                        quantidade=diferenca,
                        usuario=usuario_logado,
                        observacao=(
                            f"Operação: {operacao_ajuste}. "
                            f"Saldo anterior: {quantidade_atual}. "
                            f"Novo saldo: {nova_quantidade}. "
                            f"Status anterior: {status_atual_estoque}. "
                            f"Novo status: {novo_status_estoque}. "
                            f"Aprovado por: {aprovado_por}. "
                            f"Motivo: {motivo_ajuste}"
                        )
                    )

                    st.success("Ajuste de estoque registrado com sucesso.")
                    st.info(f"Saldo anterior: {quantidade_atual} | Novo saldo: {nova_quantidade}")

# =========================
# PEDIDOS / ORDENS
# =========================

elif modulo == "Pedidos / Ordens":
    st.header("Pedidos / Ordens")

    st.write(
        "Nesta área você pode criar pedidos, ordens de separação, requisições internas ou demandas para expedição."
    )

    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos antes de criar pedidos.")
    else:
        with st.form("form_pedido"):
            col1, col2 = st.columns(2)

            with col1:
                numero_pedido = st.text_input("Número do Pedido / Ordem")
                cliente_destino = st.text_input("Cliente / Destino")
                sku_pedido = st.selectbox("SKU", st.session_state.produtos["SKU"].tolist())
                descricao_pedido = obter_descricao_produto(sku_pedido)
                st.text_input("Descrição", value=descricao_pedido, disabled=True)

            with col2:
                quantidade_pedido = st.number_input("Quantidade", min_value=1, step=1)
                prioridade = st.selectbox("Prioridade", ["Normal", "Alta", "Urgente"])
                status_pedido = st.selectbox("Status", [
                    "Criado",
                    "Aguardando Picking",
                    "Em Picking",
                    "Separado",
                    "Conferido",
                    "Expedido",
                    "Cancelado"
                ])
                observacao_pedido = st.text_area("Observação")

            salvar_pedido = st.form_submit_button("Salvar Pedido / Ordem")

            if salvar_pedido:
                if numero_pedido == "":
                    st.error("Informe o número do pedido ou ordem.")
                else:
                    novo_pedido = {
                        "Pedido": numero_pedido,
                        "Cliente / Destino": cliente_destino,
                        "SKU": sku_pedido,
                        "Descrição": descricao_pedido,
                        "Quantidade": quantidade_pedido,
                        "Prioridade": prioridade,
                        "Status": status_pedido,
                        "Data Criação": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Observação": observacao_pedido
                    }

                    st.session_state.pedidos = pd.concat(
                        [st.session_state.pedidos, pd.DataFrame([novo_pedido])],
                        ignore_index=True
                    )

                    st.success("Pedido / Ordem cadastrado com sucesso.")

    st.divider()

    st.subheader("Pedidos / Ordens Cadastrados")

    if st.session_state.pedidos.empty:
        st.info("Ainda não existem pedidos ou ordens cadastrados.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_pedido = st.text_input("Filtrar por Pedido")

        with col2:
            filtro_sku_pedido = st.text_input("Filtrar por SKU")

        with col3:
            filtro_status_pedido = st.selectbox("Filtrar por Status", [
                "Todos",
                "Criado",
                "Aguardando Picking",
                "Em Picking",
                "Separado",
                "Conferido",
                "Expedido",
                "Cancelado"
            ])

        df_pedidos = st.session_state.pedidos.copy()

        if filtro_pedido:
            df_pedidos = df_pedidos[
                df_pedidos["Pedido"].str.contains(filtro_pedido, case=False, na=False)
            ]

        if filtro_sku_pedido:
            df_pedidos = df_pedidos[
                df_pedidos["SKU"].str.contains(filtro_sku_pedido, case=False, na=False)
            ]

        if filtro_status_pedido != "Todos":
            df_pedidos = df_pedidos[df_pedidos["Status"] == filtro_status_pedido]

        st.dataframe(df_pedidos, use_container_width=True)


# =========================
# PICKING / SEPARAÇÃO
# =========================

elif modulo == "Picking / Separação":
    st.header("Picking / Separação")

    st.write(
        "Nesta área você pode separar pedidos cadastrados, validar saldo disponível e baixar o estoque."
    )

    if st.session_state.estoque.empty:
        st.warning("Não há estoque disponível para separação.")

    elif st.session_state.pedidos.empty:
        st.warning("Não existem pedidos cadastrados para separação.")
        st.info("Cadastre primeiro um pedido no módulo 'Pedidos / Ordens'.")

    else:
        pedidos_disponiveis = st.session_state.pedidos[
            st.session_state.pedidos["Status"].isin([
                "Criado",
                "Aguardando Picking",
                "Em Picking"
            ])
        ].copy()

        if pedidos_disponiveis.empty:
            st.info("Não existem pedidos pendentes para picking.")
        else:
            pedidos_disponiveis["Opção"] = (
                pedidos_disponiveis["Pedido"].astype(str)
                + " | SKU: "
                + pedidos_disponiveis["SKU"].astype(str)
                + " | Qtd: "
                + pedidos_disponiveis["Quantidade"].astype(str)
                + " | Status: "
                + pedidos_disponiveis["Status"].astype(str)
            )

            opcao_pedido = st.selectbox(
                "Selecione o Pedido / Ordem para Separação",
                pedidos_disponiveis["Opção"].tolist()
            )

            indice_pedido = pedidos_disponiveis[
                pedidos_disponiveis["Opção"] == opcao_pedido
            ].index[0]

            pedido_selecionado = st.session_state.pedidos.loc[indice_pedido]

            numero_pedido = pedido_selecionado["Pedido"]
            cliente_destino = pedido_selecionado["Cliente / Destino"]
            sku_pick = pedido_selecionado["SKU"]
            descricao_pick = pedido_selecionado["Descrição"]
            quantidade_pick = int(pedido_selecionado["Quantidade"])
            prioridade_pick = pedido_selecionado["Prioridade"]
            status_atual = pedido_selecionado["Status"]

            st.divider()

            st.subheader("Dados do Pedido Selecionado")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.text_input("Pedido", value=numero_pedido, disabled=True)
                st.text_input("Cliente / Destino", value=cliente_destino, disabled=True)

            with col2:
                st.text_input("SKU", value=sku_pick, disabled=True)
                st.text_input("Descrição", value=descricao_pick, disabled=True)

            with col3:
                st.text_input("Quantidade a Separar", value=str(quantidade_pick), disabled=True)
                st.text_input("Prioridade", value=prioridade_pick, disabled=True)

            saldo_disponivel = st.session_state.estoque[
                (st.session_state.estoque["SKU"] == sku_pick) &
                (st.session_state.estoque["Status Estoque"] == "Disponível")
            ]["Quantidade"].sum()

            st.info(f"Saldo disponível para o SKU {sku_pick}: {saldo_disponivel}")

            if saldo_disponivel < quantidade_pick:
                st.error("Saldo insuficiente para atender este pedido.")
            else:
                with st.form("form_picking_integrado"):
                    observacao_pick = st.text_area("Observação da Separação")

                    confirmar_picking = st.form_submit_button("Confirmar Separação do Pedido")

                    if confirmar_picking:
                        indices = st.session_state.estoque[
                            (st.session_state.estoque["SKU"] == sku_pick) &
                            (st.session_state.estoque["Status Estoque"] == "Disponível")
                        ].index

                        qtd_restante = quantidade_pick
                        origem_utilizada = ""

                        for idx in indices:
                            qtd_linha = st.session_state.estoque.at[idx, "Quantidade"]
                            local_linha = st.session_state.estoque.at[idx, "Localização"]

                            if origem_utilizada == "":
                                origem_utilizada = local_linha

                            if qtd_restante <= 0:
                                break

                            if qtd_linha <= qtd_restante:
                                qtd_restante -= qtd_linha
                                st.session_state.estoque.at[idx, "Quantidade"] = 0
                            else:
                                st.session_state.estoque.at[idx, "Quantidade"] = qtd_linha - qtd_restante
                                qtd_restante = 0

                        st.session_state.estoque = st.session_state.estoque[
                            st.session_state.estoque["Quantidade"] > 0
                        ]

                        st.session_state.pedidos.at[indice_pedido, "Status"] = "Separado"

                        registrar_movimentacao(
                            tipo="Picking",
                            sku=sku_pick,
                            descricao=descricao_pick,
                            origem=origem_utilizada,
                            destino=f"Pedido {numero_pedido}",
                            quantidade=quantidade_pick,
                            usuario=usuario_logado,
                            observacao=observacao_pick
                        )

                        st.success("Pedido separado com sucesso.")
                        st.info("O status do pedido foi atualizado para 'Separado'.")

# =========================
# EXPEDIÇÃO / CONFERÊNCIA
# =========================

elif modulo == "Expedição / Conferência":
    st.header("Expedição / Conferência")

    st.write(
        "Nesta área você pode conferir pedidos separados e finalizar a expedição."
    )

    if st.session_state.pedidos.empty:
        st.warning("Não existem pedidos cadastrados.")
    else:
        pedidos_para_expedicao = st.session_state.pedidos[
            st.session_state.pedidos["Status"].isin([
                "Separado",
                "Conferido"
            ])
        ].copy()

        if pedidos_para_expedicao.empty:
            st.info("Não existem pedidos separados ou conferidos aguardando expedição.")
        else:
            pedidos_para_expedicao["Opção"] = (
                pedidos_para_expedicao["Pedido"].astype(str)
                + " | SKU: "
                + pedidos_para_expedicao["SKU"].astype(str)
                + " | Qtd: "
                + pedidos_para_expedicao["Quantidade"].astype(str)
                + " | Status: "
                + pedidos_para_expedicao["Status"].astype(str)
            )

            opcao_expedicao = st.selectbox(
                "Selecione o Pedido para Conferência / Expedição",
                pedidos_para_expedicao["Opção"].tolist()
            )

            indice_pedido_exp = pedidos_para_expedicao[
                pedidos_para_expedicao["Opção"] == opcao_expedicao
            ].index[0]

            pedido_exp = st.session_state.pedidos.loc[indice_pedido_exp]

            numero_pedido_exp = pedido_exp["Pedido"]
            cliente_destino_exp = pedido_exp["Cliente / Destino"]
            sku_exp = pedido_exp["SKU"]
            descricao_exp = pedido_exp["Descrição"]
            quantidade_exp = int(pedido_exp["Quantidade"])
            prioridade_exp = pedido_exp["Prioridade"]
            status_exp = pedido_exp["Status"]

            st.divider()

            st.subheader("Dados do Pedido")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.text_input("Pedido", value=numero_pedido_exp, disabled=True)
                st.text_input("Cliente / Destino", value=cliente_destino_exp, disabled=True)

            with col2:
                st.text_input("SKU", value=sku_exp, disabled=True)
                st.text_input("Descrição", value=descricao_exp, disabled=True)

            with col3:
                st.text_input("Quantidade", value=str(quantidade_exp), disabled=True)
                st.text_input("Status Atual", value=status_exp, disabled=True)

            st.divider()

            st.subheader("Conferência e Dados de Expedição")

            with st.form("form_expedicao"):
                col1, col2 = st.columns(2)

                with col1:
                    resultado_conferencia = st.selectbox(
                        "Resultado da Conferência",
                        [
                            "Conforme",
                            "Divergente"
                        ]
                    )

                    transportadora = st.text_input("Transportadora")
                    documento_transporte = st.text_input("Documento / Nota / Referência")

                with col2:
                    quantidade_conferida = st.number_input(
                        "Quantidade Conferida",
                        min_value=0,
                        step=1,
                        value=quantidade_exp
                    )

                    volumes = st.number_input(
                        "Volumes",
                        min_value=0,
                        step=1,
                        value=1
                    )

                    peso_total = st.number_input(
                        "Peso Total",
                        min_value=0.0,
                        step=0.1,
                        value=0.0
                    )

                observacao_exp = st.text_area("Observação da Conferência / Expedição")

                if status_exp == "Separado":
                    acao = st.selectbox(
                        "Ação",
                        [
                            "Conferir e Expedir",
                            "Somente Conferir",
                            "Registrar Divergência"
                        ]
                    )
                else:
                    acao = st.selectbox(
                        "Ação",
                        [
                            "Expedir Pedido",
                            "Registrar Divergência"
                        ]
                    )

                confirmar_expedicao = st.form_submit_button("Confirmar Ação")

                if confirmar_expedicao:
                    if resultado_conferencia == "Divergente" or quantidade_conferida != quantidade_exp:
                        st.session_state.pedidos.at[indice_pedido_exp, "Status"] = "Em Picking"

                        registrar_movimentacao(
                            tipo="Divergência na Expedição",
                            sku=sku_exp,
                            descricao=descricao_exp,
                            origem=f"Pedido {numero_pedido_exp}",
                            destino="Retorno para análise / picking",
                            quantidade=quantidade_conferida,
                            usuario=usuario_logado,
                            observacao=(
                                f"Divergência registrada. "
                                f"Qtd pedido: {quantidade_exp}. "
                                f"Qtd conferida: {quantidade_conferida}. "
                                f"Obs: {observacao_exp}"
                            )
                        )

                        st.error("Divergência registrada. O pedido voltou para status 'Em Picking'.")

                    elif acao == "Somente Conferir":
                        st.session_state.pedidos.at[indice_pedido_exp, "Status"] = "Conferido"

                        registrar_movimentacao(
                            tipo="Conferência",
                            sku=sku_exp,
                            descricao=descricao_exp,
                            origem=f"Pedido {numero_pedido_exp}",
                            destino="Área de Expedição",
                            quantidade=quantidade_exp,
                            usuario=usuario_logado,
                            observacao=(
                                f"Pedido conferido. "
                                f"Transportadora: {transportadora}. "
                                f"Documento: {documento_transporte}. "
                                f"Volumes: {volumes}. "
                                f"Peso: {peso_total}. "
                                f"Obs: {observacao_exp}"
                            )
                        )

                        st.success("Pedido conferido com sucesso. Status atualizado para 'Conferido'.")

                    elif acao in ["Conferir e Expedir", "Expedir Pedido"]:
                        st.session_state.pedidos.at[indice_pedido_exp, "Status"] = "Expedido"

                        registrar_movimentacao(
                            tipo="Expedição",
                            sku=sku_exp,
                            descricao=descricao_exp,
                            origem=f"Pedido {numero_pedido_exp}",
                            destino=cliente_destino_exp,
                            quantidade=quantidade_exp,
                            usuario=usuario_logado,
                            observacao=(
                                f"Pedido expedido. "
                                f"Transportadora: {transportadora}. "
                                f"Documento: {documento_transporte}. "
                                f"Volumes: {volumes}. "
                                f"Peso: {peso_total}. "
                                f"Obs: {observacao_exp}"
                            )
                        )

                        st.success("Pedido expedido com sucesso. Status atualizado para 'Expedido'.")

                    else:
                        st.warning("Nenhuma ação executada.")


# =========================
# INVENTÁRIO
# =========================

elif modulo == "Inventário":
    st.header("Inventário")

    if st.session_state.estoque.empty:
        st.warning("Não há estoque para inventariar.")
    else:
        st.subheader("Base Atual de Estoque")
        st.dataframe(st.session_state.estoque, use_container_width=True)

        st.divider()
        st.subheader("Registrar Contagem")

        with st.form("form_inventario"):
            sku_inv = st.selectbox("SKU", st.session_state.estoque["SKU"].unique())

            locais_sku = st.session_state.estoque[
                st.session_state.estoque["SKU"] == sku_inv
            ]["Localização"].unique()

            local_inv = st.selectbox("Localização", locais_sku)

            saldo_sistema = st.session_state.estoque[
                (st.session_state.estoque["SKU"] == sku_inv) &
                (st.session_state.estoque["Localização"] == local_inv)
            ]["Quantidade"].sum()

            st.info(f"Saldo no sistema: {saldo_sistema}")

            quantidade_fisica = st.number_input("Quantidade Física Contada", min_value=0, step=1)
            motivo = st.text_area("Motivo / Observação")

            ajustar = st.form_submit_button("Registrar Ajuste de Inventário")

            if ajustar:
                diferenca = quantidade_fisica - saldo_sistema

                st.session_state.estoque = st.session_state.estoque[
                    ~(
                        (st.session_state.estoque["SKU"] == sku_inv) &
                        (st.session_state.estoque["Localização"] == local_inv)
                    )
                ]

                descricao_inv = obter_descricao_produto(sku_inv)

                if quantidade_fisica > 0:
                    novo_saldo = {
                        "SKU": sku_inv,
                        "Descrição": descricao_inv,
                        "Localização": local_inv,
                        "Lote": "",
                        "Validade": "",
                        "Quantidade": quantidade_fisica,
                        "Status Estoque": "Disponível"
                    }

                    st.session_state.estoque = pd.concat(
                        [st.session_state.estoque, pd.DataFrame([novo_saldo])],
                        ignore_index=True
                    )

                registrar_movimentacao(
                    tipo="Inventário",
                    sku=sku_inv,
                    descricao=descricao_inv,
                    origem=local_inv,
                    destino=local_inv,
                    quantidade=diferenca,
                    usuario=usuario_logado,
                    observacao=motivo
                )

                st.success("Inventário registrado com sucesso.")


# =========================
# HISTÓRICO DE MOVIMENTAÇÕES
# =========================

elif modulo == "Histórico de Movimentações":
    st.header("Histórico de Movimentações")

    if st.session_state.movimentacoes.empty:
        st.info("Ainda não existem movimentações registradas.")
    else:
        st.dataframe(st.session_state.movimentacoes, use_container_width=True)


# =========================
# EXPORTAR DADOS
# =========================

elif modulo == "Exportar Dados":
    st.header("Exportar Dados")

    st.write("Nesta área você pode baixar as bases atuais em CSV.")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Baixar Produtos",
            data=st.session_state.produtos.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="produtos.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Baixar Localizações",
            data=st.session_state.localizacoes.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="localizacoes.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Baixar Pedidos / Ordens",
            data=st.session_state.pedidos.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="pedidos.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="Baixar Estoque",
            data=st.session_state.estoque.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="estoque.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Baixar Movimentações",
            data=st.session_state.movimentacoes.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="movimentacoes.csv",
            mime="text/csv"
        )
