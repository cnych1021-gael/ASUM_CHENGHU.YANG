"""
Global Semantic Shift Dashboard - Multilingual (zh/en/es)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils.data_loader import load_60_concepts, get_concept_definition, get_six_dimensions
from utils.user_model import is_expert_mode, record_concept_click, get_serendipity_recommendations, get_collaborative_recommendations
from utils.language_manager import get_global_language

st.set_page_config(page_title="Global Overview", page_icon="📊", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '📊 全局语义偏移看板', 'en': '📊 Global Semantic Shift Dashboard', 'es': '📊 Panel de Cambio Semántico Global'},
    'subtitle': {'zh': '60个核心政治概念的历时演变分析（1971-2025）', 'en': 'Diachronic Analysis of 60 Core Political Concepts (1971-2025)', 'es': 'Análisis Diacrónico de 60 Conceptos Políticos (1971-2025)'},
    'recommendation': {'zh': '💡 推荐系统', 'en': '💡 Recommendation System', 'es': '💡 Sistema de Recomendación'},
    'unexplored': {'zh': '**🔍 未探索的领域推荐：**', 'en': '**🔍 Unexplored Areas:**', 'es': '**🔍 Áreas No Exploradas:**'},
    'unexplored_caption': {'zh': '基于您未探索的维度推荐', 'en': 'Based on your unexplored dimensions', 'es': 'Basado en dimensiones no exploradas'},
    'similar_users': {'zh': '**👥 相似用户也在看：**', 'en': '**👥 Similar Users Are Viewing:**', 'es': '**👥 Usuarios Similares Ven:**'},
    'similar_caption': {'zh': '基于相似用户兴趣推荐', 'en': 'Based on similar users\' interests', 'es': 'Basado en intereses similares'},
    'start_explore': {'zh': '开始探索后，系统将为您推荐其他用户感兴趣的内容', 'en': 'Start exploring to get recommendations from similar users', 'es': 'Comienza a explorar para obtener recomendaciones'},
    'no_collab': {'zh': '暂无协同推荐', 'en': 'No collaborative recommendations yet', 'es': 'Sin recomendaciones colaborativas aún'},
    'select_dim': {'zh': '选择维度查看：', 'en': 'Select Dimension:', 'es': 'Seleccionar Dimensión:'},
    'all_dims': {'zh': '全部维度', 'en': 'All Dimensions', 'es': 'Todas las Dimensiones'},
    'sort_by': {'zh': '排序方式：', 'en': 'Sort By:', 'es': 'Ordenar Por:'},
    'sort_shift': {'zh': '语义偏移（从大到小）', 'en': 'Semantic Shift (Large to Small)', 'es': 'Cambio Semántico (Mayor a Menor)'},
    'sort_alpha': {'zh': '字母顺序', 'en': 'Alphabetical', 'es': 'Alfabético'},
    'expert_mode_msg': {'zh': '🔬 **专家模式** - 显示完整数据和高级分析', 'en': '🔬 **Expert Mode** - Full data and advanced analysis', 'es': '🔬 **Modo Experto** - Datos completos y análisis avanzado'},
    'novice_mode_msg': {'zh': '🎓 **新手模式** - 简化展示，包含AI解释和词云', 'en': '🎓 **Novice Mode** - Simplified view with AI explanations and word cloud', 'es': '🎓 **Modo Principiante** - Vista simplificada con explicaciones'},
    'concept_interp': {'zh': '📖 核心概念解读', 'en': '📖 Core Concepts Interpretation', 'es': '📖 Interpretación de Conceptos'},
    'top_concepts': {'zh': '🔥 语义变化最剧烈的10个概念', 'en': '🔥 Top 10 Most Changed Concepts', 'es': '🔥 Top 10 Conceptos Más Cambiados'},
    'similarity_label': {'zh': '相似度', 'en': 'Similarity', 'es': 'Similitud'},
    'definition': {'zh': '**📚 定义：**', 'en': '**📚 Definition:**', 'es': '**📚 Definición:**'},
    'big_change': {'zh': '⚠️ 这个词的含义在过去50年发生了**巨大变化**！', 'en': '⚠️ This concept has undergone **significant change** over the past 50 years!', 'es': '⚠️ ¡Este concepto ha cambiado **significativamente** en 50 años!'},
    'mod_change': {'zh': 'ℹ️ 这个词的含义有**一定程度的演变**。', 'en': 'ℹ️ This concept has evolved **moderately**.', 'es': 'ℹ️ Este concepto ha evolucionado **moderadamente**.'},
    'stable': {'zh': '✅ 这个词的含义相对**稳定**。', 'en': '✅ This concept is relatively **stable**.', 'es': '✅ Este concepto es relativamente **estable**.'},
    'stability': {'zh': '语义稳定性', 'en': 'Semantic Stability', 'es': 'Estabilidad Semántica'},
    'learn_more': {'zh': '了解更多', 'en': 'Learn More', 'es': 'Saber Más'},
    'recorded': {'zh': '已记录您对 {} 的兴趣！', 'en': 'Recorded your interest in {}!', 'es': '¡Interés en {} registrado!'},
    'word_cloud': {'zh': '☁️ 概念词云', 'en': '☁️ Concept Word Cloud', 'es': '☁️ Nube de Palabras'},
    'wc_caption': {'zh': '💡 词越大，表示语义变化越剧烈', 'en': '💡 Larger words indicate greater semantic change', 'es': '💡 Palabras más grandes = mayor cambio semántico'},
    'full_analysis': {'zh': '📊 完整数据分析', 'en': '📊 Full Data Analysis', 'es': '📊 Análisis Completo de Datos'},
    'shift_viz': {'zh': '语义偏移可视化', 'en': 'Semantic Shift Visualization', 'es': 'Visualización de Cambio Semántico'},
    'cosine_sim': {'zh': '余弦相似度', 'en': 'Cosine Similarity', 'es': 'Similitud de Coseno'},
    'concept': {'zh': '概念', 'en': 'Concept', 'es': 'Concepto'},
    'top20_title': {'zh': '{} - Top 20 语义偏移排名', 'en': '{} - Top 20 Semantic Shift Ranking', 'es': '{} - Top 20 Cambio Semántico'},
    'detail_table': {'zh': '📋 详细数据表', 'en': '📋 Detailed Data Table', 'es': '📋 Tabla de Datos Detallados'},
    'min_sim': {'zh': '最小相似度', 'en': 'Minimum Similarity', 'es': 'Similitud Mínima'},
    'max_sim': {'zh': '最大相似度', 'en': 'Maximum Similarity', 'es': 'Similitud Máxima'},
    'download': {'zh': '📥 下载数据 (CSV)', 'en': '📥 Download Data (CSV)', 'es': '📥 Descargar Datos (CSV)'},
    'stats_summary': {'zh': '📈 统计摘要', 'en': '📈 Statistical Summary', 'es': '📈 Resumen Estadístico'},
    'total_words': {'zh': '总词汇数', 'en': 'Total Words', 'es': 'Total de Palabras'},
    'drastic_shift': {'zh': '剧烈偏移 (<0.5)', 'en': 'Drastic Shift (<0.5)', 'es': 'Cambio Drástico (<0.5)'},
    'moderate_shift': {'zh': '中度偏移 (0.5-0.7)', 'en': 'Moderate Shift (0.5-0.7)', 'es': 'Cambio Moderado (0.5-0.7)'},
    'stable_shift': {'zh': '相对稳定 (≥0.7)', 'en': 'Relatively Stable (≥0.7)', 'es': 'Relativamente Estable (≥0.7)'},
    'continue': {'zh': '🧭 继续探索', 'en': '🧭 Continue Exploring', 'es': '🧭 Continuar Explorando'},
    'nav_bloc': {'zh': '🌍 阵营对比分析', 'en': '🌍 Bloc Analysis', 'es': '🌍 Análisis de Bloques'},
    'nav_consistency': {'zh': '✅ 言行一致性', 'en': '✅ Consistency Check', 'es': '✅ Verificación'},
    'nav_expert': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'}
}

df_concepts = load_60_concepts()
dimensions = get_six_dimensions()

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

expert_mode = is_expert_mode()

with st.sidebar:
    st.header(T['recommendation'][current_lang])
    
    all_concepts = {}
    for dim, concepts in dimensions.items():
        all_concepts[dim] = concepts
    
    serendipity_recs = get_serendipity_recommendations(all_concepts, n=2)
    
    if serendipity_recs:
        st.markdown(T['unexplored'][current_lang])
        for rec in serendipity_recs:
            st.info(f"• {rec}")
        st.caption(T['unexplored_caption'][current_lang])
    
    st.markdown("---")
    st.markdown(T['similar_users'][current_lang])
    
    if 'simulated_users' not in st.session_state:
        import random
        st.session_state.simulated_users = {}
        for i in range(3):
            user_weights = {dim: random.randint(0, 10) for dim in dimensions.keys()}
            clicked_concepts = random.sample(
                [c for concepts in dimensions.values() for c in concepts],
                random.randint(5, 15)
            )
            st.session_state.simulated_users[f'user_{i}'] = {
                'interest_weights': user_weights,
                'clicked_concepts': clicked_concepts,
                'click_counts': {c: random.randint(1, 5) for c in clicked_concepts}
            }
    
    try:
        collab_recs = get_collaborative_recommendations(
            st.session_state.simulated_users,
            all_concepts,
            st.session_state.user_profile.get('interest_weights', {}),
            n=2
        )
    except:
        collab_recs = []
    
    if collab_recs:
        for rec in collab_recs:
            st.success(f"• {rec}")
        st.caption(T['similar_caption'][current_lang])
    else:
        if len(st.session_state.user_profile.get('clicked_concepts', {})) == 0:
            st.info(T['start_explore'][current_lang])
        else:
            st.info(T['no_collab'][current_lang])

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    selected_dimension = st.selectbox(
        T['select_dim'][current_lang],
        [T['all_dims'][current_lang]] + list(dimensions.keys())
    )

with col2:
    if expert_mode:
        sort_by = st.selectbox(T['sort_by'][current_lang], [T['sort_shift'][current_lang], T['sort_alpha'][current_lang]])
    else:
        sort_by = T['sort_shift'][current_lang]

if selected_dimension == T['all_dims'][current_lang]:
    filtered_df = df_concepts.copy()
else:
    concepts_in_dim = dimensions[selected_dimension]
    filtered_df = df_concepts[df_concepts['Concept'].isin(concepts_in_dim)]

if sort_by == T['sort_shift'][current_lang]:
    filtered_df = filtered_df.sort_values('Similarity', ascending=True)
else:
    filtered_df = filtered_df.sort_values('Concept')

filtered_df = filtered_df.dropna(subset=['Similarity'])

st.markdown("---")

if expert_mode:
    st.info(T['expert_mode_msg'][current_lang])
else:
    st.info(T['novice_mode_msg'][current_lang])

st.markdown("---")

if not expert_mode:
    st.header(T['concept_interp'][current_lang])
    
    st.subheader(T['top_concepts'][current_lang])
    
    top_10 = filtered_df.head(10)
    
    for idx, row in top_10.iterrows():
        concept = row['Concept']
        similarity = row['Similarity']
        
        concept_dimension = None
        for dim, concepts in dimensions.items():
            if concept in concepts:
                concept_dimension = dim
                break
        
        with st.expander(f"{'🔥' if similarity < 0.5 else '⚠️'} {concept.upper()} ({T['similarity_label'][current_lang]}: {similarity:.2f})", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(T['definition'][current_lang])
                st.write(get_concept_definition(concept))
                
                if similarity < 0.5:
                    st.warning(T['big_change'][current_lang])
                elif similarity < 0.7:
                    st.info(T['mod_change'][current_lang])
                else:
                    st.success(T['stable'][current_lang])
            
            with col2:
                st.metric(T['stability'][current_lang], f"{similarity:.0%}")
                
                if st.button(T['learn_more'][current_lang], key=f"learn_{concept}"):
                    if concept_dimension:
                        record_concept_click(concept, concept_dimension)
                    st.info(T['recorded'][current_lang].format(concept))
    
    st.markdown("---")
    st.subheader(T['word_cloud'][current_lang])
    
    word_freq = {}
    for _, row in filtered_df.iterrows():
        word_freq[row['Concept']] = (1 - row['Similarity']) * 100
    
    if word_freq:
        wordcloud = WordCloud(
            width=600,
            height=300,
            background_color='white',
            colormap='RdYlGn_r'
        ).generate_from_frequencies(word_freq)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        plt.close()
        
        st.caption(T['wc_caption'][current_lang])

else:
    st.header(T['full_analysis'][current_lang])
    
    st.subheader(T['shift_viz'][current_lang])
    
    fig = px.bar(
        filtered_df.head(20),
        x='Similarity',
        y='Concept',
        color='Similarity',
        orientation='h',
        color_continuous_scale='RdYlGn',
        labels={'Similarity': T['cosine_sim'][current_lang], 'Concept': T['concept'][current_lang]},
        title=T['top20_title'][current_lang].format(selected_dimension)
    )
    
    fig.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader(T['detail_table'][current_lang])
    
    col1, col2 = st.columns(2)
    with col1:
        min_sim = st.slider(T['min_sim'][current_lang], 0.0, 1.0, 0.0, 0.05)
    with col2:
        max_sim = st.slider(T['max_sim'][current_lang], 0.0, 1.0, 1.0, 0.05)
    
    filtered_display = filtered_df[
        (filtered_df['Similarity'] >= min_sim) & 
        (filtered_df['Similarity'] <= max_sim)
    ]
    
    st.dataframe(
        filtered_display[['Dimension', 'Concept', 'Similarity', 'Shift_Status', 
                          'Cold_War_Context', 'Post_Cold_War_Context']],
        use_container_width=True,
        height=400
    )
    
    csv = filtered_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=T['download'][current_lang],
        data=csv,
        file_name=f"semantic_shift_{selected_dimension}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    st.subheader(T['stats_summary'][current_lang])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(T['total_words'][current_lang], len(filtered_df))
    
    with col2:
        drastic = len(filtered_df[filtered_df['Similarity'] < 0.5])
        st.metric(T['drastic_shift'][current_lang], drastic)
    
    with col3:
        moderate = len(filtered_df[(filtered_df['Similarity'] >= 0.5) & (filtered_df['Similarity'] < 0.7)])
        st.metric(T['moderate_shift'][current_lang], moderate)
    
    with col4:
        stable = len(filtered_df[filtered_df['Similarity'] >= 0.7])
        st.metric(T['stable_shift'][current_lang], stable)

st.markdown("---")
st.markdown(f"### {T['continue'][current_lang]}")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/2_🌍_Bloc_Analysis.py", label=T['nav_bloc'][current_lang])

with col2:
    st.page_link("pages/3_✅_Consistency_Check.py", label=T['nav_consistency'][current_lang])

with col3:
    if expert_mode:
        st.page_link("pages/4_🔬_Expert_Lab.py", label=T['nav_expert'][current_lang])
