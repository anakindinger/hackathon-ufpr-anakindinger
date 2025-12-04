import pandas as pd
import os
import glob

# Configuração
pd.options.mode.chained_assignment = None

def carregar_csv_robusto(caminho_arquivo):
    """
    Tenta ler o CSV detectando automaticamente o separador e ignorando linhas ruins.
    """
    separadores = [',', ';', '\t']
    encodings = ['utf-8', 'latin1', 'cp1252']
    
    for enc in encodings:
        for sep in separadores:
            try:
                # Ler apenas a primeira linha para validar colunas rapidamente
                df_teste = pd.read_csv(caminho_arquivo, encoding=enc, sep=sep, nrows=2)
                if len(df_teste.columns) > 1: # Se separou em mais de 1 coluna, parece certo
                    print(f"   -> Lendo {os.path.basename(caminho_arquivo)} com {enc} e separador '{sep}'")
                    return pd.read_csv(caminho_arquivo, encoding=enc, sep=sep, low_memory=False)
            except:
                continue
    return pd.DataFrame() # Retorna vazio se falhar tudo

def calcular_sentimento(resposta_texto):
    if not isinstance(resposta_texto, str):
        return None
    texto = resposta_texto.lower().strip()
    if 'concordo' in texto: return 1.0
    if 'discordo' in texto: return -1.0
    if 'indiferente' in texto: return 0.0
    return None

def padronizar_colunas(df, origem):
    """
    Renomeia colunas para um padrão único, independente do arquivo.
    """
    # Converter colunas para maiúsculas para evitar erros de Case Sensitive
    df.columns = [c.upper().strip() for c in df.columns]
    
    # Unificar nome da categoria (QUESTIONARIO ou TITULO viram CATEGORIA)
    if 'TITULO' in df.columns:
        df.rename(columns={'TITULO': 'CATEGORIA'}, inplace=True)
    elif 'QUESTIONARIO' in df.columns:
        df.rename(columns={'QUESTIONARIO': 'CATEGORIA'}, inplace=True)
    else:
        df['CATEGORIA'] = 'Geral' # Fallback se não achar
        
    # Unificar Unidade de Análise (CURSO ou LOTACAO)
    if 'LOTACAO' in df.columns:
        df.rename(columns={'LOTACAO': 'UNIDADE_ANALISE'}, inplace=True)
    elif 'CURSO' in df.columns:
        df.rename(columns={'CURSO': 'UNIDADE_ANALISE'}, inplace=True)
    else:
        df['UNIDADE_ANALISE'] = 'Desconhecido'

    # Unificar Contexto (Disciplina ou Setor)
    if 'NOME_DISCIPLINA' in df.columns:
        df.rename(columns={'NOME_DISCIPLINA': 'CONTEXTO'}, inplace=True)
    else:
        df['CONTEXTO'] = df['UNIDADE_ANALISE'] # Se não for disciplina, o contexto é a própria unidade
        
    # Garantir colunas essenciais
    if 'SETOR_CURSO' not in df.columns:
        df['SETOR_CURSO'] = 'Institucional'
        
    df['ORIGEM'] = origem
    
    # Selecionar apenas o necessário
    colunas_finais = ['ORIGEM', 'SETOR_CURSO', 'UNIDADE_ANALISE', 'CONTEXTO', 'CATEGORIA', 'PERGUNTA', 'RESPOSTA']
    
    # Verifica se todas existem, senão cria vazia para não dar erro
    for col in colunas_finais:
        if col not in df.columns:
            df[col] = None
            
    return df[colunas_finais]

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
print("🚀 Iniciando processamento v2 (Correção de Colunas)...")

dfs_consolidados = []

# Mapeamento: Arquivo de DADOS -> Nome da Origem
# (Nota: Não precisamos ler o arquivo de Perguntas separadamente se a pergunta já estiver na tabela principal ou se usarmos o ID para merge. 
# Simplificação: Usaremos os arquivos que contêm as RESPOSTAS. Geralmente eles já têm a pergunta ou o ID ligado.)

arquivos_mapa = {
    "DadosAvDisciplinasEAD_1S2025.xlsx - PESQ423_DISCIP.csv": "Disciplina EAD",
    "DadosAvDisciplinasPresenciais_1S2025.xlsx - DadosAvDisciplinas.csv": "Disciplina Presencial",
    "DadosAv_Cursos_2024.xlsx - DadosAvCursos.csv": "Cursos",
    "DadosAvInstitucional_2025.xlsx - PESQUISA 442.csv": "Institucional"
}

for nome_arquivo, origem_nome in arquivos_mapa.items():
    if os.path.exists(nome_arquivo):
        print(f"📂 Processando: {origem_nome}...")
        df_temp = carregar_csv_robusto(nome_arquivo)
        
        if not df_temp.empty:
            # Etapa de padronização
            df_padrao = padronizar_colunas(df_temp, origem_nome)
            dfs_consolidados.append(df_padrao)
        else:
            print(f"⚠️ Arquivo vazio ou ilegível: {nome_arquivo}")
    else:
        print(f"❌ Arquivo não encontrado: {nome_arquivo}")

# ==============================================================================
# FINALIZAÇÃO
# ==============================================================================
if dfs_consolidados:
    print("🔗 Unificando tudo...")
    df_final = pd.concat(dfs_consolidados, ignore_index=True)
    
    print("🧮 Calculando Sentimento...")
    df_final['PONTUACAO'] = df_final['RESPOSTA'].apply(calcular_sentimento)
    
    # Limpeza final
    df_final.dropna(subset=['RESPOSTA'], inplace=True)
    
    arquivo_saida = "base_consolidada_v2.csv"
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ SUCESSO! Base gerada: {arquivo_saida}")
    print(f"📊 Linhas totais: {len(df_final)}")
    print("Colunas disponíveis:", list(df_final.columns))
else:
    print("❌ Nenhum dado foi processado. Verifique se os arquivos estão na pasta.")