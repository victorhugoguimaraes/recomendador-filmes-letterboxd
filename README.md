# 🎬 Recomendador de Filmes — Letterboxd

Sistema de recomendação de filmes construído com dados do Letterboxd, combinando filtragem baseada em conteúdo e score de qualidade para gerar recomendações precisas e relevantes.

## Demo

👉 [Acesse o app aqui](https://share.streamlit.io)

---

## Como funciona

O sistema utiliza uma abordagem híbrida com três componentes:

**1. TF-IDF (Term Frequency-Inverse Document Frequency)**
Cada filme é representado por um vetor numérico construído a partir de gênero, tema e diretor. Palavras mais específicas e raras recebem maior peso — um gênero como "Film-Noir" tem mais peso que "Drama" por ser menos comum.

**2. Similaridade de Cosseno**
Calcula o ângulo entre os vetores de dois filmes. Quanto menor o ângulo, mais similares são os filmes. O resultado é um score entre 0 e 1.

**3. Score de Qualidade**
Inspirado na fórmula de ranking do IMDB, normaliza o rating de cada filme para penalizar filmes com poucas avaliações e premiar filmes consistentemente bem avaliados.

O score final combina os três fatores:

```
score_final = 70% × similaridade + 30% × qualidade
```

---

## Arquitetura

```
Dataset Letterboxd (Kaggle)
        ↓
  Limpeza e filtros
  (rating ≥ 2.5, sem documentários)
        ↓
  Construção do texto TF-IDF
  (gênero × 4, tema × 2, diretor × 1)
        ↓
  Cálculo de similaridade em batches
        ↓
  Score final com qualidade
        ↓
  SQLite (25MB) — top 20 similares por filme
        ↓
  App Streamlit
```

---

## Dataset

- **Fonte:** [Letterboxd Dataset — Kaggle](https://www.kaggle.com/datasets/gsimonx37/letterboxd)
- **Filmes processados:** ~72.500 (após filtros)
- **Arquivos utilizados:** `movies.csv`, `crew.csv`, `genres.csv`, `themes.csv`, `posters.csv`

### Filtros aplicados
- Rating mínimo de 2.5
- Remoção de Documentários e TV Movies
- Apenas filmes com rating cadastrado

---

## Tecnologias

- **Python** — linguagem principal
- **Pandas / NumPy** — manipulação de dados
- **Scikit-learn** — TF-IDF e similaridade de cosseno
- **SQLite** — armazenamento dos similares pré-calculados
- **Streamlit** — interface web

---

## Estrutura do Projeto

```
recomendador-filmes-letterboxd/
├── app.py                          # App Streamlit
├── recomendador_final.db           # Banco SQLite pré-calculado
├── recomendador_letterboxd.ipynb   # Pipeline completo documentado
├── requirements.txt                # Dependências
└── README.md
```

---

## Rodando localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o app
streamlit run app.py
```

---

## Decisões técnicas

**Por que SQLite e não calcular em tempo real?**
Com 72k filmes a matriz de similaridade teria 72k × 72k = ~5 bilhões de valores. Pré-calcular e salvar apenas os top 20 similares por filme resulta em um banco de 25MB consultado em milissegundos.

**Por que remover a descrição do TF-IDF?**
Testes mostraram que descrições genéricas causavam matches incorretos entre filmes de gêneros completamente diferentes. Gênero, tema e diretor provaram ser sinais mais confiáveis.

**Por que o diretor tem peso 1x e não maior?**
Com peso maior, filmes do mesmo diretor ficavam muito similares independente do gênero — um curta-metragem podia aparecer como recomendação de um longa apenas por terem o mesmo realizador.
