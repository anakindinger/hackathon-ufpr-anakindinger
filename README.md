
# 📊 Dashboard de Avaliação Institucional e de Cursos (UFPR)



Este repositório contém o código-fonte de um dashboard interativo construído com **Python** e **Streamlit** para visualização e análise dos dados de Avaliação Institucional, de Cursos e de Disciplinas (EAD/Presencial).



O objetivo é fornecer uma visão rápida do **índice de satisfação** (Sentimento: Insatisfeito a Satisfeito) por diferentes níveis hierárquicos (Origem, Setor, Categoria/Tema e Unidade de Análise).


------


## 🚀 Como Rodar o Dashboard Localmente



Siga os passos abaixo para configurar e executar o dashboard em seu ambiente local.Siga os passos abaixo para configurar e executar o dashboard em seu ambiente local.



### 1. Pré-requisitos


Certifique-se de ter o **Python (3.7+)** instalado em sua máquina.Certifique-se de ter o **Python (3.7+)** instalado em sua máquina.



### 2. Estrutura de Arquivos### 2. Estrutura de Arquivos



Para a execução correta, os seguintes arquivos devem estar na mesma pasta:



* `README.md` (Este arquivo)

* `dashboard.py` (O script principal do Streamlit)

* `base_consolidada_v2.csv` (O arquivo de dados final consolidado)

* `etl.py` (O script para consolidação dos dados brutos - *necessário se o CSV consolidado não estiver pronto*)* 

* **Arquivos de dados brutos** (Os arquivos `.csv` originais das avaliações, se você precisar rodar o `etl.py`)



### 3. Instalação de Dependências


Crie um ambiente virtual (recomendado) e instale as bibliotecas necessárias.Crie um ambiente virtual (recomendado) e instale as bibliotecas necessárias.



```bash

# 1. Crie um ambiente virtual (opcional, mas boa prática)# 1. Crie um ambiente virtual (opcional, mas boa prática)

python -m venv venv

source venv/bin/activate  # No Linux/macOSsource venv/bin/activate
# ou

.\venv\Scripts\activate  # No Windows



# 2. Instale as bibliotecas necessárias: Streamlit, Pandas e Plotly.# 2. Instale as bibliotecas necessárias: Streamlit, Pandas e Plotly.

pip install streamlit pandas plotlypip install streamlit pandas plotly

# ou instale usando o arquivo requirements

pip install -r requirements.txt

```



### 4. Preparação dos Dados (Se necessário)### 4. Preparação dos Dados (Se necessário)



Se o arquivo `base_consolidada_v2.csv` ainda não estiver pronto, execute o script de processamento. Este script fará a limpeza, o mapeamento de pontuações e a consolidação dos dados brutos.


```bash

# Se você precisa gerar o arquivo base_consolidada_v2.csv:

python etl.py

```



### 5. Execução do Dashboard



Com as dependências instaladas e o arquivo de dados `base_consolidada_v2.csv` presente, inicie o dashboard:



```bash

streamlit run dashboard.py

```
Com as dependências instaladas e o arquivo de dados base_consolidada_v2.csv presente, inicie o dashboard:

Seu navegador web abrirá automaticamente o dashboard na porta padrão (http://localhost:8501).



### 🎯 KPIs de Resumo

O painel está organizado em seções lógicas com uma paleta de cores vibrante e de alto contraste (conforme solicitado no desenvolvimento).

Os indicadores-chave são apresentados em três linhas verticais para maximizar a visibilidade:

### 🎯 KPIs de Resumo

* **Satisfação Média Geral**: Termômetro (Gauge) com a pontuação média de -1 (Insatisfeito) a +1 (Satisfeito).Os indicadores-chave são apresentados em três linhas verticais para maximizar a visibilidade:



* **Volume e Média por Origem**: Total de respostas e gráfico de barras comparando a média de satisfação por Origem (Disciplina Presencial, Curso, etc.).


* **Distribuição do Sentimento**: Gráfico de barras que quantifica o número de respostas em Insatisfeito, Neutro ou Satisfeito.


### 🔥 Mapa de Calor: Identificação Rápida


* Cruza Setores/Unidades e Categorias/Temas de avaliação.



* Cores fortes (vermelho a verde) destacam as áreas críticas (baixa satisfação) e de excelência (alta satisfação).


### 🌳 Hierarquia e Volume de Participação


* Gráfico Sunburst interativo que mostra a distribuição das respostas em camadas hierárquicas.



* O tamanho da fatia representa o volume de respostas.



* A cor da fatia representa a pontuação média de satisfação daquele item.


## 🛠️ Tecnologias Utilizadas



* Python

* Streamlit (v1.x)

* Pandas

* Plotly

