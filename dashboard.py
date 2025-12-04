import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração de Cores (Paleta Vibrante) ---
COR_DESTAQUE = '#4B0082'  # Indigo escuro/roxo
COR_SECUNDARIA = '#008080' # Teal (Verde-azulado)
BRANCO = 'white'
PRETO = 'black'

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Avaliação Institucional (Otimizado)", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Função de Carregamento e Mapeamento (AGORA SEM PONTUAÇÃO NA LEGENDA) ---
@st.cache_data
def load_consolidated_data(file_path):
    """Carrega o arquivo CSV consolidado e mapeia a pontuação para texto (Insatisfeito a Satisfeito) de forma simplificada."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df_valid = df.dropna(subset=['PONTUACAO']).copy()
        df_valid['PONTUACAO'] = df_valid['PONTUACAO'].astype(int)
        
        # Mapeamento para Legenda SIMPLIFICADA
        mapa_legenda = {
            1: 'Satisfeito',
            0: 'Neutro',
            -1: 'Insatisfeito'
        }
        df_valid['SENTIMENTO_TEXTO'] = df_valid['PONTUACAO'].map(mapa_legenda)
        
        return df_valid
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{file_path}' não encontrado. Certifique-se de ter rodado o script 'processar_dados.py' primeiro.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o arquivo: {e}")
        return pd.DataFrame()

# Carregando a base de dados
DATA_FILE = "base_consolidada_v2.csv"
df_main = load_consolidated_data(DATA_FILE)

# --- Título e Estrutura Principal ---
st.title("📊 Painel Institucional: Análise de Avaliações")
st.markdown("Análise comparativa das avaliações de Disciplinas (EAD/Presencial), Cursos e Institucional.")

if df_main.empty:
    st.stop()

# -------------------------------------------------------------
# SIDEBAR: FILTRO DE NÍVEL SUPERIOR (Origem)
# -------------------------------------------------------------
st.sidebar.header("⚙️ Filtro Principal")

# Filtro de Origem (Mantido na Sidebar)
origem_selecionada = st.sidebar.multiselect(
    "Origem dos dados:",
    options=df_main['ORIGEM'].unique(),
    default=df_main['ORIGEM'].unique()
)

df_filtered = df_main[df_main['ORIGEM'].isin(origem_selecionada)]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros de Origem selecionados.")
    st.stop()


# --- FUNÇÕES DE VISUALIZAÇÃO ---

def plot_gauge_score(df, title="Índice médio de satisfação"):
    """Cria o termômetro com cores fortes."""
    avg_score = df['PONTUACAO'].mean()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_score,
        number={'valueformat':'.2f', 'suffix': ' ', 'font': {'color': COR_DESTAQUE}},
        title = {'text': title, 'font': {'color': COR_DESTAQUE}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': COR_DESTAQUE},
            'bar': {'color': COR_SECUNDARIA}, # Barra de destaque
            # Zonas de sentimento com cores fortes
            'steps': [
                {'range': [-1, -0.3], 'color': "red"},
                {'range': [-0.3, 0.3], 'color': "yellow"},
                {'range': [0.3, 1], 'color': "green"}],
            'threshold' : {'line': {'color': PRETO, 'width': 4}, 'thickness': 0.75, 'value': avg_score}}
    ))
    fig.update_layout(height=250, margin=dict(t=50, b=0, l=0, r=0), font_color=PRETO)
    return fig

def plot_heatmap_setor_categoria(df):
    """Cria um Mapa de Calor usando a escala Vermelho/Amarelo/Verde para clareza do sentimento."""
    df_pivot = df.groupby(['SETOR_CURSO', 'CATEGORIA'])['PONTUACAO'].mean().reset_index()
    df_pivot = df_pivot.pivot(index='SETOR_CURSO', columns='CATEGORIA', values='PONTUACAO')
    
    fig = px.imshow(
        df_pivot,
        text_auto=".2f",
        aspect="auto",
        # RdYlGn é a escala padrão para satisfação (Insatisfeito -> Satisfeito)
        color_continuous_scale=px.colors.diverging.RdYlGn, 
        zmin=-1, 
        zmax=1,
        title="Mapa de calor: média de satisfação (Setor vs. Categoria)",
        labels={'color': 'Pontuação Média', 'x': 'Categorias (Temas)', 'y': 'Setores / Unidades'}
    )
    fig.update_layout(height=600, font_color=PRETO,
                      xaxis_title="Categorias (Temas)", yaxis_title="Setores / Unidades")
    fig.update_xaxes(side="top")
    return fig

def plot_sunburst_hierarchy(df):
    """Cria o gráfico Sunburst. A cor representa a média de satisfação."""
    df_agg = df.groupby(['ORIGEM', 'SETOR_CURSO', 'UNIDADE_ANALISE']).agg(
        Média_Satisfacao=('PONTUACAO', 'mean'),
        Total_Respostas=('PONTUACAO', 'size')
    ).reset_index()
    
    fig = px.sunburst(
        df_agg,
        path=['ORIGEM', 'SETOR_CURSO', 'UNIDADE_ANALISE'],
        values='Total_Respostas',
        color='Média_Satisfacao',
        color_continuous_scale=px.colors.diverging.RdYlGn,
        range_color=[-1, 1],
        title="Hierarquia de avaliação: Satisfação por origem, setor e unidade"
    )
    fig.update_layout(height=650, margin=dict(t=50, b=10, l=10, r=10), font_color=PRETO)
    return fig

def plot_sentiment_bar(df):
    """Mostra a distribuição exata das respostas: Satisfeito, Neutro, Insatisfeito."""
    df_sentiment = df.groupby('SENTIMENTO_TEXTO')['PONTUACAO'].count().reset_index(name='Total')
    
    # Ordem e cores para as legendas SIMPLIFICADAS
    order = ['Satisfeito', 'Neutro', 'Insatisfeito']
    color_map = {'Satisfeito': 'green', 'Neutro': 'gold', 'Insatisfeito': 'red'}
    
    df_sentiment['SENTIMENTO_TEXTO'] = pd.Categorical(df_sentiment['SENTIMENTO_TEXTO'], categories=order, ordered=True)
    df_sentiment = df_sentiment.sort_values('SENTIMENTO_TEXTO')
    
    fig = px.bar(
        df_sentiment,
        x='SENTIMENTO_TEXTO',
        y='Total',
        color='SENTIMENTO_TEXTO',
        color_discrete_map=color_map,
        title="Distribuição das respostas por sentimento",
        labels={'SENTIMENTO_TEXTO': 'Sentimento', 'Total': 'Contagem de respostas'}
    )
    fig.update_layout(font_color=PRETO, xaxis_title="Sentimento", yaxis_title="Contagem")
    fig.update_xaxes(showgrid=False)
    return fig


# --- LAYOUT DO DASHBOARD (Em 3 Linhas de KPI) ---

st.header("Resumo da avaliação institucional")

# Linha 1: Satisfação Média Geral (Termômetro)
st.subheader("🎯 Satisfação média geral")
col_gauge, col_spacer = st.columns([1, 4]) 

with col_gauge:
    st.plotly_chart(plot_gauge_score(df_filtered), use_container_width=True)

st.markdown("---")


# Linha 2: Volume de Dados e Média por Origem
st.subheader("📈 Volume de dados e comparativo por origem")
col_volume, col_bar = st.columns([1, 4])

with col_volume:
    total_respostas = df_filtered.shape[0]
    st.metric(label="Total de respostas", value=f"{total_respostas:,}".replace(',', '.'))
    st.markdown(f"**Origens incluídas:** {', '.join(origem_selecionada)}")

with col_bar:
    df_origem_agg = df_filtered.groupby('ORIGEM')['PONTUACAO'].mean().sort_values(ascending=False).reset_index()
    fig_bar = px.bar(
        df_origem_agg, 
        x='ORIGEM', 
        y='PONTUACAO', 
        color_discrete_sequence=[COR_SECUNDARIA],
        title="Pontuação média por origem"
    )
    fig_bar.update_layout(font_color=PRETO, xaxis_title="", yaxis_title="Pontuação média", height=300, margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")


# Linha 3: Distribuição de Sentimento (Legendas Claras)
st.subheader("🔍 Distribuição detalhada do sentimento")
col_sentiment, col_spacer2 = st.columns([3, 2])

with col_sentiment:
    st.plotly_chart(plot_sentiment_bar(df_filtered), use_container_width=True)


st.markdown("---")

# -------------------------------------------------------------
# Quarta Seção: MAPA DE CALOR + FILTROS DE DETALHE
# -------------------------------------------------------------
st.subheader("🔥 Mapa de calor: identificação rápida de pontos críticos")

# Filtros de detalhe (Setor e Categoria) MOVIDOS para perto do Mapa de Calor
col_filtros_mapa, col_grafico_mapa = st.columns([1, 4])

with col_filtros_mapa:
    st.markdown("Ajuste de visualização")
    
    # Filtro de Setor
    setor_selecionado = st.multiselect(
        "Setor:",
        options=df_filtered['SETOR_CURSO'].unique(),
        default=df_filtered['SETOR_CURSO'].unique()
    )
    
    # Filtro de Categoria
    categoria_selecionada = st.multiselect(
        "Categoria (Tema):",
        options=df_filtered['CATEGORIA'].unique(),
        default=df_filtered['CATEGORIA'].unique()
    )

df_filtered_mapa = df_filtered[
    df_filtered['SETOR_CURSO'].isin(setor_selecionado) & 
    df_filtered['CATEGORIA'].isin(categoria_selecionada)
]

with col_grafico_mapa:
    if not df_filtered_mapa.empty:
        st.markdown("Cores em **vermelho** indicam **Insatisfeito**, e **verde** indicam **Satisfeito**.")
        st.plotly_chart(plot_heatmap_setor_categoria(df_filtered_mapa), use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para o Mapa de Calor com os filtros de Setor/Categoria selecionados.")

st.markdown("---")

# -------------------------------------------------------------
# Quinta Seção: HIERARQUIA + DETALHES
# -------------------------------------------------------------
st.subheader("🌳 Hierarquia e volume de participação")

# Estrutura de colunas para colocar detalhes ao lado da Hierarquia
col_hier_1, col_hier_2 = st.columns([2, 1])

with col_hier_1:
    if not df_filtered.empty:
        st.plotly_chart(plot_sunburst_hierarchy(df_filtered), use_container_width=True)
    else:
        st.warning("Sem dados para o Sunburst.")

with col_hier_2:
    st.markdown(f'<p> Mais detalhes do gráfico</p>', unsafe_allow_html=True)
    st.info("Clique nas fatias para filtrar o gráfico! A cor varia de **Insatisfeito (vermelho)** a **Satisfeito (verde)**, e o tamanho da fatia mostra o volume de respostas.")
    
    st.markdown(f'<p> Top 5 unidades/cursos por satisfação</p>', unsafe_allow_html=True)
    if not df_filtered.empty:
        df_ranking = df_filtered.groupby('UNIDADE_ANALISE')['PONTUACAO'].mean().sort_values(ascending=False).head(5).reset_index()
        df_ranking.columns = ['Unidade', 'Média']
        st.dataframe(df_ranking, hide_index=True, use_container_width=True)
    else:
        st.info("Sem dados para ranking.")

st.markdown("---")

# Sexta Seção: Dados Brutos
with st.expander("🔍 Ver tabela de dados brutos filtrados"):
    st.dataframe(df_filtered)

# --- FIM DO DASHBOARD ---
