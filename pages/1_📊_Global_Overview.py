"""全局语义偏移看板 - 多语言（zh/en/es）+ AI解释"""
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils.data_loader import load_60_concepts, get_concept_definition, get_six_dimensions
from utils.user_model import is_expert_mode, record_concept_click, get_serendipity_recommendations, record_page_view
from utils.language_manager import get_global_language
from utils.ai_explainer import explain_concept_evolution, is_ai_available

st.set_page_config(page_title="Global Overview", page_icon="📊", layout="wide")

current_lang = get_global_language()
record_page_view("Global Overview")

T = {
    'title': {'zh': '📊 全局语义偏移看板', 'en': '📊 Global Semantic Shift Dashboard', 'es': '📊 Panel de Cambio Semántico'},
    'subtitle': {'zh': '60个核心政治概念的历时演变（1971-2025）', 'en': 'Diachronic Evolution of 60 Core Political Concepts (1971-2025)', 'es': 'Evolución de 60 Conceptos Políticos (1971-2025)'},
    'recommendation': {'zh': '💡 推荐系统', 'en': '💡 Recommendations', 'es': '💡 Recomendaciones'},
    'unexplored': {'zh': '🔍 未探索的领域：', 'en': '🔍 Unexplored Areas:', 'es': '🔍 Áreas No Exploradas:'},
    'select_dim': {'zh': '选择维度：', 'en': 'Select Dimension:', 'es': 'Seleccionar Dimensión:'},
    'all_dims': {'zh': '全部维度', 'en': 'All Dimensions', 'es': 'Todas'},
    'expert_mode_msg': {'zh': '🔬 **专家模式** - 显示完整数据和高级分析', 'en': '🔬 **Expert Mode** - Full data', 'es': '🔬 **Experto** - Datos completos'},
    'novice_mode_msg': {'zh': '🎓 **新手模式** - 简化展示，含AI解释', 'en': '🎓 **Novice Mode** - With AI explanations', 'es': '🎓 **Principiante** - Con IA'},
    'top_concepts': {'zh': '🔥 语义变化最剧烈的10个概念', 'en': '🔥 Top 10 Most Changed Concepts', 'es': '🔥 Top 10 Más Cambiados'},
    'similarity': {'zh': '相似度', 'en': 'Similarity', 'es': 'Similitud'},
    'definition': {'zh': '📚 定义：', 'en': '📚 Definition:', 'es': '📚 Definición:'},
    'big_change': {'zh': '⚠️ 这个词的含义在过去50年发生了**巨大变化**！', 'en': '⚠️ Underwent **significant change**!', 'es': '⚠️ ¡Cambió **significativamente**!'},
    'mod_change': {'zh': 'ℹ️ 这个词的含义有**一定演变**', 'en': 'ℹ️ Evolved **moderately**', 'es': 'ℹ️ Evolucionó **moderadamente**'},
    'stable': {'zh': '✅ 这个词的含义相对**稳定**', 'en': '✅ Relatively **stable**', 'es': '✅ Relativamente **estable**'},
    'stability': {'zh': '稳定性', 'en': 'Stability', 'es': 'Estabilidad'},
    'learn_more': {'zh': '📖 了解更多', 'en': '📖 Learn More', 'es': '📖 Más'},
    'ai_explain': {'zh': '🤖 AI深度解释', 'en': '🤖 AI Explanation', 'es': '🤖 Explicación IA'},
    'ai_loading': {'zh': '🤖 AI正在分析...', 'en': '🤖 AI analyzing...', 'es': '🤖 IA analizando...'},
    'ai_generated': {'zh': '✨ AI生成的解释', 'en': '✨ AI-Generated', 'es': '✨ Generado por IA'},
    'ai_disclaimer': {'zh': '💡 由Google Gemini AI生成。仅供学术参考。', 'en': '💡 By Google Gemini. Academic only.', 'es': '💡 Por Google Gemini. Solo académico.'},
    'recorded': {'zh': '✅ 已记录您对 {} 的兴趣！', 'en': '✅ Recorded interest in {}!', 'es': '✅ ¡Interés en {} registrado!'},
    'word_cloud': {'zh': '☁️ 概念词云', 'en': '☁️ Word Cloud', 'es': '☁️ Nube'},
    'wc_caption': {'zh': '💡 词越大，语义变化越剧烈', 'en': '💡 Larger = more change', 'es': '💡 Más grande = más cambio'},
    'full_analysis': {'zh': '📊 完整数据分析', 'en': '📊 Full Analysis', 'es': '📊 Análisis Completo'},
    'top20_title': {'zh': 'Top 20 语义偏移排名', 'en': 'Top 20 Semantic Shift', 'es': 'Top 20 Cambio Semántico'},
    'detail_table': {'zh': '📋 详细数据表', 'en': '📋 Data Table', 'es': '📋 Tabla'},
    'download': {'zh': '📥 下载数据', 'en': '📥 Download', 'es': '📥 Descargar'},
    'stats_summary': {'zh': '📈 统计摘要', 'en': '📈 Stats', 'es': '📈 Resumen'},
    'total_words': {'zh': '总词汇', 'en': 'Total', 'es': 'Total'},
    'drastic_shift': {'zh': '剧烈偏移', 'en': 'Drastic', 'es': 'Drástico'},
    'moderate_shift': {'zh': '中度偏移', 'en': 'Moderate', 'es': 'Moderado'},
    'stable_shift': {'zh': '相对稳定', 'en': 'Stable', 'es': 'Estable'},
}

df_concepts = load_60_concepts()
dimensions = get_six_dimensions()

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

expert_mode = is_expert_mode()
ab_group = st.session_state.user_profile.get('ab_group', 'experiment')

# 侧边栏推荐
with st.sidebar:
    if ab_group == 'experiment':
        st.header(T['recommendation'][current_lang])
        recs = get_serendipity_recommendations(dimensions, n=2)
        if recs:
            st.markdown(f"**{T['unexplored'][current_lang]}**")
            for rec in recs:
                st.info(f"• {rec}")

st.markdown("---")

# 维度选择
selected_dim = st.selectbox(
    T['select_dim'][current_lang],
    [T['all_dims'][current_lang]] + list(dimensions.keys())
)

if selected_dim == T['all_dims'][current_lang]:
    filtered_df = df_concepts.copy()
else:
    concepts_in_dim = dimensions[selected_dim]
    filtered_df = df_concepts[df_concepts['Concept'].isin(concepts_in_dim)]

filtered_df = filtered_df.sort_values('Similarity', ascending=True).dropna(subset=['Similarity'])

st.markdown("---")

if expert_mode:
    st.info(T['expert_mode_msg'][current_lang])
else:
    st.info(T['novice_mode_msg'][current_lang])

st.markdown("---")

# ===== 新手模式：核心概念解读 + AI =====
if not expert_mode:
    st.header(T['top_concepts'][current_lang])
    
    top_10 = filtered_df.head(10)
    
    for idx, row in top_10.iterrows():
        concept = row['Concept']
        similarity = row['Similarity']
        
        # 找概念所属维度
        concept_dim = None
        for dim, cs in dimensions.items():
            if concept in cs:
                concept_dim = dim
                break
        
        with st.expander(f"{'🔥' if similarity < 0.5 else '⚠️'} {concept.upper()} ({T['similarity'][current_lang]}: {similarity:.2f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{T['definition'][current_lang]}**")
                st.write(get_concept_definition(concept, current_lang))
                
                if similarity < 0.5:
                    st.warning(T['big_change'][current_lang])
                elif similarity < 0.7:
                    st.info(T['mod_change'][current_lang])
                else:
                    st.success(T['stable'][current_lang])
            
            with col2:
                st.metric(T['stability'][current_lang], f"{similarity:.0%}")
                if st.button(T['learn_more'][current_lang], key=f"learn_{concept}"):
                    if concept_dim:
                        record_concept_click(concept, concept_dim)
                    st.success(T['recorded'][current_lang].format(concept))
            
            # ============ AI 深度解释 ============
            st.markdown("---")
            if is_ai_available():
                if st.button(T['ai_explain'][current_lang], key=f"ai_{concept}", type="primary"):
                    with st.spinner(T['ai_loading'][current_lang]):
                        cold_ctx = str(row.get('Cold_War_Context', ''))[:200] if 'Cold_War_Context' in row else ''
                        post_ctx = str(row.get('Post_Cold_War_Context', ''))[:200] if 'Post_Cold_War_Context' in row else ''
                        
                        explanation = explain_concept_evolution(
                            concept=concept,
                            similarity=similarity,
                            cold_context=cold_ctx,
                            post_context=post_ctx,
                            lang=current_lang
                        )
                        
                        st.success(T['ai_generated'][current_lang])
                        st.markdown(explanation)
                        st.caption(T['ai_disclaimer'][current_lang])
    
    # 词云
    st.markdown("---")
    st.subheader(T['word_cloud'][current_lang])
    
    word_freq = {row['Concept']: (1 - row['Similarity']) * 100 for _, row in filtered_df.iterrows()}
    
    if word_freq:
        wordcloud = WordCloud(width=600, height=300, background_color='white', colormap='RdYlGn_r').generate_from_frequencies(word_freq)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        plt.close()
        st.caption(T['wc_caption'][current_lang])

# ===== 专家模式：完整数据分析 =====
else:
    st.header(T['full_analysis'][current_lang])
    
    fig = px.bar(
        filtered_df.head(20),
        x='Similarity', y='Concept',
        color='Similarity', orientation='h',
        color_continuous_scale='RdYlGn',
        title=T['top20_title'][current_lang]
    )
    fig.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader(T['detail_table'][current_lang])
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, "semantic_shift.csv", "text/csv")
    
    # 统计
    st.markdown("---")
    st.subheader(T['stats_summary'][current_lang])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(T['total_words'][current_lang], len(filtered_df))
    col2.metric(T['drastic_shift'][current_lang], len(filtered_df[filtered_df['Similarity'] < 0.5]))
    col3.metric(T['moderate_shift'][current_lang], len(filtered_df[(filtered_df['Similarity'] >= 0.5) & (filtered_df['Similarity'] < 0.7)]))
    col4.metric(T['stable_shift'][current_lang], len(filtered_df[filtered_df['Similarity'] >= 0.7]))
