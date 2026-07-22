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
        
    if "devolucoes" not in st.session_state:
        st.session_state.devolucoes = pd.DataFrame(columns=[
            "Data/Hora",
            "Tipo Devolução",
            "Documento / Referência",
            "Origem",
            "Destino",
            "SKU",
            "Descrição",
            "Lote",
            "Validade",
            "Quantidade",
            "Tratativa",
            "Status Estoque",
            "Usuário",
            "Motivo",
            "Observação"
        ])

    if "conferencias_entrada" not in st.session_state:
        st.session_state.conferencias_entrada = pd.DataFrame(columns=[
            "Data/Hora",
            "Documento / Referência",
            "Fornecedor",
            "SKU",
            "Descrição",
            "Lote",
            "Validade",
            "Quantidade Esperada",
            "Quantidade Recebida",
            "Diferença",
            "Resultado",
            "Tratativa",
            "Localização Destino",
            "Status Estoque",
            "Usuário",
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

def valor_ja_cadastrado(df, coluna, valor):
    if df.empty:
        return False

    if valor is None:
        return False

    return df[coluna].astype(str).str.strip().str.upper().eq(
        str(valor).strip().upper()
    ).any()


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
        "Conferência de Entrada",
        "Consulta de Estoque",        
       "Movimentação Interna",
        "Ajustes de Estoque",
        "Bloqueio / Desbloqueio",
        "Gestão de Lotes e Validades",
        "Rastreabilidade",
        "Pedidos / Ordens",
        "Gestão de Status de Pedidos",
        "Picking / Separação",        
        "Expedição / Conferência",
        "Devoluções",
        "Inventário",        
        "Histórico de Movimentações",
        "Relatórios / Exportar Dados"
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

    st.write(
        "Visão geral dos principais indicadores operacionais do WMS Lite."
    )

    # =========================
    # INDICADORES PRINCIPAIS
    # =========================

    total_skus = st.session_state.produtos["SKU"].nunique() if not st.session_state.produtos.empty else 0
    total_localizacoes = st.session_state.localizacoes["Código"].nunique() if not st.session_state.localizacoes.empty else 0
    total_estoque = st.session_state.estoque["Quantidade"].sum() if not st.session_state.estoque.empty else 0
    total_movimentacoes = len(st.session_state.movimentacoes)
    total_pedidos = len(st.session_state.pedidos)

    if st.session_state.pedidos.empty:
        pedidos_pendentes = 0
        pedidos_expedidos = 0
    else:
        pedidos_pendentes = len(
            st.session_state.pedidos[
                st.session_state.pedidos["Status"].isin([
                    "Criado",
                    "Aguardando Picking",
                    "Em Picking",
                    "Separado",
                    "Conferido"
                ])
            ]
        )

        pedidos_expedidos = len(
            st.session_state.pedidos[
                st.session_state.pedidos["Status"] == "Expedido"
            ]
        )

    if st.session_state.estoque.empty:
        itens_bloqueados = 0
        itens_quarentena = 0
    else:
        itens_bloqueados = st.session_state.estoque[
            st.session_state.estoque["Status Estoque"] == "Bloqueado"
        ]["Quantidade"].sum()

        itens_quarentena = st.session_state.estoque[
            st.session_state.estoque["Status Estoque"] == "Quarentena"
        ]["Quantidade"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("SKUs Cadastrados", total_skus)
    col2.metric("Localizações", total_localizacoes)
    col3.metric("Qtd. Total em Estoque", total_estoque)
    col4.metric("Movimentações", total_movimentacoes)

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Pedidos / Ordens", total_pedidos)
    col6.metric("Pedidos Pendentes", pedidos_pendentes)
    col7.metric("Pedidos Expedidos", pedidos_expedidos)
    col8.metric("Itens Bloqueados", itens_bloqueados)

    col9, col10, col11, col12 = st.columns(4)

    col9.metric("Itens em Quarentena", itens_quarentena)

    # =========================
    # VALIDADES
    # =========================

    itens_vencidos = 0
    itens_vencendo_30 = 0

    if not st.session_state.estoque.empty:
        df_validade_dash = st.session_state.estoque.copy()

        df_validade_dash["Data Validade"] = pd.to_datetime(
            df_validade_dash["Validade"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        hoje = pd.Timestamp(date.today())

        df_validade_dash["Dias para Vencer"] = (
            df_validade_dash["Data Validade"] - hoje
        ).dt.days

        itens_vencidos = len(
            df_validade_dash[
                df_validade_dash["Dias para Vencer"] < 0
            ]
        )

        itens_vencendo_30 = len(
            df_validade_dash[
                (df_validade_dash["Dias para Vencer"] >= 0) &
                (df_validade_dash["Dias para Vencer"] <= 30)
            ]
        )

    col10.metric("Itens Vencidos", itens_vencidos)
    col11.metric("Vencem em até 30 dias", itens_vencendo_30)

    # =========================
    # ESTOQUE ABAIXO DO MÍNIMO
    # =========================

    produtos_abaixo_minimo = pd.DataFrame()

    if not st.session_state.produtos.empty and not st.session_state.estoque.empty:
        saldo_por_sku = st.session_state.estoque.groupby(
            ["SKU"],
            as_index=False
        )["Quantidade"].sum()

        produtos_minimo = st.session_state.produtos.copy()

        produtos_abaixo_minimo = pd.merge(
            produtos_minimo,
            saldo_por_sku,
            on="SKU",
            how="left"
        )

        produtos_abaixo_minimo["Quantidade"] = produtos_abaixo_minimo["Quantidade"].fillna(0)

        produtos_abaixo_minimo = produtos_abaixo_minimo[
            produtos_abaixo_minimo["Quantidade"] < produtos_abaixo_minimo["Estoque Mínimo"]
        ]

    col12.metric("SKUs Abaixo do Mínimo", len(produtos_abaixo_minimo))

    st.divider()

    # =========================
    # RESUMO DO ESTOQUE
    # =========================

    st.subheader("Resumo do Estoque por SKU")

    if st.session_state.estoque.empty:
        st.info("Ainda não existem itens em estoque.")
    else:
        estoque_resumo = st.session_state.estoque.groupby(
            ["SKU", "Descrição", "Status Estoque"],
            as_index=False
        )["Quantidade"].sum()

        st.dataframe(
            estoque_resumo,
            use_container_width=True
        )

    st.divider()

    # =========================
    # PRODUTOS ABAIXO DO MÍNIMO
    # =========================

    st.subheader("Produtos Abaixo do Estoque Mínimo")

    if produtos_abaixo_minimo.empty:
        st.success("Não há produtos abaixo do estoque mínimo.")
    else:
        colunas_minimo = [
            "SKU",
            "Descrição",
            "Categoria",
            "Estoque Mínimo",
            "Quantidade",
            "Status"
        ]

        st.warning("Existem produtos com saldo abaixo do estoque mínimo.")

        st.dataframe(
            produtos_abaixo_minimo[colunas_minimo],
            use_container_width=True
        )

    st.divider()

    # =========================
    # PEDIDOS POR STATUS
    # =========================

    st.subheader("Pedidos / Ordens por Status")

    if st.session_state.pedidos.empty:
        st.info("Ainda não existem pedidos cadastrados.")
    else:
        pedidos_status = st.session_state.pedidos.groupby(
            ["Status"],
            as_index=False
        )["Pedido"].count()

        pedidos_status = pedidos_status.rename(
            columns={"Pedido": "Quantidade"}
        )

        st.dataframe(
            pedidos_status,
            use_container_width=True
        )

    st.divider()

    # =========================
    # MOVIMENTAÇÕES POR TIPO
    # =========================

    st.subheader("Movimentações por Tipo")

    if st.session_state.movimentacoes.empty:
        st.info("Ainda não existem movimentações registradas.")
    else:
        movimentacoes_tipo = st.session_state.movimentacoes.groupby(
            ["Tipo"],
            as_index=False
        )["Quantidade"].sum()

        st.dataframe(
            movimentacoes_tipo,
            use_container_width=True
        )

    st.divider()

    # =========================
    # ALERTAS OPERACIONAIS
    # =========================

    st.subheader("Alertas Operacionais")

    alertas = []

    if itens_bloqueados > 0:
        alertas.append(f"Existem {itens_bloqueados} unidades bloqueadas.")

    if itens_quarentena > 0:
        alertas.append(f"Existem {itens_quarentena} unidades em quarentena.")

    if itens_vencidos > 0:
        alertas.append(f"Existem {itens_vencidos} registros de estoque vencidos.")

    if itens_vencendo_30 > 0:
        alertas.append(f"Existem {itens_vencendo_30} registros vencendo em até 30 dias.")

    if len(produtos_abaixo_minimo) > 0:
        alertas.append(f"Existem {len(produtos_abaixo_minimo)} SKUs abaixo do estoque mínimo.")

    if pedidos_pendentes > 0:
        alertas.append(f"Existem {pedidos_pendentes} pedidos pendentes no fluxo operacional.")

    if len(alertas) == 0:
        st.success("Não há alertas operacionais críticos no momento.")
    else:
        for alerta in alertas:
            st.warning(alerta)

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
            sku_limpo = sku.strip()
            descricao_limpa = descricao.strip()

            if sku_limpo == "" or descricao_limpa == "":
                st.error("Preencha pelo menos SKU e Descrição.")
            elif valor_ja_cadastrado(st.session_state.produtos, "SKU", sku_limpo):
                st.error("Este SKU já está cadastrado. Verifique antes de criar um novo produto.")
            else:
                novo_produto = {
                    "SKU": sku_limpo,
                    "Descrição": descricao_limpa,
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
            codigo_limpo = codigo.strip()

            if codigo_limpo == "":
                st.error("Informe o código da localização.")
            elif valor_ja_cadastrado(st.session_state.localizacoes, "Código", codigo_limpo):
                st.error("Esta localização já está cadastrada. Verifique antes de criar uma nova localização.")
            else:
                nova_localizacao = {
                    "Código": codigo_limpo,
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
# CONFERÊNCIA DE ENTRADA
# =========================

elif modulo == "Conferência de Entrada":
    st.header("Conferência de Entrada")

    st.write(
        "Nesta área você pode conferir materiais recebidos antes de liberar para estoque, quarentena, bloqueio ou devolução."
    )

    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos antes de realizar conferência de entrada.")
    else:
        with st.form("form_conferencia_entrada"):
            col1, col2 = st.columns(2)

            with col1:
                documento_conf = st.text_input("Documento / NF / Pedido / Referência")
                fornecedor_conf = st.text_input("Fornecedor")
                sku_conf = st.selectbox("SKU", st.session_state.produtos["SKU"].tolist())
                descricao_conf = obter_descricao_produto(sku_conf)
                st.text_input("Descrição", value=descricao_conf, disabled=True)

                lote_conf = st.text_input("Lote")
                validade_conf = st.date_input("Validade", value=date.today())

            with col2:
                quantidade_esperada = st.number_input(
                    "Quantidade Esperada",
                    min_value=0,
                    step=1
                )

                quantidade_recebida = st.number_input(
                    "Quantidade Recebida",
                    min_value=0,
                    step=1
                )

                if st.session_state.localizacoes.empty:
                    destino_conf = st.text_input("Localização de Destino", value="RECEBIMENTO")
                else:
                    destino_conf = st.selectbox(
                        "Localização de Destino",
                        st.session_state.localizacoes["Código"].tolist()
                    )

                resultado_conf = st.selectbox(
                    "Resultado da Conferência",
                    [
                        "Conforme",
                        "Falta",
                        "Excesso",
                        "Avaria",
                        "Não conformidade",
                        "Divergência documental",
                        "Outro"
                    ]
                )

                tratativa_conf = st.selectbox(
                    "Tratativa",
                    [
                        "Liberar para Estoque Disponível",
                        "Enviar para Quarentena",
                        "Bloquear Estoque",
                        "Recusar / Devolver ao Fornecedor"
                    ]
                )

            observacao_conf = st.text_area("Observação da Conferência")

            confirmar_conf = st.form_submit_button("Registrar Conferência de Entrada")

            if confirmar_conf:
                diferenca_conf = quantidade_recebida - quantidade_esperada

                if documento_conf == "":
                    st.error("Informe o documento, NF, pedido ou referência.")
                elif quantidade_recebida == 0:
                    st.error("A quantidade recebida deve ser maior que zero.")
                else:
                    if tratativa_conf == "Liberar para Estoque Disponível":
                        status_estoque_conf = "Disponível"
                    elif tratativa_conf == "Enviar para Quarentena":
                        status_estoque_conf = "Quarentena"
                    elif tratativa_conf == "Bloquear Estoque":
                        status_estoque_conf = "Bloqueado"
                    else:
                        status_estoque_conf = "Fora do Estoque"

                    nova_conferencia = {
                        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Documento / Referência": documento_conf,
                        "Fornecedor": fornecedor_conf,
                        "SKU": sku_conf,
                        "Descrição": descricao_conf,
                        "Lote": lote_conf,
                        "Validade": validade_conf.strftime("%d/%m/%Y"),
                        "Quantidade Esperada": quantidade_esperada,
                        "Quantidade Recebida": quantidade_recebida,
                        "Diferença": diferenca_conf,
                        "Resultado": resultado_conf,
                        "Tratativa": tratativa_conf,
                        "Localização Destino": destino_conf,
                        "Status Estoque": status_estoque_conf,
                        "Usuário": usuario_logado,
                        "Observação": observacao_conf
                    }

                    st.session_state.conferencias_entrada = pd.concat(
                        [
                            st.session_state.conferencias_entrada,
                            pd.DataFrame([nova_conferencia])
                        ],
                        ignore_index=True
                    )

                    if tratativa_conf != "Recusar / Devolver ao Fornecedor":
                        novo_estoque_conf = {
                            "SKU": sku_conf,
                            "Descrição": descricao_conf,
                            "Localização": destino_conf,
                            "Lote": lote_conf,
                            "Validade": validade_conf.strftime("%d/%m/%Y"),
                            "Quantidade": quantidade_recebida,
                            "Status Estoque": status_estoque_conf
                        }

                        st.session_state.estoque = pd.concat(
                            [
                                st.session_state.estoque,
                                pd.DataFrame([novo_estoque_conf])
                            ],
                            ignore_index=True
                        )

                    registrar_movimentacao(
                        tipo="Conferência de Entrada",
                        sku=sku_conf,
                        descricao=descricao_conf,
                        origem=fornecedor_conf if fornecedor_conf != "" else "Fornecedor",
                        destino=destino_conf if tratativa_conf != "Recusar / Devolver ao Fornecedor" else "Recusado / Devolver ao Fornecedor",
                        quantidade=quantidade_recebida,
                        usuario=usuario_logado,
                        observacao=(
                            f"Documento: {documento_conf}. "
                            f"Esperado: {quantidade_esperada}. "
                            f"Recebido: {quantidade_recebida}. "
                            f"Diferença: {diferenca_conf}. "
                            f"Resultado: {resultado_conf}. "
                            f"Tratativa: {tratativa_conf}. "
                            f"Lote: {lote_conf}. "
                            f"Status estoque: {status_estoque_conf}. "
                            f"Obs: {observacao_conf}"
                        )
                    )

                    if tratativa_conf == "Recusar / Devolver ao Fornecedor":
                        st.warning("Conferência registrada. O material não foi lançado no estoque.")
                    else:
                        st.success("Conferência registrada e material lançado no estoque com sucesso.")

    st.divider()

    st.subheader("Histórico de Conferências de Entrada")

    if st.session_state.conferencias_entrada.empty:
        st.info("Ainda não existem conferências de entrada registradas.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_doc_conf = st.text_input("Filtrar por Documento", key="filtro_doc_conf")

        with col2:
            filtro_sku_conf = st.text_input("Filtrar por SKU", key="filtro_sku_conf")

        with col3:
            filtro_resultado_conf = st.selectbox(
                "Filtrar por Resultado",
                [
                    "Todos",
                    "Conforme",
                    "Falta",
                    "Excesso",
                    "Avaria",
                    "Não conformidade",
                    "Divergência documental",
                    "Outro"
                ],
                key="filtro_resultado_conf"
            )

        df_conf = st.session_state.conferencias_entrada.copy()

        if filtro_doc_conf:
            df_conf = df_conf[
                df_conf["Documento / Referência"].astype(str).str.contains(
                    filtro_doc_conf,
                    case=False,
                    na=False
                )
            ]

        if filtro_sku_conf:
            df_conf = df_conf[
                df_conf["SKU"].astype(str).str.contains(
                    filtro_sku_conf,
                    case=False,
                    na=False
                )
            ]

        if filtro_resultado_conf != "Todos":
            df_conf = df_conf[
                df_conf["Resultado"] == filtro_resultado_conf
            ]

        st.dataframe(df_conf, use_container_width=True)

        st.subheader("Resumo das Conferências")

        if df_conf.empty:
            st.info("Nenhuma conferência encontrada com os filtros selecionados.")
        else:
            resumo_conf = df_conf.groupby(
                ["Resultado", "Tratativa"],
                as_index=False
            )["Quantidade Recebida"].sum()

            st.dataframe(resumo_conf, use_container_width=True)

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
# BLOQUEIO / DESBLOQUEIO
# =========================

elif modulo == "Bloqueio / Desbloqueio":
    st.header("Bloqueio / Desbloqueio de Estoque")

    st.write(
        "Nesta área você pode alterar o status do estoque para Disponível, Quarentena ou Bloqueado."
    )

    if st.session_state.estoque.empty:
        st.warning("Não há estoque cadastrado para bloquear ou desbloquear.")
    else:
        st.subheader("Selecionar Item de Estoque")

        estoque_operacao = st.session_state.estoque.copy()

        estoque_operacao["Opção"] = (
            estoque_operacao["SKU"].astype(str)
            + " | "
            + estoque_operacao["Descrição"].astype(str)
            + " | Local: "
            + estoque_operacao["Localização"].astype(str)
            + " | Lote: "
            + estoque_operacao["Lote"].astype(str)
            + " | Qtd: "
            + estoque_operacao["Quantidade"].astype(str)
            + " | Status: "
            + estoque_operacao["Status Estoque"].astype(str)
        )

        opcao_item = st.selectbox(
            "Escolha o item",
            estoque_operacao["Opção"].tolist()
        )

        indice_item = estoque_operacao[
            estoque_operacao["Opção"] == opcao_item
        ].index[0]

        item_estoque = st.session_state.estoque.loc[indice_item]

        sku_bloq = item_estoque["SKU"]
        descricao_bloq = item_estoque["Descrição"]
        local_bloq = item_estoque["Localização"]
        lote_bloq = item_estoque["Lote"]
        validade_bloq = item_estoque["Validade"]
        quantidade_bloq = item_estoque["Quantidade"]
        status_atual_bloq = item_estoque["Status Estoque"]

        st.divider()

        st.subheader("Dados do Item Selecionado")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input("SKU", value=sku_bloq, disabled=True)
            st.text_input("Descrição", value=descricao_bloq, disabled=True)

        with col2:
            st.text_input("Localização", value=local_bloq, disabled=True)
            st.text_input("Lote", value=lote_bloq, disabled=True)

        with col3:
            st.text_input("Validade", value=validade_bloq, disabled=True)
            st.text_input("Quantidade", value=str(quantidade_bloq), disabled=True)

        st.info(f"Status atual do estoque: {status_atual_bloq}")

        st.divider()

        st.subheader("Alterar Status do Estoque")

        with st.form("form_bloqueio_desbloqueio"):
            novo_status = st.selectbox(
                "Novo Status",
                [
                    "Disponível",
                    "Quarentena",
                    "Bloqueado"
                ]
            )

            motivo_status = st.selectbox(
                "Motivo",
                [
                    "Liberação de Qualidade",
                    "Avaria",
                    "Divergência de Recebimento",
                    "Divergência de Inventário",
                    "Produto em Análise",
                    "Vencimento / Validade",
                    "Bloqueio Operacional",
                    "Desbloqueio Operacional",
                    "Outro"
                ]
            )

            observacao_status = st.text_area("Observação")

            confirmar_status = st.form_submit_button("Confirmar Alteração de Status")

            if confirmar_status:
                if novo_status == status_atual_bloq:
                    st.warning("O novo status é igual ao status atual. Nenhuma alteração foi realizada.")
                else:
                    st.session_state.estoque.at[indice_item, "Status Estoque"] = novo_status

                    registrar_movimentacao(
                        tipo="Alteração de Status",
                        sku=sku_bloq,
                        descricao=descricao_bloq,
                        origem=status_atual_bloq,
                        destino=novo_status,
                        quantidade=quantidade_bloq,
                        usuario=usuario_logado,
                        observacao=(
                            f"Motivo: {motivo_status}. "
                            f"Localização: {local_bloq}. "
                            f"Lote: {lote_bloq}. "
                            f"Obs: {observacao_status}"
                        )
                    )

                    st.success(f"Status alterado de '{status_atual_bloq}' para '{novo_status}' com sucesso.")

# =========================
# GESTÃO DE LOTES E VALIDADES
# =========================

elif modulo == "Gestão de Lotes e Validades":
    st.header("Gestão de Lotes e Validades")

    st.write(
        "Nesta área você pode consultar lotes, validades, itens vencidos e itens próximos do vencimento."
    )

    if st.session_state.estoque.empty:
        st.warning("Não há estoque cadastrado para análise de lotes e validades.")
    else:
        df_lotes = st.session_state.estoque.copy()

        # Converter validade para data
        df_lotes["Data Validade"] = pd.to_datetime(
            df_lotes["Validade"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        hoje = pd.Timestamp(date.today())

        df_lotes["Dias para Vencer"] = (
            df_lotes["Data Validade"] - hoje
        ).dt.days

        def classificar_validade(dias):
            if pd.isna(dias):
                return "Sem validade informada"
            elif dias < 0:
                return "Vencido"
            elif dias <= 30:
                return "Vence em até 30 dias"
            elif dias <= 60:
                return "Vence em até 60 dias"
            elif dias <= 90:
                return "Vence em até 90 dias"
            else:
                return "Dentro da validade"

        df_lotes["Situação Validade"] = df_lotes["Dias para Vencer"].apply(classificar_validade)

        st.subheader("Indicadores de Validade")

        total_lotes = df_lotes["Lote"].nunique()
        itens_vencidos = len(df_lotes[df_lotes["Situação Validade"] == "Vencido"])
        itens_30_dias = len(df_lotes[df_lotes["Situação Validade"] == "Vence em até 30 dias"])
        itens_sem_validade = len(df_lotes[df_lotes["Situação Validade"] == "Sem validade informada"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Lotes Diferentes", total_lotes)
        col2.metric("Itens Vencidos", itens_vencidos)
        col3.metric("Vencem em até 30 dias", itens_30_dias)
        col4.metric("Sem Validade Informada", itens_sem_validade)

        st.divider()

        st.subheader("Filtros")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            filtro_sku_lote = st.text_input("Filtrar por SKU")

        with col2:
            filtro_lote = st.text_input("Filtrar por Lote")

        with col3:
            filtro_status_estoque = st.selectbox(
                "Status do Estoque",
                [
                    "Todos",
                    "Disponível",
                    "Quarentena",
                    "Bloqueado"
                ]
            )

        with col4:
            filtro_validade = st.selectbox(
                "Situação da Validade",
                [
                    "Todos",
                    "Vencido",
                    "Vence em até 30 dias",
                    "Vence em até 60 dias",
                    "Vence em até 90 dias",
                    "Dentro da validade",
                    "Sem validade informada"
                ]
            )

        df_filtrado = df_lotes.copy()

        if filtro_sku_lote:
            df_filtrado = df_filtrado[
                df_filtrado["SKU"].astype(str).str.contains(
                    filtro_sku_lote,
                    case=False,
                    na=False
                )
            ]

        if filtro_lote:
            df_filtrado = df_filtrado[
                df_filtrado["Lote"].astype(str).str.contains(
                    filtro_lote,
                    case=False,
                    na=False
                )
            ]

        if filtro_status_estoque != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["Status Estoque"] == filtro_status_estoque
            ]

        if filtro_validade != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["Situação Validade"] == filtro_validade
            ]

        st.divider()

        st.subheader("Consulta Detalhada por Lote e Validade")

        colunas_exibir = [
            "SKU",
            "Descrição",
            "Localização",
            "Lote",
            "Validade",
            "Quantidade",
            "Status Estoque",
            "Dias para Vencer",
            "Situação Validade"
        ]

        st.dataframe(
            df_filtrado[colunas_exibir],
            use_container_width=True
        )

        st.divider()

        st.subheader("Resumo por SKU, Lote e Validade")

        if df_filtrado.empty:
            st.info("Nenhum item encontrado com os filtros selecionados.")
        else:
            resumo_lotes = df_filtrado.groupby(
                [
                    "SKU",
                    "Descrição",
                    "Lote",
                    "Validade",
                    "Status Estoque",
                    "Situação Validade"
                ],
                as_index=False
            )["Quantidade"].sum()

            st.dataframe(
                resumo_lotes,
                use_container_width=True
            )

        st.divider()

        st.subheader("Alertas Operacionais")

        vencidos = df_lotes[df_lotes["Situação Validade"] == "Vencido"]
        proximos_30 = df_lotes[df_lotes["Situação Validade"] == "Vence em até 30 dias"]

        if vencidos.empty and proximos_30.empty:
            st.success("Não há itens vencidos ou vencendo em até 30 dias.")
        else:
            if not vencidos.empty:
                st.error("Existem itens vencidos. Recomenda-se avaliar bloqueio, segregação ou descarte.")
                st.dataframe(
                    vencidos[colunas_exibir],
                    use_container_width=True
                )

            if not proximos_30.empty:
                st.warning("Existem itens vencendo em até 30 dias. Recomenda-se priorizar consumo, picking ou análise.")
                st.dataframe(
                    proximos_30[colunas_exibir],
                    use_container_width=True
                )

# =========================
# RASTREABILIDADE
# =========================

elif modulo == "Rastreabilidade":
    st.header("Rastreabilidade")

    st.write(
        "Nesta área você pode consultar o histórico operacional por SKU, lote, pedido, localização, usuário ou tipo de movimentação."
    )

    st.divider()

    st.subheader("Filtros de Rastreabilidade")

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_sku_rast = st.text_input("SKU")
        filtro_lote_rast = st.text_input("Lote")

    with col2:
        filtro_pedido_rast = st.text_input("Pedido / Ordem")
        filtro_local_rast = st.text_input("Localização")

    with col3:
        filtro_usuario_rast = st.text_input("Usuário")
        filtro_tipo_rast = st.text_input("Tipo de Movimentação")

    st.divider()

    aba1, aba2, aba3 = st.tabs([
        "Estoque Atual",
        "Movimentações",
        "Pedidos / Ordens"
    ])

    # =========================
    # ABA 1 - ESTOQUE ATUAL
    # =========================

    with aba1:
        st.subheader("Rastreabilidade no Estoque Atual")

        if st.session_state.estoque.empty:
            st.info("Não há estoque cadastrado.")
        else:
            df_estoque_rast = st.session_state.estoque.copy()

            if filtro_sku_rast:
                df_estoque_rast = df_estoque_rast[
                    df_estoque_rast["SKU"].astype(str).str.contains(
                        filtro_sku_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_lote_rast:
                df_estoque_rast = df_estoque_rast[
                    df_estoque_rast["Lote"].astype(str).str.contains(
                        filtro_lote_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_local_rast:
                df_estoque_rast = df_estoque_rast[
                    df_estoque_rast["Localização"].astype(str).str.contains(
                        filtro_local_rast,
                        case=False,
                        na=False
                    )
                ]

            if df_estoque_rast.empty:
                st.info("Nenhum registro de estoque encontrado com os filtros informados.")
            else:
                st.dataframe(df_estoque_rast, use_container_width=True)

                st.subheader("Resumo por SKU, Lote e Localização")

                resumo_estoque_rast = df_estoque_rast.groupby(
                    [
                        "SKU",
                        "Descrição",
                        "Lote",
                        "Validade",
                        "Localização",
                        "Status Estoque"
                    ],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_estoque_rast, use_container_width=True)

    # =========================
    # ABA 2 - MOVIMENTAÇÕES
    # =========================

    with aba2:
        st.subheader("Rastreabilidade nas Movimentações")

        if st.session_state.movimentacoes.empty:
            st.info("Não há movimentações registradas.")
        else:
            df_mov_rast = st.session_state.movimentacoes.copy()

            if filtro_sku_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["SKU"].astype(str).str.contains(
                        filtro_sku_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_pedido_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["Destino"].astype(str).str.contains(
                        filtro_pedido_rast,
                        case=False,
                        na=False
                    ) |
                    df_mov_rast["Origem"].astype(str).str.contains(
                        filtro_pedido_rast,
                        case=False,
                        na=False
                    ) |
                    df_mov_rast["Observação"].astype(str).str.contains(
                        filtro_pedido_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_local_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["Origem"].astype(str).str.contains(
                        filtro_local_rast,
                        case=False,
                        na=False
                    ) |
                    df_mov_rast["Destino"].astype(str).str.contains(
                        filtro_local_rast,
                        case=False,
                        na=False
                    ) |
                    df_mov_rast["Observação"].astype(str).str.contains(
                        filtro_local_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_usuario_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["Usuário"].astype(str).str.contains(
                        filtro_usuario_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_tipo_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["Tipo"].astype(str).str.contains(
                        filtro_tipo_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_lote_rast:
                df_mov_rast = df_mov_rast[
                    df_mov_rast["Observação"].astype(str).str.contains(
                        filtro_lote_rast,
                        case=False,
                        na=False
                    )
                ]

            if df_mov_rast.empty:
                st.info("Nenhuma movimentação encontrada com os filtros informados.")
            else:
                st.dataframe(df_mov_rast, use_container_width=True)

                st.subheader("Resumo de Movimentações por Tipo")

                resumo_mov_tipo = df_mov_rast.groupby(
                    ["Tipo"],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_mov_tipo, use_container_width=True)

                st.subheader("Resumo de Movimentações por Usuário")

                resumo_mov_usuario = df_mov_rast.groupby(
                    ["Usuário"],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_mov_usuario, use_container_width=True)

    # =========================
    # ABA 3 - PEDIDOS / ORDENS
    # =========================

    with aba3:
        st.subheader("Rastreabilidade em Pedidos / Ordens")

        if st.session_state.pedidos.empty:
            st.info("Não há pedidos ou ordens cadastrados.")
        else:
            df_pedidos_rast = st.session_state.pedidos.copy()

            if filtro_sku_rast:
                df_pedidos_rast = df_pedidos_rast[
                    df_pedidos_rast["SKU"].astype(str).str.contains(
                        filtro_sku_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_pedido_rast:
                df_pedidos_rast = df_pedidos_rast[
                    df_pedidos_rast["Pedido"].astype(str).str.contains(
                        filtro_pedido_rast,
                        case=False,
                        na=False
                    )
                ]

            if filtro_usuario_rast:
                df_pedidos_rast = df_pedidos_rast[
                    df_pedidos_rast["Observação"].astype(str).str.contains(
                        filtro_usuario_rast,
                        case=False,
                        na=False
                    )
                ]

            if df_pedidos_rast.empty:
                st.info("Nenhum pedido encontrado com os filtros informados.")
            else:
                st.dataframe(df_pedidos_rast, use_container_width=True)

                st.subheader("Resumo de Pedidos por Status")

                resumo_pedidos_status = df_pedidos_rast.groupby(
                    ["Status"],
                    as_index=False
                )["Pedido"].count()

                resumo_pedidos_status = resumo_pedidos_status.rename(
                    columns={"Pedido": "Quantidade"}
                )

                st.dataframe(resumo_pedidos_status, use_container_width=True)

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
                numero_pedido_limpo = numero_pedido.strip()
                cliente_destino_limpo = cliente_destino.strip()

                pedido_sku_duplicado = False

                if not st.session_state.pedidos.empty:
                    pedido_sku_duplicado = (
                        (
                            st.session_state.pedidos["Pedido"].astype(str).str.strip().str.upper()
                            == numero_pedido_limpo.upper()
                        )
                        &
                        (
                            st.session_state.pedidos["SKU"].astype(str).str.strip().str.upper()
                            == str(sku_pedido).strip().upper()
                        )
                    ).any()

                if numero_pedido_limpo == "":
                    st.error("Informe o número do pedido ou ordem.")
                elif pedido_sku_duplicado:
                    st.error("Este pedido já possui este SKU cadastrado. Verifique antes de duplicar a linha.")
                else:
                    novo_pedido = {
                        "Pedido": numero_pedido_limpo,
                        "Cliente / Destino": cliente_destino_limpo,
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
                df_pedidos["Pedido"].astype(str).str.contains(
                    filtro_pedido,
                    case=False,
                    na=False
                )
            ]

        if filtro_sku_pedido:
            df_pedidos = df_pedidos[
                df_pedidos["SKU"].astype(str).str.contains(
                    filtro_sku_pedido,
                    case=False,
                    na=False
                )
            ]

        if filtro_status_pedido != "Todos":
            df_pedidos = df_pedidos[df_pedidos["Status"] == filtro_status_pedido]

        st.dataframe(df_pedidos, use_container_width=True)



# =========================
# GESTÃO DE STATUS DE PEDIDOS
# =========================

elif modulo == "Gestão de Status de Pedidos":
    st.header("Gestão de Status de Pedidos")

    st.write(
        "Nesta área você pode cancelar, reabrir ou alterar o status de pedidos com registro de motivo no histórico."
    )

    if st.session_state.pedidos.empty:
        st.warning("Não existem pedidos cadastrados para gerenciar.")
    else:
        pedidos_status = st.session_state.pedidos.copy()

        pedidos_status["Opção"] = (
            pedidos_status["Pedido"].astype(str)
            + " | SKU: "
            + pedidos_status["SKU"].astype(str)
            + " | Qtd: "
            + pedidos_status["Quantidade"].astype(str)
            + " | Status Atual: "
            + pedidos_status["Status"].astype(str)
        )

        opcao_pedido_status = st.selectbox(
            "Selecione o Pedido / Ordem",
            pedidos_status["Opção"].tolist()
        )

        indice_pedido_status = pedidos_status[
            pedidos_status["Opção"] == opcao_pedido_status
        ].index[0]

        pedido_status = st.session_state.pedidos.loc[indice_pedido_status]

        numero_pedido_status = pedido_status["Pedido"]
        cliente_destino_status = pedido_status["Cliente / Destino"]
        sku_status = pedido_status["SKU"]
        descricao_status = pedido_status["Descrição"]
        quantidade_status = pedido_status["Quantidade"]
        prioridade_status = pedido_status["Prioridade"]
        status_atual_pedido = pedido_status["Status"]

        st.divider()

        st.subheader("Dados do Pedido Selecionado")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input("Pedido", value=numero_pedido_status, disabled=True)
            st.text_input("Cliente / Destino", value=cliente_destino_status, disabled=True)

        with col2:
            st.text_input("SKU", value=sku_status, disabled=True)
            st.text_input("Descrição", value=descricao_status, disabled=True)

        with col3:
            st.text_input("Quantidade", value=str(quantidade_status), disabled=True)
            st.text_input("Status Atual", value=status_atual_pedido, disabled=True)

        st.divider()

        st.subheader("Alterar Status")

        with st.form("form_gestao_status_pedidos"):
            novo_status_pedido = st.selectbox(
                "Novo Status",
                [
                    "Criado",
                    "Aguardando Picking",
                    "Em Picking",
                    "Separado",
                    "Conferido",
                    "Expedido",
                    "Cancelado"
                ]
            )

            motivo_status_pedido = st.selectbox(
                "Motivo",
                [
                    "Erro de cadastro",
                    "Solicitação do cliente",
                    "Falta de estoque",
                    "Erro operacional",
                    "Divergência na separação",
                    "Divergência na expedição",
                    "Reabertura para correção",
                    "Cancelamento comercial",
                    "Outro"
                ]
            )

            observacao_status_pedido = st.text_area("Observação")

            confirmar_status_pedido = st.form_submit_button("Confirmar Alteração de Status")

            if confirmar_status_pedido:
                if novo_status_pedido == status_atual_pedido:
                    st.warning("O novo status é igual ao status atual. Nenhuma alteração foi realizada.")
                elif observacao_status_pedido.strip() == "":
                    st.error("Informe uma observação para registrar o motivo da alteração.")
                else:
                    st.session_state.pedidos.at[indice_pedido_status, "Status"] = novo_status_pedido

                    registrar_movimentacao(
                        tipo="Alteração de Status de Pedido",
                        sku=sku_status,
                        descricao=descricao_status,
                        origem=status_atual_pedido,
                        destino=novo_status_pedido,
                        quantidade=quantidade_status,
                        usuario=usuario_logado,
                        observacao=(
                            f"Pedido: {numero_pedido_status}. "
                            f"Cliente/Destino: {cliente_destino_status}. "
                            f"Motivo: {motivo_status_pedido}. "
                            f"Obs: {observacao_status_pedido}"
                        )
                    )

                    st.success(
                        f"Status do pedido {numero_pedido_status} alterado de "
                        f"'{status_atual_pedido}' para '{novo_status_pedido}' com sucesso."
                    )

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
# DEVOLUÇÕES
# =========================

elif modulo == "Devoluções":
    st.header("Devoluções")

    st.write(
        "Nesta área você pode registrar devoluções de cliente, retornos internos e devoluções para fornecedor."
    )

    tipo_devolucao = st.selectbox(
        "Tipo de Devolução",
        [
            "Devolução de Cliente / Retorno",
            "Devolução para Fornecedor"
        ]
    )

    st.divider()

    # =========================
    # DEVOLUÇÃO DE CLIENTE / RETORNO
    # =========================

    if tipo_devolucao == "Devolução de Cliente / Retorno":
        st.subheader("Registrar Devolução de Cliente / Retorno")

        if st.session_state.produtos.empty:
            st.warning("Cadastre produtos antes de registrar devoluções.")
        else:
            with st.form("form_devolucao_cliente"):
                col1, col2 = st.columns(2)

                with col1:
                    documento_ref = st.text_input("Documento / Pedido / Referência")
                    origem_dev = st.text_input("Origem da Devolução", value="Cliente")
                    sku_dev = st.selectbox("SKU", st.session_state.produtos["SKU"].tolist())
                    descricao_dev = obter_descricao_produto(sku_dev)
                    st.text_input("Descrição", value=descricao_dev, disabled=True)

                    lote_dev = st.text_input("Lote")
                    validade_dev = st.date_input("Validade", value=date.today())

                with col2:
                    quantidade_dev = st.number_input("Quantidade Devolvida", min_value=1, step=1)

                    if st.session_state.localizacoes.empty:
                        destino_dev = st.text_input("Localização de Destino", value="QUARENTENA")
                    else:
                        destino_dev = st.selectbox(
                            "Localização de Destino",
                            st.session_state.localizacoes["Código"].tolist()
                        )

                    tratativa_dev = st.selectbox(
                        "Tratativa",
                        [
                            "Retornar ao Estoque Disponível",
                            "Enviar para Quarentena",
                            "Bloquear Estoque",
                            "Descarte / Sucata"
                        ]
                    )

                    motivo_dev = st.selectbox(
                        "Motivo da Devolução",
                        [
                            "Produto errado",
                            "Avaria",
                            "Excesso",
                            "Cancelamento",
                            "Não conformidade",
                            "Retorno de cliente",
                            "Erro operacional",
                            "Outro"
                        ]
                    )

                observacao_dev = st.text_area("Observação")

                confirmar_dev_cliente = st.form_submit_button("Registrar Devolução")

                if confirmar_dev_cliente:
                    if tratativa_dev == "Retornar ao Estoque Disponível":
                        status_estoque_dev = "Disponível"
                    elif tratativa_dev == "Enviar para Quarentena":
                        status_estoque_dev = "Quarentena"
                    elif tratativa_dev == "Bloquear Estoque":
                        status_estoque_dev = "Bloqueado"
                    else:
                        status_estoque_dev = "Fora do Estoque"

                    if tratativa_dev != "Descarte / Sucata":
                        novo_estoque_dev = {
                            "SKU": sku_dev,
                            "Descrição": descricao_dev,
                            "Localização": destino_dev,
                            "Lote": lote_dev,
                            "Validade": validade_dev.strftime("%d/%m/%Y"),
                            "Quantidade": quantidade_dev,
                            "Status Estoque": status_estoque_dev
                        }

                        st.session_state.estoque = pd.concat(
                            [st.session_state.estoque, pd.DataFrame([novo_estoque_dev])],
                            ignore_index=True
                        )

                    nova_devolucao = {
                        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Tipo Devolução": tipo_devolucao,
                        "Documento / Referência": documento_ref,
                        "Origem": origem_dev,
                        "Destino": destino_dev,
                        "SKU": sku_dev,
                        "Descrição": descricao_dev,
                        "Lote": lote_dev,
                        "Validade": validade_dev.strftime("%d/%m/%Y"),
                        "Quantidade": quantidade_dev,
                        "Tratativa": tratativa_dev,
                        "Status Estoque": status_estoque_dev,
                        "Usuário": usuario_logado,
                        "Motivo": motivo_dev,
                        "Observação": observacao_dev
                    }

                    st.session_state.devolucoes = pd.concat(
                        [st.session_state.devolucoes, pd.DataFrame([nova_devolucao])],
                        ignore_index=True
                    )

                    registrar_movimentacao(
                        tipo="Devolução de Cliente",
                        sku=sku_dev,
                        descricao=descricao_dev,
                        origem=origem_dev,
                        destino=destino_dev if tratativa_dev != "Descarte / Sucata" else "Descarte / Sucata",
                        quantidade=quantidade_dev,
                        usuario=usuario_logado,
                        observacao=(
                            f"Documento: {documento_ref}. "
                            f"Tratativa: {tratativa_dev}. "
                            f"Motivo: {motivo_dev}. "
                            f"Lote: {lote_dev}. "
                            f"Obs: {observacao_dev}"
                        )
                    )

                    st.success("Devolução de cliente / retorno registrada com sucesso.")

    # =========================
    # DEVOLUÇÃO PARA FORNECEDOR
    # =========================

    elif tipo_devolucao == "Devolução para Fornecedor":
        st.subheader("Registrar Devolução para Fornecedor")

        if st.session_state.estoque.empty:
            st.warning("Não há estoque disponível para devolução ao fornecedor.")
        else:
            estoque_dev_forn = st.session_state.estoque.copy()

            estoque_dev_forn["Opção"] = (
                estoque_dev_forn["SKU"].astype(str)
                + " | "
                + estoque_dev_forn["Descrição"].astype(str)
                + " | Local: "
                + estoque_dev_forn["Localização"].astype(str)
                + " | Lote: "
                + estoque_dev_forn["Lote"].astype(str)
                + " | Qtd: "
                + estoque_dev_forn["Quantidade"].astype(str)
                + " | Status: "
                + estoque_dev_forn["Status Estoque"].astype(str)
            )

            with st.form("form_devolucao_fornecedor"):
                col1, col2 = st.columns(2)

                with col1:
                    documento_ref_forn = st.text_input("Documento / NF / Referência")
                    fornecedor_dev = st.text_input("Fornecedor")
                    opcao_item_forn = st.selectbox(
                        "Item para Devolver",
                        estoque_dev_forn["Opção"].tolist()
                    )

                indice_item_forn = estoque_dev_forn[
                    estoque_dev_forn["Opção"] == opcao_item_forn
                ].index[0]

                item_forn = st.session_state.estoque.loc[indice_item_forn]

                sku_forn = item_forn["SKU"]
                descricao_forn = item_forn["Descrição"]
                local_forn = item_forn["Localização"]
                lote_forn = item_forn["Lote"]
                validade_forn = item_forn["Validade"]
                quantidade_disponivel_forn = int(item_forn["Quantidade"])
                status_forn = item_forn["Status Estoque"]

                with col2:
                    st.text_input("SKU", value=sku_forn, disabled=True)
                    st.text_input("Localização", value=local_forn, disabled=True)
                    st.text_input("Lote", value=lote_forn, disabled=True)
                    st.text_input("Saldo da Linha", value=str(quantidade_disponivel_forn), disabled=True)

                    quantidade_forn = st.number_input(
                        "Quantidade a Devolver",
                        min_value=1,
                        step=1
                    )

                    motivo_forn = st.selectbox(
                        "Motivo da Devolução",
                        [
                            "Produto errado",
                            "Avaria",
                            "Não conformidade",
                            "Divergência de recebimento",
                            "Vencimento / Validade",
                            "Erro operacional",
                            "Outro"
                        ]
                    )

                observacao_forn = st.text_area("Observação")

                confirmar_dev_forn = st.form_submit_button("Registrar Devolução para Fornecedor")

                if confirmar_dev_forn:
                    if quantidade_forn > quantidade_disponivel_forn:
                        st.error("Quantidade a devolver maior que o saldo disponível da linha selecionada.")
                    else:
                        nova_qtd = quantidade_disponivel_forn - quantidade_forn
                        st.session_state.estoque.at[indice_item_forn, "Quantidade"] = nova_qtd

                        st.session_state.estoque = st.session_state.estoque[
                            st.session_state.estoque["Quantidade"] > 0
                        ]

                        nova_devolucao_forn = {
                            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "Tipo Devolução": tipo_devolucao,
                            "Documento / Referência": documento_ref_forn,
                            "Origem": local_forn,
                            "Destino": fornecedor_dev,
                            "SKU": sku_forn,
                            "Descrição": descricao_forn,
                            "Lote": lote_forn,
                            "Validade": validade_forn,
                            "Quantidade": quantidade_forn,
                            "Tratativa": "Saída para fornecedor",
                            "Status Estoque": status_forn,
                            "Usuário": usuario_logado,
                            "Motivo": motivo_forn,
                            "Observação": observacao_forn
                        }

                        st.session_state.devolucoes = pd.concat(
                            [st.session_state.devolucoes, pd.DataFrame([nova_devolucao_forn])],
                            ignore_index=True
                        )

                        registrar_movimentacao(
                            tipo="Devolução para Fornecedor",
                            sku=sku_forn,
                            descricao=descricao_forn,
                            origem=local_forn,
                            destino=fornecedor_dev,
                            quantidade=quantidade_forn,
                            usuario=usuario_logado,
                            observacao=(
                                f"Documento: {documento_ref_forn}. "
                                f"Motivo: {motivo_forn}. "
                                f"Lote: {lote_forn}. "
                                f"Status estoque: {status_forn}. "
                                f"Obs: {observacao_forn}"
                            )
                        )

                        st.success("Devolução para fornecedor registrada com sucesso.")

    st.divider()

    st.subheader("Histórico de Devoluções")

    if st.session_state.devolucoes.empty:
        st.info("Ainda não existem devoluções registradas.")
    else:
        st.dataframe(st.session_state.devolucoes, use_container_width=True)

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
# RELATÓRIOS / EXPORTAR DADOS
# =========================

elif modulo == "Relatórios / Exportar Dados":
    st.header("Relatórios / Exportar Dados")

    st.write(
        "Nesta área você pode consultar relatórios operacionais e baixar as bases atuais em CSV."
    )

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "Estoque Geral",
        "Pedidos / Ordens",
        "Movimentações",
        "Alertas Operacionais",
        "Exportar CSV"
    ])

    # =========================
    # ABA 1 - ESTOQUE GERAL
    # =========================

    with aba1:
        st.subheader("Relatório de Estoque Geral")

        if st.session_state.estoque.empty:
            st.info("Não há estoque cadastrado.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                filtro_sku_rel = st.text_input("Filtrar SKU", key="rel_estoque_sku")

            with col2:
                filtro_local_rel = st.text_input("Filtrar Localização", key="rel_estoque_local")

            with col3:
                filtro_status_rel = st.selectbox(
                    "Filtrar Status",
                    [
                        "Todos",
                        "Disponível",
                        "Quarentena",
                        "Bloqueado"
                    ],
                    key="rel_estoque_status"
                )

            df_rel_estoque = st.session_state.estoque.copy()

            if filtro_sku_rel:
                df_rel_estoque = df_rel_estoque[
                    df_rel_estoque["SKU"].astype(str).str.contains(
                        filtro_sku_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_local_rel:
                df_rel_estoque = df_rel_estoque[
                    df_rel_estoque["Localização"].astype(str).str.contains(
                        filtro_local_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_status_rel != "Todos":
                df_rel_estoque = df_rel_estoque[
                    df_rel_estoque["Status Estoque"] == filtro_status_rel
                ]

            st.dataframe(df_rel_estoque, use_container_width=True)

            st.divider()

            st.subheader("Resumo por SKU")

            if df_rel_estoque.empty:
                st.info("Nenhum item encontrado com os filtros selecionados.")
            else:
                resumo_sku = df_rel_estoque.groupby(
                    [
                        "SKU",
                        "Descrição",
                        "Status Estoque"
                    ],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_sku, use_container_width=True)

                total_qtd = df_rel_estoque["Quantidade"].sum()
                total_skus = df_rel_estoque["SKU"].nunique()
                total_locais = df_rel_estoque["Localização"].nunique()

                col1, col2, col3 = st.columns(3)

                col1.metric("Quantidade Total", total_qtd)
                col2.metric("SKUs no Relatório", total_skus)
                col3.metric("Localizações no Relatório", total_locais)

    # =========================
    # ABA 2 - PEDIDOS / ORDENS
    # =========================

    with aba2:
        st.subheader("Relatório de Pedidos / Ordens")

        if st.session_state.pedidos.empty:
            st.info("Não há pedidos ou ordens cadastrados.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                filtro_pedido_rel = st.text_input("Filtrar Pedido", key="rel_pedido_numero")

            with col2:
                filtro_sku_pedido_rel = st.text_input("Filtrar SKU", key="rel_pedido_sku")

            with col3:
                filtro_status_pedido_rel = st.selectbox(
                    "Filtrar Status",
                    [
                        "Todos",
                        "Criado",
                        "Aguardando Picking",
                        "Em Picking",
                        "Separado",
                        "Conferido",
                        "Expedido",
                        "Cancelado"
                    ],
                    key="rel_pedido_status"
                )

            df_rel_pedidos = st.session_state.pedidos.copy()

            if filtro_pedido_rel:
                df_rel_pedidos = df_rel_pedidos[
                    df_rel_pedidos["Pedido"].astype(str).str.contains(
                        filtro_pedido_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_sku_pedido_rel:
                df_rel_pedidos = df_rel_pedidos[
                    df_rel_pedidos["SKU"].astype(str).str.contains(
                        filtro_sku_pedido_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_status_pedido_rel != "Todos":
                df_rel_pedidos = df_rel_pedidos[
                    df_rel_pedidos["Status"] == filtro_status_pedido_rel
                ]

            st.dataframe(df_rel_pedidos, use_container_width=True)

            st.divider()

            st.subheader("Resumo por Status")

            if df_rel_pedidos.empty:
                st.info("Nenhum pedido encontrado com os filtros selecionados.")
            else:
                resumo_status = df_rel_pedidos.groupby(
                    ["Status"],
                    as_index=False
                )["Pedido"].count()

                resumo_status = resumo_status.rename(
                    columns={"Pedido": "Quantidade"}
                )

                st.dataframe(resumo_status, use_container_width=True)

                total_pedidos = len(df_rel_pedidos)
                total_qtd_pedida = df_rel_pedidos["Quantidade"].sum()

                col1, col2 = st.columns(2)

                col1.metric("Total de Pedidos / Ordens", total_pedidos)
                col2.metric("Quantidade Total Solicitada", total_qtd_pedida)

    # =========================
    # ABA 3 - MOVIMENTAÇÕES
    # =========================

    with aba3:
        st.subheader("Relatório de Movimentações")

        if st.session_state.movimentacoes.empty:
            st.info("Não há movimentações registradas.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                filtro_tipo_mov_rel = st.text_input("Filtrar Tipo", key="rel_mov_tipo")

            with col2:
                filtro_sku_mov_rel = st.text_input("Filtrar SKU", key="rel_mov_sku")

            with col3:
                filtro_usuario_mov_rel = st.text_input("Filtrar Usuário", key="rel_mov_usuario")

            df_rel_mov = st.session_state.movimentacoes.copy()

            if filtro_tipo_mov_rel:
                df_rel_mov = df_rel_mov[
                    df_rel_mov["Tipo"].astype(str).str.contains(
                        filtro_tipo_mov_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_sku_mov_rel:
                df_rel_mov = df_rel_mov[
                    df_rel_mov["SKU"].astype(str).str.contains(
                        filtro_sku_mov_rel,
                        case=False,
                        na=False
                    )
                ]

            if filtro_usuario_mov_rel:
                df_rel_mov = df_rel_mov[
                    df_rel_mov["Usuário"].astype(str).str.contains(
                        filtro_usuario_mov_rel,
                        case=False,
                        na=False
                    )
                ]

            st.dataframe(df_rel_mov, use_container_width=True)

            st.divider()

            st.subheader("Resumo por Tipo de Movimentação")

            if df_rel_mov.empty:
                st.info("Nenhuma movimentação encontrada com os filtros selecionados.")
            else:
                resumo_mov_tipo = df_rel_mov.groupby(
                    ["Tipo"],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_mov_tipo, use_container_width=True)

                st.subheader("Resumo por Usuário")

                resumo_mov_usuario = df_rel_mov.groupby(
                    ["Usuário"],
                    as_index=False
                )["Quantidade"].sum()

                st.dataframe(resumo_mov_usuario, use_container_width=True)

                total_mov = len(df_rel_mov)
                total_qtd_mov = df_rel_mov["Quantidade"].sum()

                col1, col2 = st.columns(2)

                col1.metric("Total de Movimentações", total_mov)
                col2.metric("Quantidade Movimentada", total_qtd_mov)

    # =========================
    # ABA 4 - ALERTAS OPERACIONAIS
    # =========================

    with aba4:
        st.subheader("Alertas Operacionais")

        col1, col2, col3 = st.columns(3)

        # Estoque baixo
        with col1:
            st.markdown("### Estoque Baixo")

            if st.session_state.produtos.empty or st.session_state.estoque.empty:
                st.info("Sem dados suficientes para avaliar estoque baixo.")
            else:
                saldo_sku_alerta = st.session_state.estoque.groupby(
                    ["SKU", "Descrição"],
                    as_index=False
                )["Quantidade"].sum()

                produtos_minimo = st.session_state.produtos[
                    [
                        "SKU",
                        "Estoque Mínimo"
                    ]
                ].copy()

                alerta_minimo = saldo_sku_alerta.merge(
                    produtos_minimo,
                    on="SKU",
                    how="left"
                )

                alerta_minimo["Estoque Mínimo"] = pd.to_numeric(
                    alerta_minimo["Estoque Mínimo"],
                    errors="coerce"
                ).fillna(0)

                alerta_minimo = alerta_minimo[
                    alerta_minimo["Quantidade"] <= alerta_minimo["Estoque Mínimo"]
                ]

                if alerta_minimo.empty:
                    st.success("Nenhum item abaixo do estoque mínimo.")
                else:
                    st.warning("Existem itens abaixo ou iguais ao estoque mínimo.")
                    st.dataframe(alerta_minimo, use_container_width=True)

        # Estoque bloqueado/quarentena
        with col2:
            st.markdown("### Bloqueados / Quarentena")

            if st.session_state.estoque.empty:
                st.info("Não há estoque cadastrado.")
            else:
                alerta_bloqueado = st.session_state.estoque[
                    st.session_state.estoque["Status Estoque"].isin(
                        [
                            "Bloqueado",
                            "Quarentena"
                        ]
                    )
                ]

                if alerta_bloqueado.empty:
                    st.success("Nenhum item bloqueado ou em quarentena.")
                else:
                    st.warning("Existem itens bloqueados ou em quarentena.")
                    st.dataframe(alerta_bloqueado, use_container_width=True)

        # Pedidos pendentes
        with col3:
            st.markdown("### Pedidos Pendentes")

            if st.session_state.pedidos.empty:
                st.info("Não há pedidos cadastrados.")
            else:
                pedidos_pendentes = st.session_state.pedidos[
                    st.session_state.pedidos["Status"].isin(
                        [
                            "Criado",
                            "Aguardando Picking",
                            "Em Picking",
                            "Separado",
                            "Conferido"
                        ]
                    )
                ]

                if pedidos_pendentes.empty:
                    st.success("Nenhum pedido pendente.")
                else:
                    st.warning("Existem pedidos pendentes.")
                    st.dataframe(pedidos_pendentes, use_container_width=True)

        st.divider()

        st.subheader("Validades Críticas")

        if st.session_state.estoque.empty:
            st.info("Não há estoque cadastrado.")
        else:
            df_validade_alerta = st.session_state.estoque.copy()

            df_validade_alerta["Data Validade"] = pd.to_datetime(
                df_validade_alerta["Validade"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            hoje = pd.Timestamp(date.today())

            df_validade_alerta["Dias para Vencer"] = (
                df_validade_alerta["Data Validade"] - hoje
            ).dt.days

            df_validade_alerta = df_validade_alerta[
                df_validade_alerta["Dias para Vencer"].notna()
            ]

            df_vencidos = df_validade_alerta[
                df_validade_alerta["Dias para Vencer"] < 0
            ]

            df_vence_30 = df_validade_alerta[
                (df_validade_alerta["Dias para Vencer"] >= 0) &
                (df_validade_alerta["Dias para Vencer"] <= 30)
            ]

            if df_vencidos.empty and df_vence_30.empty:
                st.success("Não há itens vencidos ou vencendo em até 30 dias.")
            else:
                if not df_vencidos.empty:
                    st.error("Itens vencidos encontrados.")
                    st.dataframe(df_vencidos, use_container_width=True)

                if not df_vence_30.empty:
                    st.warning("Itens vencendo em até 30 dias encontrados.")
                    st.dataframe(df_vence_30, use_container_width=True)

    # =========================
    # ABA 5 - EXPORTAR CSV
    # =========================

    with aba5:
        st.subheader("Exportar Bases em CSV")

        st.write(
            "Use estes botões para baixar as bases atuais do sistema."
        )

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

