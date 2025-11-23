import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(
    page_title="Dashboard - Maladies Animales",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f4788;
        font-weight: bold;
    }
    h2, h3 {
        color: #2c5aa0;
    }
    </style>
    """, unsafe_allow_html=True)

# Fonction pour charger les données
@st.cache_data
def load_data(file_path):
    """Charge et prétraite les données"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Conversion de la date
        df['date_publication'] = pd.to_datetime(df['date_publication'], format='%d-%m-%Y', errors='coerce')
        
        # Extraction du mois et de l'année
        df['annee'] = df['date_publication'].dt.year
        df['mois'] = df['date_publication'].dt.month
        df['mois_annee'] = df['date_publication'].dt.to_period('M').astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")
        return None

# Fonction pour créer un graphique temporel
def create_timeline_chart(df):
    """Crée un graphique de l'évolution temporelle des news"""
    df_time = df[df['date_publication'].notna()].copy()
    timeline_data = df_time.groupby('mois_annee').size().reset_index(name='nombre_news')
    
    fig = px.line(timeline_data, 
                  x='mois_annee', 
                  y='nombre_news',
                  title='Évolution du Nombre de News au Cours du Temps',
                  labels={'mois_annee': 'Période', 'nombre_news': 'Nombre de News'},
                  markers=True)
    
    fig.update_traces(line_color='#2c5aa0', marker=dict(size=8))
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        hovermode='x unified'
    )
    
    return fig

# Fonction pour créer un graphique par région
def create_location_chart(df):
    """Crée un graphique des news par région"""
    location_data = df[df['lieu'] != 'non spécifié']['lieu'].value_counts().head(10).reset_index()
    location_data.columns = ['lieu', 'nombre']
    
    fig = px.bar(location_data,
                 x='lieu',
                 y='nombre',
                 title='Top 10 des Régions Mentionnées',
                 labels={'lieu': 'Région', 'nombre': 'Nombre de News'},
                 color='nombre',
                 color_continuous_scale='Blues')
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

# Fonction pour créer un graphique par source
def create_source_chart(df):
    """Crée un graphique de la distribution des sources"""
    source_data = df['source'].value_counts().reset_index()
    source_data.columns = ['source', 'nombre']
    
    fig = px.pie(source_data,
                 values='nombre',
                 names='source',
                 title='Distribution des Sources de Publication',
                 hole=0.4,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True)
    
    return fig

# Fonction pour créer un graphique par maladie
def create_disease_chart(df):
    """Crée un graphique des maladies les plus mentionnées"""
    disease_data = df[df['maladie'] != 'non identifié']['maladie'].value_counts().head(10).reset_index()
    disease_data.columns = ['maladie', 'nombre']
    
    fig = px.bar(disease_data,
                 y='maladie',
                 x='nombre',
                 orientation='h',
                 title='Top 10 des Maladies Mentionnées',
                 labels={'maladie': 'Maladie', 'nombre': 'Nombre de News'},
                 color='nombre',
                 color_continuous_scale='Reds')
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

# Fonction pour créer un graphique de distribution des langues
def create_language_chart(df):
    """Crée un graphique de distribution des langues"""
    lang_data = df['langue'].value_counts().reset_index()
    lang_data.columns = ['langue', 'nombre']
    
    fig = go.Figure(data=[go.Bar(
        x=lang_data['langue'],
        y=lang_data['nombre'],
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][:len(lang_data)],
        text=lang_data['nombre'],
        textposition='auto'
    )])
    
    fig.update_layout(
        title='Distribution des Langues',
        xaxis_title='Langue',
        yaxis_title='Nombre de News',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# Fonction pour créer des statistiques sur les longueurs de texte
def create_text_length_stats(df):
    """Crée des graphiques pour les statistiques de longueur de texte"""
    fig = go.Figure()
    
    # Boxplot pour les caractères
    fig.add_trace(go.Box(
        y=df['nb_caracteres'],
        name='Caractères',
        marker_color='lightblue',
        boxmean='sd'
    ))
    
    # Boxplot pour les mots
    fig.add_trace(go.Box(
        y=df['nb_mots'],
        name='Mots',
        marker_color='lightgreen',
        boxmean='sd'
    ))
    
    fig.update_layout(
        title='Distribution de la Longueur des News',
        yaxis_title='Nombre',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True
    )
    
    return fig

# Fonction pour créer un nuage de mots
def create_wordcloud(df):
    """Crée un nuage de mots à partir des maladies"""
    diseases = df[df['maladie'] != 'non identifié']['maladie'].tolist()
    text = ' '.join(diseases)
    
    if text:
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white',
                            colormap='Blues',
                            max_words=50).generate(text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        return fig
    return None

# Fonction pour créer un heatmap source vs maladie
def create_heatmap(df):
    """Crée un heatmap croisant sources et maladies"""
    # Filtrer les données
    df_filtered = df[(df['maladie'] != 'non identifié') & (df['source'] != 'autre')]
    
    # Créer une table de contingence
    pivot_table = pd.crosstab(df_filtered['source'], df_filtered['maladie'])
    
    # Garder seulement les top 10 maladies
    top_diseases = df_filtered['maladie'].value_counts().head(10).index
    pivot_table = pivot_table[top_diseases]
    
    fig = px.imshow(pivot_table,
                    labels=dict(x="Maladie", y="Source", color="Nombre"),
                    title="Heatmap: Sources vs Maladies",
                    aspect="auto",
                    color_continuous_scale='Blues')
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# INTERFACE PRINCIPALE
def main():
    # Titre et description
    st.title("🐾 Dashboard d'Analyse - News sur les Maladies Animales")
    st.markdown("---")
    
    # Sidebar pour upload du fichier
    st.sidebar.header("📁 Configuration")
    uploaded_file = st.sidebar.file_uploader(
        "Charger le fichier CSV",
        type=['csv'],
        help="Sélectionnez le fichier CSV contenant les données scrapées"
    )
    
    # Charger les données par défaut ou uploadées
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.sidebar.info("💡 Veuillez charger un fichier CSV pour commencer l'analyse")
        # Essayer de charger un fichier par défaut
        try:
            df = load_data('dataset_maladies_animales_final.csv')
            st.sidebar.success("✅ Fichier par défaut chargé")
        except:
            st.warning("⚠️ Aucun fichier chargé. Veuillez uploader un fichier CSV dans la barre latérale.")
            st.stop()
    
    if df is None or df.empty:
        st.error("❌ Impossible de charger les données")
        st.stop()
    
    # Filtres dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par langue
    langues = ['Toutes'] + list(df['langue'].unique())
    langue_selectionnee = st.sidebar.selectbox("Langue", langues)
    
    # Filtre par source
    sources = ['Toutes'] + list(df['source'].unique())
    source_selectionnee = st.sidebar.selectbox("Source", sources)
    
    # Filtre par statut
    status_options = ['Tous', 'succès', 'échec']
    status_selectionne = st.sidebar.selectbox("Statut du scraping", status_options)
    
    # Appliquer les filtres
    df_filtered = df.copy()
    if langue_selectionnee != 'Toutes':
        df_filtered = df_filtered[df_filtered['langue'] == langue_selectionnee]
    if source_selectionnee != 'Toutes':
        df_filtered = df_filtered[df_filtered['source'] == source_selectionnee]
    if status_selectionne != 'Tous':
        df_filtered = df_filtered[df_filtered['status'] == status_selectionne]
    
    # Métriques clés
    st.header("📊 Métriques Générales")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total News", len(df_filtered))
    
    with col2:
        success_rate = (df_filtered['status'] == 'succès').sum() / len(df_filtered) * 100
        st.metric("Taux de Succès", f"{success_rate:.1f}%")
    
    with col3:
        avg_chars = df_filtered['nb_caracteres'].mean()
        st.metric("Moy. Caractères", f"{avg_chars:.0f}")
    
    with col4:
        avg_words = df_filtered['nb_mots'].mean()
        st.metric("Moy. Mots", f"{avg_words:.0f}")
    
    with col5:
        nb_langues = df_filtered['langue'].nunique()
        st.metric("Langues", nb_langues)
    
    st.markdown("---")
    
    # Onglets pour organiser les visualisations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Tendances Temporelles", 
        "🌍 Analyses Géographiques", 
        "🦠 Maladies", 
        "📰 Sources & Langues",
        "📊 Statistiques Textuelles"
    ])
    
    with tab1:
        st.subheader("Évolution Temporelle des Publications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if df_filtered['date_publication'].notna().sum() > 0:
                fig_timeline = create_timeline_chart(df_filtered)
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.warning("Aucune donnée temporelle disponible")
        
        with col2:
            # Statistiques temporelles
            st.markdown("### 📅 Statistiques Temporelles")
            df_with_dates = df_filtered[df_filtered['date_publication'].notna()]
            
            if not df_with_dates.empty:
                st.write(f"**Date la plus ancienne:** {df_with_dates['date_publication'].min().strftime('%d-%m-%Y')}")
                st.write(f"**Date la plus récente:** {df_with_dates['date_publication'].max().strftime('%d-%m-%Y')}")
                st.write(f"**Période couverte:** {(df_with_dates['date_publication'].max() - df_with_dates['date_publication'].min()).days} jours")
                
                # Distribution par année
                year_dist = df_with_dates['annee'].value_counts().sort_index()
                st.write("**Distribution par année:**")
                st.bar_chart(year_dist)
    
    with tab2:
        st.subheader("Analyses Géographiques")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_location = create_location_chart(df_filtered)
            st.plotly_chart(fig_location, use_container_width=True)
        
        with col2:
            # Carte si possible (nécessite des coordonnées)
            st.markdown("### 🗺️ Répartition Géographique")
            location_stats = df_filtered['lieu'].value_counts()
            st.dataframe(location_stats.head(15), use_container_width=True)
    
    with tab3:
        st.subheader("Analyse des Maladies")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_disease = create_disease_chart(df_filtered)
            st.plotly_chart(fig_disease, use_container_width=True)
        
        with col2:
            st.markdown("### ☁️ Nuage de Mots - Maladies")
            fig_wordcloud = create_wordcloud(df_filtered)
            if fig_wordcloud:
                st.pyplot(fig_wordcloud)
            else:
                st.warning("Pas assez de données pour générer un nuage de mots")
        
        # Heatmap
        st.markdown("### 🔥 Heatmap: Croisement Sources x Maladies")
        fig_heatmap = create_heatmap(df_filtered)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab4:
        st.subheader("Sources et Langues")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_source = create_source_chart(df_filtered)
            st.plotly_chart(fig_source, use_container_width=True)
        
        with col2:
            fig_language = create_language_chart(df_filtered)
            st.plotly_chart(fig_language, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("### 📋 Détails des Sources")
        source_details = df_filtered.groupby('source').agg({
            'code': 'count',
            'nb_caracteres': 'mean',
            'nb_mots': 'mean'
        }).round(0)
        source_details.columns = ['Nombre de News', 'Moy. Caractères', 'Moy. Mots']
        st.dataframe(source_details, use_container_width=True)
    
    with tab5:
        st.subheader("Statistiques sur les Textes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_text_stats = create_text_length_stats(df_filtered)
            st.plotly_chart(fig_text_stats, use_container_width=True)
        
        with col2:
            st.markdown("### 📏 Statistiques Détaillées")
            
            stats_df = pd.DataFrame({
                'Métrique': ['Caractères', 'Mots'],
                'Minimum': [df_filtered['nb_caracteres'].min(), df_filtered['nb_mots'].min()],
                'Moyenne': [df_filtered['nb_caracteres'].mean(), df_filtered['nb_mots'].mean()],
                'Médiane': [df_filtered['nb_caracteres'].median(), df_filtered['nb_mots'].median()],
                'Maximum': [df_filtered['nb_caracteres'].max(), df_filtered['nb_mots'].max()],
                'Écart-type': [df_filtered['nb_caracteres'].std(), df_filtered['nb_mots'].std()]
            })
            
            st.dataframe(stats_df.round(0), use_container_width=True, hide_index=True)
        
        # Histogramme de distribution
        st.markdown("### 📊 Distribution des Longueurs")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig_hist_chars = px.histogram(df_filtered, x='nb_caracteres', 
                                         title='Distribution du Nombre de Caractères',
                                         nbins=30,
                                         color_discrete_sequence=['#2c5aa0'])
            fig_hist_chars.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_hist_chars, use_container_width=True)
        
        with col_b:
            fig_hist_words = px.histogram(df_filtered, x='nb_mots',
                                         title='Distribution du Nombre de Mots',
                                         nbins=30,
                                         color_discrete_sequence=['#ff7f0e'])
            fig_hist_words.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_hist_words, use_container_width=True)
    
    # Section pour explorer les données brutes
    st.markdown("---")
    st.header("🔍 Exploration des Données")
    
    with st.expander("Voir les données brutes"):
        st.dataframe(df_filtered, use_container_width=True)
    
    with st.expander("Télécharger les données filtrées"):
        csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name='donnees_filtrees.csv',
            mime='text/csv'
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            Dashboard créé avec Streamlit 🎈 | Projet d'Analyse de News sur les Maladies Animales
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()