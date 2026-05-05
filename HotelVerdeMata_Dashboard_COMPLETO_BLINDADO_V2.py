# ============================================================
# DASHBOARD DE EVENTOS - VERDE DA MATA HOTEL / HOTEL IMPERIAL
# Leitura automática de relatório PDF + Dashboard em Streamlit
#
# Instalação:
# pip install streamlit pandas plotly pdfplumber openpyxl
#
# Execução:
# streamlit run HotelVerdeMata_Dashboard.py
# ============================================================

import io
import re
import unicodedata
from datetime import datetime

import pandas as pd
import pdfplumber
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================
# CONFIGURAÇÃO PRINCIPAL
# =========================

st.set_page_config(
    page_title="Dashboard de Eventos | Verde da Mata Hotel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================
# PALETA VISUAL
# =========================

COR_PRINCIPAL = "#677526"
COR_DESTAQUE = "#afb512"
COR_TEXTO = "#202124"
COR_TEXTO_SUAVE = "#667085"
COR_FUNDO = "#f7f8f3"
COR_CARD = "#ffffff"
COR_BORDA = "#e5e8dc"
COR_ALERTA = "#b42318"
COR_AZUL = "#315a7d"
COR_CINZA = "#f1f3ea"

CORES_STATUS = {
    "Realizado": "#677526",
    "Confirmado": "#afb512",
    "A Confirmar": "#d8d278",
    "Em Andamento": "#315a7d",
    "Cancelado": "#b42318",
}

MESES_ORDEM = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


# =========================
# CSS CORPORATIVO
# =========================

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: linear-gradient(180deg, #ffffff 0%, {COR_FUNDO} 100%);
            color: {COR_TEXTO};
        }}

        section[data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid {COR_BORDA};
            box-shadow: 8px 0 24px rgba(16,24,40,0.04);
        }}

        section[data-testid="stSidebar"] * {{
            color: {COR_TEXTO};
        }}

        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }}

        .hero {{
            background: linear-gradient(135deg, {COR_PRINCIPAL} 0%, #87923b 55%, {COR_DESTAQUE} 100%);
            border-radius: 28px;
            padding: 30px 34px;
            color: white;
            box-shadow: 0 18px 48px rgba(103,117,38,0.24);
            margin-bottom: 22px;
        }}

        .hero-title {{
            font-size: 34px;
            line-height: 1.1;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: 8px;
        }}

        .hero-subtitle {{
            font-size: 15px;
            opacity: .94;
            margin-bottom: 18px;
        }}

        .hero-chip {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 999px;
            padding: 8px 12px;
            font-size: 13px;
            margin-right: 8px;
            color: white;
        }}

        .kpi-card {{
            background: {COR_CARD};
            border: 1px solid {COR_BORDA};
            border-radius: 22px;
            padding: 20px 20px 18px 20px;
            box-shadow: 0 12px 32px rgba(16,24,40,0.07);
            min-height: 128px;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card:before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, {COR_PRINCIPAL}, {COR_DESTAQUE});
        }}

        .kpi-label {{
            font-size: 13px;
            color: {COR_TEXTO_SUAVE};
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .kpi-value {{
            font-size: 28px;
            color: {COR_TEXTO};
            font-weight: 800;
            letter-spacing: -0.03em;
        }}

        .kpi-note {{
            color: {COR_TEXTO_SUAVE};
            font-size: 12px;
            margin-top: 8px;
        }}

        .section-card {{
            background: {COR_CARD};
            border: 1px solid {COR_BORDA};
            border-radius: 24px;
            padding: 22px;
            box-shadow: 0 12px 32px rgba(16,24,40,0.06);
            margin-bottom: 18px;
        }}

        .section-title {{
            font-size: 21px;
            font-weight: 800;
            color: {COR_TEXTO};
            margin-bottom: 6px;
            letter-spacing: -0.03em;
        }}

        .section-subtitle {{
            color: {COR_TEXTO_SUAVE};
            font-size: 13px;
            margin-bottom: 12px;
        }}

        .sidebar-logo {{
            background: linear-gradient(135deg, {COR_PRINCIPAL}, {COR_DESTAQUE});
            color: white !important;
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 18px;
            box-shadow: 0 12px 28px rgba(103,117,38,.18);
        }}

        .sidebar-logo-title {{
            font-size: 20px;
            font-weight: 800;
            color: white !important;
            margin-bottom: 4px;
        }}

        .sidebar-logo-sub {{
            font-size: 12px;
            color: rgba(255,255,255,.88) !important;
        }}

        div[data-testid="stMetric"] {{
            background: #fff;
            border: 1px solid {COR_BORDA};
            padding: 15px;
            border-radius: 16px;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: #ffffff;
            border: 1px solid {COR_BORDA};
            border-radius: 999px;
            padding: 10px 18px;
            color: {COR_TEXTO};
            font-weight: 700;
        }}

        .stTabs [aria-selected="true"] {{
            background: {COR_PRINCIPAL} !important;
            color: white !important;
            border-color: {COR_PRINCIPAL} !important;
        }}

        .stButton button, .stDownloadButton button {{
            background: {COR_PRINCIPAL};
            color: white;
            border: 0;
            border-radius: 14px;
            padding: 0.65rem 1rem;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(103,117,38,.18);
        }}

        .stButton button:hover, .stDownloadButton button:hover {{
            background: {COR_DESTAQUE};
            color: #202124;
            border: 0;
        }}

        div[data-testid="stFileUploader"] section {{
            background: #ffffff;
            border: 1.5px dashed {COR_PRINCIPAL};
            border-radius: 18px;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid {COR_BORDA};
        }}

        .small-muted {{
            color: {COR_TEXTO_SUAVE};
            font-size: 12px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# FUNÇÕES AUXILIARES
# =========================

def limpar_texto(texto: str) -> str:
    if texto is None:
        return ""
    texto = str(texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def remover_acentos(texto: str) -> str:
    texto = limpar_texto(texto).lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def br_money_to_float(valor) -> float:
    if pd.isna(valor):
        return 0.0
    valor = str(valor).strip()
    valor = re.sub(r"[^0-9,.-]", "", valor)
    if valor.count(",") == 1:
        valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return 0.0


def formatar_moeda(valor) -> str:
    try:
        valor = float(valor)
    except Exception:
        valor = 0.0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor) -> str:
    try:
        return f"{float(valor):.1f}%".replace(".", ",")
    except Exception:
        return "0,0%"


def formatar_numero(valor) -> str:
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return "0"


def corrigir_situacao(situacao: str) -> str:
    s = limpar_texto(situacao)
    s_norm = remover_acentos(s)
    mapa = {
        "cancelado": "Cancelado",
        "realizado": "Realizado",
        "em andamento": "Em Andamento",
        "confirmado": "Confirmado",
        "a confirmar": "A Confirmar",
    }
    return mapa.get(s_norm, s)


def eh_subsequencia(palavra: str, texto: str) -> bool:
    """
    Verifica se as letras de uma palavra aparecem em sequência dentro do texto,
    mesmo com caracteres/ruídos no meio. Ex.: 'Cancelado' dentro de 'ACNaOnc LeTlaDdAo'.
    """
    it = iter(texto)
    return all(letra in it for letra in palavra)


def detectar_situacao_linha(texto_status: str, linha_completa: str = "") -> str:
    """
    Detecta a situação do evento de forma robusta, inclusive quando o PDF mistura
    letras da coluna Situação com a coluna Cliente ou Data.
    """
    texto = remover_acentos(texto_status)
    linha = remover_acentos(linha_completa)

    compacto = re.sub(r"[^a-z]", "", texto)
    compacto_linha = re.sub(r"[^a-z]", "", linha)

    # 1) Detecção direta e por subsequência no campo da situação
    if "cancelado" in texto or eh_subsequencia("cancelado", compacto):
        return "Cancelado"

    if "realizado" in texto or eh_subsequencia("realizado", compacto):
        return "Realizado"

    if "em andamento" in texto or "andamento" in texto or "andamen" in texto or eh_subsequencia("andamento", compacto):
        return "Em Andamento"

    if "a confirmar" in texto or eh_subsequencia("aconfirmar", compacto):
        return "A Confirmar"

    if "confirmado" in texto or eh_subsequencia("confirmado", compacto):
        return "Confirmado"

    # 2) Fallback no texto completo da linha
    if "cancelado" in linha:
        return "Cancelado"

    if "realizado" in linha:
        return "Realizado"

    if "em andamento" in linha or "andamen" in linha:
        return "Em Andamento"

    if "a confirmar" in linha:
        return "A Confirmar"

    if "confirmado" in linha:
        return "Confirmado"

    return "A Confirmar"


def montar_data_por_digitos(texto: str, modo: str = "primeira") -> str | None:
    """
    Monta uma data quando o PDF quebra algo como:
    '(MO24T/O01R/2) 026' -> 24/01/2026
    """
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
    if datas:
        return datas[0] if modo == "primeira" else datas[-1]

    digitos = re.sub(r"\D", "", texto)

    if len(digitos) >= 8:
        bruto = digitos[:8] if modo == "primeira" else digitos[-8:]
        return f"{bruto[:2]}/{bruto[2:4]}/{bruto[4:8]}"

    return None


def montar_data_inicio_fallback(palavras_linha) -> str | None:
    """
    Fallback para linhas em que a data de início vem misturada ao texto do cliente.
    Exemplo real do PDF:
    'REPRESENTAC1A1O/0 L4T/2D0A26' -> 11/04/2026
    'EVENT0O6/S0 4L/T2D02A6' -> 06/04/2026
    """
    trecho = " ".join(
        w["text"] for w in palavras_linha
        if 250 <= w["x0"] < 410
    )

    digitos = re.sub(r"\D", "", trecho)

    if len(digitos) >= 8:
        bruto = digitos[-8:]
        return f"{bruto[:2]}/{bruto[2:4]}/{bruto[4:8]}"

    return None


def detectar_categoria(evento_cliente: str) -> str:
    texto = remover_acentos(evento_cliente)
    regras = [
        ("Casamento / Social", ["casamento", "jantar casamento", "happy hour"]),
        ("Treinamento / Curso", ["curso", "treinamento", "qualifica", "podologia", "reforma tributaria"]),
        ("Corporativo", ["sebrae", "unimed", "honda", "novo", "cartorio", "contabilidade", "negocios", "business", "firma", "cnm", "alvo", "tres coracoes", "pague menos", "cajuina", "pole", "otica"]),
        ("Religioso / Comunidade", ["igreja", "encontro", "associacao", "asa"]),
        ("Orçamento", ["orcamento"]),
    ]
    for categoria, palavras in regras:
        if any(p in texto for p in palavras):
            return categoria
    return "Outros"


def extrair_nome_evento(descricao: str) -> str:
    texto = limpar_texto(descricao)
    marcadores_clientes = [
        " IMPERIAL PALACE HOTEL LTDA",
        " TRES CORACOES",
        " CAJUINA SAO GERALDO",
        " MEVBRASIL",
        " J P LIMA",
        " M M ASSESSORIA",
        " BF COMERCIO",
        " LIVESTORM",
        " N D SALDANHA",
        " T & T COMERCIO",
        " ALVO EVENTOS",
        " ASSOCIACAO",
        " DANYEL ELLYEZER",
        " FRANCISCO AGILYMAR",
        " PARTIDO NOVO",
        " POLE ALIMENTOS",
    ]
    for marcador in marcadores_clientes:
        if marcador in texto:
            return texto.split(marcador)[0].strip()
    return texto[:80].strip()


def extrair_cliente(descricao: str) -> str:
    texto = limpar_texto(descricao)
    marcadores = [
        "IMPERIAL PALACE HOTEL LTDA (MOTOR)",
        "TRES CORACOES ALIMENTOS S.A.",
        "CAJUINA SAO GERALDO LTDA",
        "MEVBRASIL TREINAMENTOS E DESENVOLVIMENTO HUMANO LTDA",
        "J P LIMA ARARIPINA",
        "M M ASSESSORIA A EVENTOS CONGRESSOS E PROMOCOES LTDA",
        "BF COMERCIO E SERVICOS LTDA",
        "LIVESTORM PUBLICIDADE E EVENTOS LTDA",
        "N D SALDANHA MIMO",
        "T & T COMERCIO E REPRESENTACAO LTDA",
        "ALVO EVENTOS LTDA",
        "ASSOCIACAO PROGRAMA UM MILHAO DE CISTERNAS PARA O SEMIARIDO",
        "DANYEL ELLYEZER ARAUJO SILVA",
        "FRANCISCO AGILYMAR DA SILVA MARTINS",
        "PARTIDO NOVO",
        "POLE ALIMENTOS LTDA",
    ]
    for marcador in marcadores:
        if marcador in texto:
            return marcador
    return "Cliente não identificado"


@st.cache_data(show_spinner=False)
def extrair_eventos_pdf_bytes(pdf_bytes: bytes) -> pd.DataFrame:
    """
    Extração robusta do relatório PDF por coordenadas das colunas.
    Esta versão corrige o problema em que o pdfplumber misturava a data de início
    com o texto do cliente, fazendo várias linhas serem ignoradas.
    """
    registros = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for pagina in pdf.pages:
            palavras = pagina.extract_words(
                x_tolerance=1,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=False
            )

            # Agrupa palavras por linha visual, usando a coordenada vertical
            grupos = []
            for palavra in sorted(palavras, key=lambda w: (w["top"], w["x0"])):
                if palavra["top"] < 85:
                    continue

                inserida = False
                for grupo in grupos:
                    if abs(grupo[0] - palavra["top"]) < 2:
                        grupo[1].append(palavra)
                        inserida = True
                        break

                if not inserida:
                    grupos.append([palavra["top"], [palavra]])

            for _, palavras_linha in grupos:
                palavras_linha = sorted(palavras_linha, key=lambda w: w["x0"])

                if not palavras_linha:
                    continue

                primeira = palavras_linha[0]["text"]

                # Só considera linhas que começam com o número do evento
                if not re.match(r"^\d+$", primeira):
                    continue

                try:
                    numero = int(primeira)
                    linha_completa = " ".join(w["text"] for w in palavras_linha)

                    # Colunas por posição horizontal do PDF
                    nome_txt = " ".join(w["text"] for w in palavras_linha if 55 <= w["x0"] < 231)
                    cliente_txt = " ".join(w["text"] for w in palavras_linha if 231 <= w["x0"] < 344)

                    # A data de início geralmente fica quebrada/misturada entre x=344 e x=410
                    inicio_txt = " ".join(w["text"] for w in palavras_linha if 344 <= w["x0"] < 410)

                    # A data de término fica entre x=410 e x=456
                    termino_txt = " ".join(w["text"] for w in palavras_linha if 410 <= w["x0"] < 456)

                    # A situação pode vir corrompida; por isso pegamos uma faixa maior
                    situacao_txt = " ".join(w["text"] for w in palavras_linha if 410 <= w["x0"] < 526)

                    # Total no fim da linha
                    total_txt = " ".join(w["text"] for w in palavras_linha if w["x0"] >= 526)

                    inicio = montar_data_por_digitos(inicio_txt, "primeira")

                    # Fallback para casos em que a data de início vem grudada/misturada no texto do cliente.
                    # Isso corrige eventos como 765 e 776, que antes não eram lidos.
                    if inicio is None:
                        inicio = montar_data_inicio_fallback(palavras_linha)

                    termino = montar_data_por_digitos(termino_txt, "ultima") or inicio

                    if inicio is None:
                        continue

                    situacao = detectar_situacao_linha(situacao_txt, linha_completa)

                    valor_match = re.findall(
                        r"\d{1,3}(?:\.\d{3})*,\d{2}|0,00|\d+,\d{2}",
                        total_txt
                    )
                    total = br_money_to_float(valor_match[-1]) if valor_match else 0.0

                    evento_cliente = limpar_texto(f"{nome_txt} {cliente_txt}")
                    evento = limpar_texto(nome_txt) if nome_txt else extrair_nome_evento(evento_cliente)
                    cliente = limpar_texto(cliente_txt) if cliente_txt else extrair_cliente(evento_cliente)

                    registros.append({
                        "Número": numero,
                        "Evento / Cliente": evento_cliente,
                        "Evento": evento,
                        "Cliente": cliente,
                        "Início": inicio,
                        "Término": termino,
                        "Situação": situacao,
                        "Total": total,
                    })

                except Exception:
                    continue

    df = pd.DataFrame(registros)

    if df.empty:
        return df

    df["Início"] = pd.to_datetime(df["Início"], dayfirst=True, errors="coerce")
    df["Término"] = pd.to_datetime(df["Término"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Início"])

    df["Ano"] = df["Início"].dt.year
    df["Mês Nº"] = df["Início"].dt.month
    df["Mês"] = df["Mês Nº"].map(MESES_ORDEM)
    df["Dia"] = df["Início"].dt.day

    df["Dia da Semana Nº"] = df["Início"].dt.weekday
    df["Dia da Semana"] = df["Dia da Semana Nº"].map({
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    })

    df["Duração (dias)"] = (df["Término"] - df["Início"]).dt.days + 1
    df["Duração (dias)"] = df["Duração (dias)"].clip(lower=1)

    df["Categoria"] = df["Evento / Cliente"].apply(detectar_categoria)

    df["Situação"] = df["Situação"].apply(corrigir_situacao)
    df["É Cancelado"] = df["Situação"].eq("Cancelado")
    df["É Realizado"] = df["Situação"].eq("Realizado")
    df["É Receita Ativa"] = df["Situação"].isin(["Realizado", "Confirmado", "Em Andamento", "A Confirmar"])

    return df.sort_values("Início").reset_index(drop=True)


def aplicar_layout_plotly(fig, altura=420, legenda=True):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COR_TEXTO, family="Inter"),
        height=altura,
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ) if legenda else None,
    )
    fig.update_xaxes(showgrid=False, linecolor=COR_BORDA)
    fig.update_yaxes(gridcolor="#edf0e5", zerolinecolor="#edf0e5")
    return fig


def card_kpi(titulo, valor, nota=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-note">{nota}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(titulo, subtitulo=""):
    st.markdown(
        f"""
        <div class="section-title">{titulo}</div>
        <div class="section-subtitle">{subtitulo}</div>
        """,
        unsafe_allow_html=True,
    )


def gerar_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        base = df.copy()
        for col in ["Início", "Término"]:
            if col in base.columns:
                base[col] = base[col].dt.strftime("%d/%m/%Y")
        base.to_excel(writer, index=False, sheet_name="Base Filtrada")

        resumo_status = df.groupby("Situação", as_index=False).agg(
            Eventos=("Número", "count"), Valor=("Total", "sum")
        )
        resumo_status.to_excel(writer, index=False, sheet_name="Resumo Status")

        resumo_mes = df.groupby(["Mês Nº", "Mês"], as_index=False).agg(
            Eventos=("Número", "count"), Valor=("Total", "sum")
        ).sort_values("Mês Nº")
        resumo_mes.to_excel(writer, index=False, sheet_name="Resumo Mensal")

    return output.getvalue()


# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-title">Verde da Mata</div>
            <div class="sidebar-logo-sub">Dashboard executivo de eventos</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Envie o PDF do relatório para gerar a análise automaticamente.")
    arquivo = st.file_uploader("Relatório em PDF", type=["pdf"], label_visibility="collapsed")

    st.divider()
    st.subheader("Filtros")


# =========================
# ESTADO INICIAL
# =========================

if arquivo is None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Dashboard de Eventos</div>
            <div class="hero-subtitle">Análise automatizada do relatório PDF do Verde da Mata Hotel / Hotel Imperial.</div>
            <span class="hero-chip">📄 Leitura de PDF</span>
            <span class="hero-chip">📊 Dashboard executivo</span>
            <span class="hero-chip">🎛️ Filtros inteligentes</span>
            <span class="hero-chip">📥 Exportação Excel</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        card_kpi("1. Envie o PDF", "Upload", "Use a barra lateral")
    with col_b:
        card_kpi("2. Analise", "Filtros", "Situação, mês, valor e busca")
    with col_c:
        card_kpi("3. Exporte", "Excel", "Base tratada e resumos")

    st.info("Aguardando o envio do relatório em PDF pela barra lateral.")
    st.stop()


pdf_bytes = arquivo.getvalue()
df = extrair_eventos_pdf_bytes(pdf_bytes)

if df.empty:
    st.error("Não consegui extrair os eventos do PDF. Verifique se o relatório está no mesmo padrão da lista de eventos.")
    st.stop()


# =========================
# FILTROS DINÂMICOS
# =========================

with st.sidebar:
    situacoes = sorted(df["Situação"].dropna().unique().tolist())
    meses_df = df[["Mês", "Mês Nº"]].drop_duplicates().sort_values("Mês Nº")
    categorias = sorted(df["Categoria"].dropna().unique().tolist())

    filtro_situacao = st.multiselect("Situação", situacoes, default=situacoes)
    filtro_mes = st.multiselect("Mês", meses_df["Mês"].tolist(), default=meses_df["Mês"].tolist())
    filtro_categoria = st.multiselect("Categoria", categorias, default=categorias)

    min_data = df["Início"].min().date()
    max_data = df["Início"].max().date()
    filtro_datas = st.date_input("Período", value=(min_data, max_data), min_value=min_data, max_value=max_data)

    valor_min = float(df["Total"].min())
    valor_max = float(df["Total"].max())
    if valor_min == valor_max:
        valor_max = valor_min + 1
    filtro_valor = st.slider("Faixa de valor", valor_min, valor_max, (valor_min, valor_max))

    busca = st.text_input("Buscar evento / cliente", placeholder="Digite parte do nome...")

    considerar_cancelados = st.toggle("Incluir cancelados na receita total", value=True)

    st.divider()
    st.caption(f"Arquivo carregado: {arquivo.name}")
    st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    with st.expander("Conferência da leitura"):
        st.write("Total de linhas extraídas:", len(df))
        st.write(df["Situação"].value_counts())


if isinstance(filtro_datas, tuple) and len(filtro_datas) == 2:
    data_ini, data_fim = filtro_datas
else:
    data_ini, data_fim = min_data, max_data

mask = (
    df["Situação"].isin(filtro_situacao)
    & df["Mês"].isin(filtro_mes)
    & df["Categoria"].isin(filtro_categoria)
    & (df["Início"].dt.date >= data_ini)
    & (df["Início"].dt.date <= data_fim)
    & (df["Total"] >= filtro_valor[0])
    & (df["Total"] <= filtro_valor[1])
)

df_filtrado = df.loc[mask].copy()

if busca:
    termo = remover_acentos(busca)
    df_filtrado = df_filtrado[
        df_filtrado["Evento / Cliente"].apply(lambda x: termo in remover_acentos(x))
        | df_filtrado["Cliente"].apply(lambda x: termo in remover_acentos(x))
        | df_filtrado["Evento"].apply(lambda x: termo in remover_acentos(x))
    ].copy()


# =========================
# CABEÇALHO
# =========================

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">Dashboard de Eventos</div>
        <div class="hero-subtitle">Verde da Mata Hotel | Análise executiva automatizada a partir do relatório PDF</div>
        <span class="hero-chip">📌 {len(df_filtrado)} eventos filtrados</span>
        <span class="hero-chip">📅 {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</span>
        <span class="hero-chip">💼 {df_filtrado['Cliente'].nunique() if not df_filtrado.empty else 0} clientes</span>
    </div>
    """,
    unsafe_allow_html=True,
)


if df_filtrado.empty:
    st.warning("Nenhum evento encontrado com os filtros selecionados.")
    st.stop()


# =========================
# KPIs (CORRIGIDO + EXECUTIVO)
# =========================

# 🔹 BASE FILTRADA
base_receita = df_filtrado if considerar_cancelados else df_filtrado[df_filtrado["É Receita Ativa"]]

total_eventos = len(df_filtrado)
valor_total = base_receita["Total"].sum()
valor_realizado = df_filtrado.loc[df_filtrado["Situação"].eq("Realizado"), "Total"].sum()
valor_cancelado_filtrado = df_filtrado.loc[df_filtrado["Situação"].eq("Cancelado"), "Total"].sum()
ticket_medio = base_receita["Total"].mean() if len(base_receita) else 0
cancelados_filtrado = int(df_filtrado["É Cancelado"].sum())
taxa_cancelamento_filtrado = cancelados_filtrado / total_eventos * 100 if total_eventos else 0
maior_evento = df_filtrado["Total"].max() if total_eventos else 0

# 🔴 BASE TOTAL (SEM FILTRO)
cancelados_total = int(df["É Cancelado"].sum())
total_eventos_total = len(df)
valor_cancelado_total = df.loc[df["Situação"].eq("Cancelado"), "Total"].sum()

taxa_cancelamento_total = cancelados_total / total_eventos_total * 100 if total_eventos_total else 0

# 💸 IMPACTO FINANCEIRO REAL
valor_total_geral = df["Total"].sum()
impacto_cancelamento = (valor_cancelado_total / valor_total_geral * 100) if valor_total_geral else 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    card_kpi("Total de Eventos", formatar_numero(total_eventos), "Filtro aplicado")
with col2:
    card_kpi("Valor Total", formatar_moeda(valor_total), "Base filtrada")
with col3:
    card_kpi("Realizado", formatar_moeda(valor_realizado), "Receita realizada")
with col4:
    card_kpi("Cancelamentos (TOTAL)", formatar_percentual(taxa_cancelamento_total), f"{cancelados_total} evento(s)")
with col5:
    card_kpi("Impacto Cancelamento", formatar_percentual(impacto_cancelamento), f"{formatar_moeda(valor_cancelado_total)}")

st.write("")


# =========================
# ABAS
# =========================

tab_visao, tab_financeiro, tab_eventos, tab_agenda, tab_base = st.tabs([
    "Visão Geral", "Financeiro", "Eventos e Clientes", "Agenda", "Base de Dados"
])


# =========================
# ABA 1 - VISÃO GERAL
# =========================

with tab_visao:
    col_a, col_b = st.columns([1.15, 0.85])

    with col_a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Valor por Situação", "Total financeiro agrupado por status do evento.")
        resumo_status = df_filtrado.groupby("Situação", as_index=False).agg(
            Valor=("Total", "sum"), Eventos=("Número", "count")
        ).sort_values("Valor", ascending=False)
        fig = px.bar(
            resumo_status,
            x="Situação",
            y="Valor",
            text=resumo_status["Valor"].apply(formatar_moeda),
            color="Situação",
            color_discrete_map=CORES_STATUS,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig = aplicar_layout_plotly(fig, altura=430, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Distribuição dos Eventos", "Participação por quantidade de eventos.")
        qtd_status = df_filtrado["Situação"].value_counts().reset_index()
        qtd_status.columns = ["Situação", "Quantidade"]
        fig = px.pie(
            qtd_status,
            names="Situação",
            values="Quantidade",
            hole=0.58,
            color="Situação",
            color_discrete_map=CORES_STATUS,
        )
        fig.update_traces(textinfo="percent+label")
        fig = aplicar_layout_plotly(fig, altura=430, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_c, col_d = st.columns([1, 1])
    with col_c:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Evolução Mensal", "Valor total por mês de início do evento.")
        mensal = df_filtrado.groupby(["Mês Nº", "Mês"], as_index=False).agg(
            Valor=("Total", "sum"), Eventos=("Número", "count")
        ).sort_values("Mês Nº")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mensal["Mês"], y=mensal["Valor"], mode="lines+markers+text",
            text=mensal["Valor"].apply(lambda v: f"{v/1000:.1f}k".replace(".", ",")),
            textposition="top center", line=dict(color=COR_PRINCIPAL, width=4),
            marker=dict(size=11, color=COR_DESTAQUE, line=dict(color=COR_PRINCIPAL, width=2)),
            name="Valor"
        ))
        fig = aplicar_layout_plotly(fig, altura=410, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Categorias de Eventos", "Classificação automática pelo nome do evento/cliente.")
        categorias_resumo = df_filtrado.groupby("Categoria", as_index=False).agg(
            Valor=("Total", "sum"), Eventos=("Número", "count")
        ).sort_values("Valor", ascending=True)
        fig = px.bar(
            categorias_resumo,
            x="Valor",
            y="Categoria",
            orientation="h",
            text=categorias_resumo["Valor"].apply(formatar_moeda),
            color_discrete_sequence=[COR_PRINCIPAL],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig = aplicar_layout_plotly(fig, altura=410, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# ABA 2 - FINANCEIRO
# =========================

with tab_financeiro:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Ticket médio", formatar_moeda(ticket_medio))
    with col_b:
        st.metric("Valor cancelado", formatar_moeda(valor_cancelado_filtrado))
    with col_c:
        conversao = 100 - taxa_cancelamento_filtrado
        st.metric("Taxa de não cancelamento", formatar_percentual(conversao))

    col_f1, col_f2 = st.columns([1.2, 0.8])

    with col_f1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Receita Ativa x Valor Cancelado", "Comparação entre valores ativos e perdas por cancelamento.")
        receita_ativa = df_filtrado.loc[df_filtrado["É Receita Ativa"], "Total"].sum()
        comp = pd.DataFrame({
            "Grupo": ["Receita Ativa", "Valor Cancelado"],
            "Valor": [receita_ativa, valor_cancelado_filtrado]
        })
        fig = px.bar(
            comp,
            x="Grupo",
            y="Valor",
            text=comp["Valor"].apply(formatar_moeda),
            color="Grupo",
            color_discrete_map={"Receita Ativa": COR_PRINCIPAL, "Valor Cancelado": COR_ALERTA}
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig = aplicar_layout_plotly(fig, altura=420, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_f2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Ranking Mensal", "Melhores meses por valor total.")
        ranking_mes = df_filtrado.groupby(["Mês Nº", "Mês"], as_index=False).agg(
            Valor=("Total", "sum"), Eventos=("Número", "count")
        ).sort_values("Valor", ascending=False)
        st.dataframe(
            ranking_mes[["Mês", "Eventos", "Valor"]].assign(Valor=lambda x: x["Valor"].apply(formatar_moeda)),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Curva Acumulada", "Soma acumulada dos valores ao longo do calendário.")
    diario = df_filtrado.groupby("Início", as_index=False).agg(Valor=("Total", "sum")).sort_values("Início")
    diario["Acumulado"] = diario["Valor"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=diario["Início"], y=diario["Acumulado"], mode="lines",
        fill="tozeroy", line=dict(color=COR_PRINCIPAL, width=4), name="Acumulado"
    ))
    fig = aplicar_layout_plotly(fig, altura=420, legenda=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# ABA 3 - EVENTOS E CLIENTES
# =========================

with tab_eventos:
    col_e1, col_e2 = st.columns([1, 1])

    with col_e1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Top 10 Eventos", "Maiores eventos por valor.")
        top_eventos = df_filtrado.nlargest(10, "Total").sort_values("Total", ascending=True)
        fig = px.bar(
            top_eventos,
            x="Total",
            y="Evento",
            orientation="h",
            text=top_eventos["Total"].apply(formatar_moeda),
            color_discrete_sequence=[COR_PRINCIPAL],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig = aplicar_layout_plotly(fig, altura=520, legenda=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_e2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Top Clientes", "Clientes com maior valor acumulado.")
        top_clientes = df_filtrado.groupby("Cliente", as_index=False).agg(
            Valor=("Total", "sum"), Eventos=("Número", "count")
        ).sort_values("Valor", ascending=False).head(10)
        st.dataframe(
            top_clientes.assign(Valor=lambda x: x["Valor"].apply(formatar_moeda)),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Eventos por Dia da Semana", "Ajuda a identificar maior concentração operacional.")
    semana = df_filtrado.groupby(["Dia da Semana Nº", "Dia da Semana"], as_index=False).agg(
        Eventos=("Número", "count"), Valor=("Total", "sum")
    ).sort_values("Dia da Semana Nº")
    fig = px.bar(
        semana,
        x="Dia da Semana",
        y="Eventos",
        text="Eventos",
        color_discrete_sequence=[COR_DESTAQUE],
        hover_data={"Valor": ":,.2f"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig = aplicar_layout_plotly(fig, altura=420, legenda=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# ABA 4 - AGENDA
# =========================

with tab_agenda:
    col_ag1, col_ag2 = st.columns([1.1, 0.9])

    with col_ag1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Agenda Mensal", "Quantidade de eventos por mês e situação.")
        agenda = df_filtrado.groupby(["Mês Nº", "Mês", "Situação"], as_index=False).agg(Eventos=("Número", "count"))
        agenda = agenda.sort_values("Mês Nº")
        fig = px.bar(
            agenda,
            x="Mês",
            y="Eventos",
            color="Situação",
            text="Eventos",
            color_discrete_map=CORES_STATUS,
            barmode="stack",
        )
        fig = aplicar_layout_plotly(fig, altura=460, legenda=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ag2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section_header("Próximos Eventos", "Lista ordenada por data de início.")
        hoje = pd.Timestamp.today().normalize()
        proximos = df_filtrado[df_filtrado["Início"] >= hoje].sort_values("Início").head(12)
        if proximos.empty:
            proximos = df_filtrado.sort_values("Início").tail(12)
        exibir = proximos[["Início", "Evento", "Situação", "Total"]].copy()
        exibir["Início"] = exibir["Início"].dt.strftime("%d/%m/%Y")
        exibir["Total"] = exibir["Total"].apply(formatar_moeda)
        st.dataframe(exibir, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Mapa de Concentração", "Volume de eventos por dia do mês.")
    heat = df_filtrado.groupby(["Mês Nº", "Mês", "Dia"], as_index=False).agg(Eventos=("Número", "count"))
    pivot = heat.pivot_table(index="Mês", columns="Dia", values="Eventos", fill_value=0)
    ordem_meses = [MESES_ORDEM[i] for i in range(1, 13) if MESES_ORDEM[i] in pivot.index]
    pivot = pivot.reindex(ordem_meses)
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=[[0, "#f4f5ee"], [0.5, COR_DESTAQUE], [1, COR_PRINCIPAL]],
        labels=dict(x="Dia", y="Mês", color="Eventos"),
    )
    fig = aplicar_layout_plotly(fig, altura=420, legenda=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# ABA 5 - BASE DE DADOS
# =========================

with tab_base:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header("Base tratada", "Dados extraídos do PDF e enriquecidos automaticamente.")
    base = df_filtrado.copy()
    base["Início"] = base["Início"].dt.strftime("%d/%m/%Y")
    base["Término"] = base["Término"].dt.strftime("%d/%m/%Y")
    base["Total Formatado"] = base["Total"].apply(formatar_moeda)

    colunas_exibir = [
        "Número", "Evento", "Cliente", "Início", "Término", "Mês", "Dia da Semana",
        "Categoria", "Situação", "Duração (dias)", "Total Formatado"
    ]
    st.dataframe(base[colunas_exibir], use_container_width=True, hide_index=True)

    col_dl1, col_dl2 = st.columns([0.25, 0.75])
    with col_dl1:
        st.download_button(
            "Baixar Excel",
            data=gerar_excel(df_filtrado),
            file_name="dashboard_eventos_verde_da_mata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_dl2:
        csv = df_filtrado.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            "Baixar CSV",
            data=csv,
            file_name="eventos_filtrados.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# RODAPÉ
# =========================

st.caption("Dashboard desenvolvido em Python, Streamlit, Pandas, Plotly e PDFPlumber. Layout claro com identidade visual baseada nas cores #677526 e #afb512.")
