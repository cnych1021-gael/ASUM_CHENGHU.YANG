"""专家实验室 - 高级可视化与深度分析"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from utils.data_loader import load_60_concepts, load_global_deviation, load_p5_cohesion, get_six_dimensions
from utils.user_model import is_expert_mode, record_page_view
from utils.language_manager import get_global_language
from utils.ai_explainer import answer_question, is_ai_available

st.set_page_config(page_title="Expert Lab", page_icon="🔬", layout="wide")

current_lang = get_global_language()
record_page_view("Expert Lab")

# 检查专家模式
if not is_expert_mode():
    st.error({
        'zh': '🔒 此页面仅限专家模式访问。请在主页切换到专家模式。',
        'en': '🔒 This page requires Expert Mode. Switch on home page.',
        'es': '🔒 Esta página requiere Modo Experto.'
    }[current_lang])
    st.stop()

T = {
    'title': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'},
    'subtitle': {'zh': '高级可视化与深度分析', 'en': 'Advanced Visualizations & Deep Analysis', 'es': 'Visualizaciones Avanzadas'},
    'tab_cluster': {'zh': '🎯 聚类分析', 'en': '🎯 Cluster', 'es': '🎯 Clustering'},
    'tab_3d': {'zh': '🌌 3D语义空间', 'en': '🌌 3D Space', 'es': '🌌 Espacio 3D'},
    'tab_p5': {'zh': '🏛️ P5凝聚力', 'en': '🏛️ P5 Cohesion', 'es': '🏛️ Cohesión P5'},
    'tab_ai': {'zh': '🤖 AI 研究助手', 'en': '🤖 AI Assistant', 'es': '🤖 Asistente IA'},
    'cluster_title': {'zh': '60个概念的语义偏移聚类', 'en': '60 Concepts Cluster Analysis', 'es': 'Análisis de Clusters'},
    'n_clusters': {'zh': '聚类数量', 'en': 'Number of Clusters', 'es': 'Número de Clusters'},
    'cluster_method': {'zh': '聚类方法', 'en': 'Method', 'es': 'Método'},
    '3d_title': {'zh': '3D语义偏移空间', 'en': '3D Semantic Space', 'es': 'Espacio Semántico 3D'},
    'p5_title': {'zh': 'P5各国语义凝聚力', 'en': 'P5 Semantic Cohesion', 'es': 'Cohesión Semántica P5'},
    'ai_research': {'zh': '💬 与AI研究助手对话', 'en': '💬 Chat with AI Research Assistant', 'es': '💬 Asistente IA'},
    'ai_placeholder': {'zh': '例如：分析sovereignty和human_right的语义关系', 'en': 'e.g., Analyze sovereignty vs human_right', 'es': 'ej: Analizar relación'},
    'ai_btn': {'zh': '🤖 提问', 'en': '🤖 Ask', 'es': '🤖 Preguntar'},
    'ai_loading': {'zh': '🤖 AI研究中...', 'en': '🤖 Researching...', 'es': '🤖 Investigando...'},
    'download': {'zh': '📥 下载完整数据', 'en': '📥 Download Full Data', 'es': '📥 Descargar'},
}

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")
st.markdown("---")

# 加载数据
df_concepts = load_60_concepts()
df_global = load_global_deviation()
df_p5 = load_p5_cohesion()
dimensions = get_six_dimensions()

# 添加维度信息
def get_dim(concept):
    for dim, cs in dimensions.items():
        if concept in cs:
            return dim
    return "其他"

df_concepts['Dimension_Auto'] = df_concepts['Concept'].apply(get_dim)

# 4 个标签页
tab1, tab2, tab3, tab4 = st.tabs([T['tab_cluster'][current_lang], T['tab_3d'][current_lang], 
                                    T['tab_p5'][current_lang], T['tab_ai'][current_lang]])

# ============ Tab 1: 聚类分析 ============
with tab1:
    st.header(T['cluster_title'][current_lang])
    
    col1, col2 = st.columns(2)
    with col1:
        n_clusters = st.slider(T['n_clusters'][current_lang], 2, 8, 4)
    
    # K-means 聚类
    if 'Similarity' in df_concepts.columns:
        # 使用 Similarity 作为特征（一维聚类用阈值）
        features = df_concepts[['Similarity']].values
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_concepts['Cluster'] = kmeans.fit_predict(features)
        
        # 散点图
        fig = px.scatter(
            df_concepts, x='Concept', y='Similarity',
            color='Cluster', size=[20]*len(df_concepts),
            hover_data=['Dimension_Auto'],
            color_continuous_scale='Viridis',
            title=f"K-Means 聚类 (k={n_clusters})"
        )
        fig.update_layout(height=500, xaxis_tickangle=-90)
        st.plotly_chart(fig, use_container_width=True)
        
        # 聚类统计
        cluster_stats = df_concepts.groupby('Cluster').agg({
            'Similarity': ['mean', 'count'],
            'Concept': lambda x: ', '.join(x.head(5))
        }).reset_index()
        cluster_stats.columns = ['Cluster', 'Avg_Similarity', 'Count', 'Sample_Concepts']
        st.dataframe(cluster_stats, use_container_width=True)

# ============ Tab 2: 3D 空间 ============
with tab2:
    st.header(T['3d_title'][current_lang])
    
    if 'Bloc' in df_global.columns and 'Deviation_ColdWar' in df_global.columns:
        # 按概念聚合
        global_agg = df_global.groupby('Concept').agg({
            'Deviation_ColdWar': 'mean',
            'Deviation_PostColdWar': 'mean'
        }).reset_index()
        
        # 合并 Similarity
        global_agg = global_agg.merge(df_concepts[['Concept', 'Similarity']], on='Concept', how='left')
        global_agg['Dimension'] = global_agg['Concept'].apply(get_dim)
        
        fig = px.scatter_3d(
            global_agg.dropna(),
            x='Deviation_ColdWar', y='Deviation_PostColdWar', z='Similarity',
            color='Dimension', hover_data=['Concept'],
            title="3D语义空间：冷战偏差 × 后冷战偏差 × 语义稳定性"
        )
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("3D数据不完整")

# ============ Tab 3: P5 凝聚力 ============
with tab3:
    st.header(T['p5_title'][current_lang])
    
    if not df_p5.empty:
        st.dataframe(df_p5, use_container_width=True, height=400)
        
        # 热力图
        if 'Concept' in df_p5.columns:
            numeric_cols = df_p5.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                fig = px.imshow(
                    df_p5[numeric_cols].T,
                    labels={'x': 'Concept', 'y': 'Country', 'color': 'Cohesion'},
                    color_continuous_scale='RdBu',
                    aspect='auto',
                    title="P5凝聚力热力图"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    csv = df_p5.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, "p5_cohesion.csv", "text/csv")

# ============ Tab 4: AI 研究助手 ============
with tab4:
    st.header(T['ai_research'][current_lang])
    
    if is_ai_available():
        # 历史对话
        if 'expert_chat_history' not in st.session_state:
            st.session_state.expert_chat_history = []
        
        # 显示历史
        for msg in st.session_state.expert_chat_history[-5:]:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
        
        user_q = st.text_input(
            T['ai_research'][current_lang],
            placeholder=T['ai_placeholder'][current_lang],
            key="expert_ai_q"
        )
        
        if st.button(T['ai_btn'][current_lang], type="primary"):
            if user_q:
                # 准备完整数据上下文
                context = f"""数据集：
- 60个概念语义偏移数据，平均相似度 {df_concepts['Similarity'].mean():.3f}
- 最稳定: {df_concepts.loc[df_concepts['Similarity'].idxmax(), 'Concept']}
- 最不稳定: {df_concepts.loc[df_concepts['Similarity'].idxmin(), 'Concept']}
- 涵盖6个维度：政治法律、安全冲突、经济发展、国际秩序、人文社会、环境科技
- P5国家：USA, CHN, RUS, GBR, FRA"""
                
                with st.spinner(T['ai_loading'][current_lang]):
                    answer = answer_question(user_q, context, current_lang)
                    
                    st.session_state.expert_chat_history.append({'role': 'user', 'content': user_q})
                    st.session_state.expert_chat_history.append({'role': 'assistant', 'content': answer})
                    
                    st.success("✨ AI回答")
                    st.markdown(answer)
                    st.caption("💡 由Google Gemini AI生成")
    else:
        st.warning("⚠️ AI功能未配置")
