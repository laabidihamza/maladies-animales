import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================
# CONFIGURATION
# ============================================

OUTPUT_FILE = "data/dataset_traduit.csv"

# ============================================
# DATA LOADING & CLEANING
# ============================================

@st.cache_data
def load_and_clean_data():
    if not os.path.exists(OUTPUT_FILE):
        st.error(f"❌ Fichier introuvable : {OUTPUT_FILE}")
        st.stop()

    try:
        df = pd.read_csv(OUTPUT_FILE, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {e}")
        st.stop()

    # Filter valid rows
    df_valid = df[
        (df['langue'] != 'N/A') &
        (df['langue'].notna()) &
        (df['contenu'] != 'Erreur lors du scraping')
    ].copy()

    if df_valid.empty:
        st.error("❌ Aucune donnée valide à afficher")
        st.stop()

    # Fill missing values
    df_valid['langue'] = df_valid['langue'].fillna('Non détecté')
    df_valid['source_publication'] = df_valid['source_publication'].fillna('Non classé')
    df_valid['maladie'] = df_valid['maladie'].fillna('Non identifiée')
    df_valid['animal'] = df_valid['animal'].fillna('Non spécifié')
    df_valid['lieu'] = df_valid['lieu'].fillna('Non spécifié')
    df_valid['date_publication'] = df_valid['date_publication'].fillna('inconnue')

    # Numeric conversion
    df_valid['nb_mots'] = pd.to_numeric(df_valid['nb_mots'], errors='coerce').fillna(0).astype(int)
    df_valid['nb_caracteres'] = pd.to_numeric(df_valid['nb_caracteres'], errors='coerce').fillna(0).astype(int)

    # Remove duplicates
    df_valid = df_valid.drop_duplicates(subset=['url']).reset_index(drop=True)

    return df_valid

# ============================================
# MAIN APP
# ============================================

st.set_page_config(
    page_title="Dashboard Maladies Animales",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Maladies Animales")

df = load_and_clean_data()
st.caption(f"📈 Base de données : {len(df)} articles analysés")

# ============================================
# SIDEBAR FILTERS
# ============================================

st.sidebar.header("🔍 Filtres")

# Language filter
langue_options = ["Toutes les langues"] + sorted(df['langue'].unique())
selected_langue = st.sidebar.selectbox("🌍 Langue", langue_options)

# Source filter
source_options = ["Toutes les sources"] + sorted(df['source_publication'].unique())
selected_source = st.sidebar.selectbox("📰 Type de source", source_options)

# Lieu filter
lieu_options = ["Tous les lieux"] + sorted(df['lieu'].unique())
selected_lieu = st.sidebar.selectbox("📍 Lieu", lieu_options)

# Maladie filter
maladie_options = ["Toutes les maladies"] + sorted(df['maladie'].unique())
selected_maladie = st.sidebar.selectbox("🦠 Maladie", maladie_options)

# Animal filter
animal_options = ["Tous les animaux"] + sorted(df['animal'].unique())
selected_animal = st.sidebar.selectbox("🐾 Animal", animal_options)

# Reset button (not truly needed in Streamlit, but for UX)
if st.sidebar.button("🔄 Réinitialiser"):
    st.rerun()

# ============================================
# APPLY FILTERS
# ============================================

filtered_df = df.copy()
if selected_langue != "Toutes les langues":
    filtered_df = filtered_df[filtered_df['langue'] == selected_langue]
if selected_source != "Toutes les sources":
    filtered_df = filtered_df[filtered_df['source_publication'] == selected_source]
if selected_lieu != "Tous les lieux":
    filtered_df = filtered_df[filtered_df['lieu'] == selected_lieu]
if selected_maladie != "Toutes les maladies":
    filtered_df = filtered_df[filtered_df['maladie'] == selected_maladie]
if selected_animal != "Tous les animaux":
    filtered_df = filtered_df[filtered_df['animal'] == selected_animal]

# Handle no results
if filtered_df.empty:
    st.warning("⚠️ Aucune donnée disponible avec ces filtres.")
    st.stop()

# ============================================
# KPIs
# ============================================

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Articles", len(filtered_df))
col2.metric("Mots moy.", int(filtered_df['nb_mots'].mean()))
col3.metric("Maladies", filtered_df['maladie'].nunique())
col4.metric("Animaux", filtered_df['animal'].nunique())
col5.metric("Lieux", filtered_df['lieu'].nunique())

# ============================================
# CHARTS
# ============================================

# Langue (Donut)
st.subheader("🌍 Répartition par langue")
langue_counts = filtered_df['langue'].value_counts()
fig_langue = px.pie(
    langue_counts,
    values=langue_counts.values,
    names=langue_counts.index,
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig_langue, use_container_width=True)

# Source
st.subheader("📰 Répartition par type de source")
source_counts = filtered_df['source_publication'].value_counts()
fig_source = px.bar(
    source_counts,
    x=source_counts.index,
    y=source_counts.values,
    color=source_counts.values,
    color_continuous_scale='Viridis',
    text=source_counts.values
)
fig_source.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_source, use_container_width=True)

# Maladies (Top 15)
st.subheader("🦠 Top 15 des maladies les plus mentionnées")
maladie_counts = filtered_df['maladie'].value_counts().head(15)
fig_maladie = px.bar(
    maladie_counts,
    x=maladie_counts.values,
    y=maladie_counts.index,
    orientation='h',
    color=maladie_counts.values,
    color_continuous_scale='Reds',
    text=maladie_counts.values
)
st.plotly_chart(fig_maladie, use_container_width=True)

# Animaux (Top 15)
st.subheader("🐾 Top 15 des animaux les plus mentionnés")
animal_counts = filtered_df['animal'].value_counts().head(15)
fig_animal = px.bar(
    animal_counts,
    x=animal_counts.values,
    y=animal_counts.index,
    orientation='h',
    color=animal_counts.values,
    color_continuous_scale='Greens',
    text=animal_counts.values
)
st.plotly_chart(fig_animal, use_container_width=True)

# Lieux (Top 15)
st.subheader("📍 Top 15 des lieux les plus mentionnés")
lieu_counts = filtered_df['lieu'].value_counts().head(15)
fig_lieu = px.bar(
    lieu_counts,
    x=lieu_counts.values,
    y=lieu_counts.index,
    orientation='h',
    color=lieu_counts.values,
    color_continuous_scale='Blues',
    text=lieu_counts.values
)
st.plotly_chart(fig_lieu, use_container_width=True)

# Stats (Box plot)
st.subheader("📊 Distribution statistique du contenu")
stats_fig = go.Figure()
stats_fig.add_trace(go.Box(
    y=filtered_df['nb_mots'],
    name='Nombre de mots',
    marker_color='#3498db',
    boxmean='sd'
))
stats_fig.add_trace(go.Box(
    y=filtered_df['nb_caracteres'] / 100,
    name='Nb caractères (÷100)',
    marker_color='#e74c3c',
    boxmean='sd'
))
st.plotly_chart(stats_fig, use_container_width=True)

# ============================================
# DATA TABLE
# ============================================

st.subheader("📋 Détails des articles (top 50)")
table_df = filtered_df[['code', 'titre', 'maladie', 'animal', 'lieu', 'langue', 'nb_mots', 'date_publication']].head(50)
st.dataframe(table_df, use_container_width=True)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("🦠 Dashboard Maladies Animales - Analyse automatisée d'articles")