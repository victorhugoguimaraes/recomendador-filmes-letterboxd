import streamlit as st
import sqlite3
import pandas as pd

# ── Configuração ────────────────────────────────────────────────────
st.set_page_config(page_title="Recomendador de Filmes", layout="wide")

# ── CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1100px; }
    h1 { font-size: 1.8rem !important; font-weight: 600 !important; }
    .subtitle { color: #888; font-size: 0.95rem; margin-top: -10px; margin-bottom: 30px; }
    .card {
        background: #141414;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .card img {
        width: 100%;
        height: 280px;
        object-fit: cover;
        display: block;
    }
    .card-placeholder {
        width: 100%;
        height: 280px;
        background: #1e1e1e;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #333;
        font-size: 2rem;
    }
    .card-body { padding: 10px 12px 14px; }
    .card-title { font-size: 0.85rem; font-weight: 600; color: #f0f0f0; margin-bottom: 4px; line-height: 1.3; }
    .card-genre { font-size: 0.72rem; color: #888; margin-bottom: 4px; }
    .card-rating { font-size: 0.75rem; color: #f5c518; }
    .search-result-btn button {
        background: #1e1e1e !important;
        border: 1px solid #333 !important;
        color: #f0f0f0 !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
        text-align: left !important;
    }
    .search-result-btn button:hover {
        border-color: #888 !important;
        color: #fff !important;
    }
    div[data-testid="stTextInput"] label { display: none; }
    div[data-testid="stTextInput"] input {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        color: #f0f0f0 !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Banco de dados ──────────────────────────────────────────────────
@st.cache_data
def carregar_filmes():
    conn = sqlite3.connect("recomendador_final.db")
    filmes = pd.read_sql("SELECT id, name, date, rating, link, generos FROM filmes", conn)
    conn.close()
    return filmes

def buscar_similares(filme_id, excluir_ids=set(), n=6):
    conn = sqlite3.connect("recomendador_final.db")
    row = conn.execute(
        "SELECT similares_ids FROM similares WHERE filme_id = ?", (filme_id,)
    ).fetchone()
    conn.close()
    if not row:
        return []
    ids = [int(i) for i in row[0].split(",") if int(i) not in excluir_ids]
    return ids[:n]

# ── Interface ───────────────────────────────────────────────────────
st.markdown("# Recomendador de Filmes")
st.markdown('<p class="subtitle">Escolha um filme e descubra o que assistir a seguir.</p>', unsafe_allow_html=True)

filmes = carregar_filmes()
filmes_dict = filmes.set_index("id").to_dict("index")

# Session state
if "ja_assisti" not in st.session_state:
    st.session_state.ja_assisti = set()
if "filme_atual" not in st.session_state:
    st.session_state.filme_atual = None

# ── Busca ────────────────────────────────────────────────────────────
nome_digitado = st.text_input("", placeholder="🔍  Digite o nome do filme...")

if nome_digitado and len(nome_digitado) >= 2:
    filmes_encontrados = filmes[
        filmes["name"].str.contains(nome_digitado, case=False, na=False)
    ].head(6)

    if not filmes_encontrados.empty:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filmes_encontrados.iterrows()):
            ano = str(row["date"])[:4] if pd.notna(row["date"]) else ""
            label = f"{row['name']} ({ano})"
            with cols[i % 3]:
                st.markdown('<div class="search-result-btn">', unsafe_allow_html=True)
                if st.button(label, key=f"filme_{row['id']}", use_container_width=True):
                    st.session_state.ja_assisti = set()
                    st.session_state.filme_atual = row["name"]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("Nenhum filme encontrado.")

# ── Recomendações ────────────────────────────────────────────────────
if st.session_state.filme_atual:
    filme_row = filmes[filmes["name"] == st.session_state.filme_atual].iloc[0]
    filme_id = int(filme_row["id"])

    ids_recomendar = buscar_similares(filme_id, st.session_state.ja_assisti, n=6)

    st.markdown("---")

    if not ids_recomendar:
        st.info("Não há mais recomendações disponíveis!")
    else:
        st.markdown(f"<p style='color:#888; font-size:0.9rem; margin-bottom:20px;'>Recomendações baseadas em <strong style='color:#f0f0f0'>{st.session_state.filme_atual}</strong></p>", unsafe_allow_html=True)

        for i in range(0, len(ids_recomendar), 3):
            cols = st.columns(3, gap="medium")
            for j, col in enumerate(cols):
                if i + j < len(ids_recomendar):
                    fid = ids_recomendar[i + j]
                    info = filmes_dict.get(fid, {})
                    nome = info.get("name", "")
                    rating = info.get("rating", "")
                    genero = info.get("generos", "")
                    link = info.get("link", "")
                    ano = str(info.get("date", ""))[:4]

                    with col:
                        if link:
                            st.markdown(f"""
                            <div class="card">
                                <img src="{link}" />
                                <div class="card-body">
                                    <div class="card-title">{nome} ({ano})</div>
                                    <div class="card-genre">{genero}</div>
                                    <div class="card-rating">★ {rating}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="card">
                                <div class="card-placeholder">🎬</div>
                                <div class="card-body">
                                    <div class="card-title">{nome} ({ano})</div>
                                    <div class="card-genre">{genero}</div>
                                    <div class="card-rating">★ {rating}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        if st.button("Já assisti", key=f"ja_{fid}"):
                            st.session_state.ja_assisti.add(fid)
                            st.rerun()