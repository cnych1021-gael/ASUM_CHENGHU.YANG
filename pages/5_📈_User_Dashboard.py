"""
User Profile Dashboard - Multilingual (zh/en/es)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.user_model import initialize_user_profile, get_ab_test_metrics, record_page_view
from utils.data_loader import get_six_dimensions
from utils.language_manager import get_global_language

st.set_page_config(page_title="User Dashboard", page_icon="📈", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '📈 个人学习画像仪表板', 'en': '📈 Personal Learning Dashboard', 'es': '📈 Panel de Aprendizaje Personal'},
    'subtitle': {'zh': '可视化您的探索历程', 'en': 'Visualize Your Exploration Journey', 'es': 'Visualiza Tu Viaje de Exploración'},
    'no_profile': {'zh': '⚠️ 请先从首页开始使用系统', 'en': '⚠️ Please start from the home page', 'es': '⚠️ Por favor comience desde la página principal'},
    'no_exploration': {'zh': '🎯 您还没有开始探索！请访问其他页面开始您的学习之旅。', 'en': "🎯 You haven't started exploring yet! Please visit other pages to begin your learning journey.", 'es': '🎯 ¡Aún no has comenzado a explorar! Por favor visita otras páginas para comenzar tu viaje.'},
    'stats_header': {'zh': '📊 探索统计', 'en': '📊 Exploration Statistics', 'es': '📊 Estadísticas de Exploración'},
    'total_concepts': {'zh': '总探索词汇', 'en': 'Total Concepts Explored', 'es': 'Conceptos Totales Explorados'},
    'total_clicks': {'zh': '总点击次数', 'en': 'Total Clicks', 'es': 'Clics Totales'},
    'dimensions_explored': {'zh': '探索维度数', 'en': 'Dimensions Explored', 'es': 'Dimensiones Exploradas'},
    'session_time': {'zh': '本次会话时长', 'en': 'Current Session Duration', 'es': 'Duración de Sesión Actual'},
    'minutes': {'zh': '分钟', 'en': 'min', 'es': 'min'},
    'radar_header': {'zh': '🎯 兴趣偏好雷达图', 'en': '🎯 Interest Preference Radar', 'es': '🎯 Radar de Preferencias'},
    'radar_title': {'zh': '各维度探索兴趣强度（归一化）', 'en': 'Interest Intensity by Dimension (Normalized)', 'es': 'Intensidad de Interés por Dimensión (Normalizada)'},
    'interest_intensity': {'zh': '兴趣强度', 'en': 'Interest Intensity', 'es': 'Intensidad de Interés'},
    'radar_caption': {'zh': '💡 雷达图越大，表示您对该维度的兴趣越高', 'en': '💡 Larger radar indicates higher interest in that dimension', 'es': '💡 Radar más grande indica mayor interés en esa dimensión'},
    'distribution_header': {'zh': '📊 维度探索分布', 'en': '📊 Dimension Exploration Distribution', 'es': '📊 Distribución de Exploración'},
    'dimension': {'zh': '维度', 'en': 'Dimension', 'es': 'Dimensión'},
    'click_count': {'zh': '点击次数', 'en': 'Click Count', 'es': 'Cantidad de Clics'},
    'click_dist': {'zh': '各维度点击分布', 'en': 'Click Distribution by Dimension', 'es': 'Distribución de Clics por Dimensión'},
    'concepts_count': {'zh': '已探索词汇数', 'en': 'Concepts Explored', 'es': 'Conceptos Explorados'},
    'concepts_dist': {'zh': '各维度已探索词汇数量', 'en': 'Concepts Explored by Dimension', 'es': 'Conceptos por Dimensión'},
    'timeline_header': {'zh': '⏱️ 探索时间线', 'en': '⏱️ Exploration Timeline', 'es': '⏱️ Línea de Tiempo'},
    'time': {'zh': '时间', 'en': 'Time', 'es': 'Tiempo'},
    'concept': {'zh': '概念', 'en': 'Concept', 'es': 'Concepto'},
    'timeline_title': {'zh': '您的探索时间轴', 'en': 'Your Exploration Timeline', 'es': 'Tu Línea de Tiempo de Exploración'},
    'timeline_caption': {'zh': '💡 横轴表示时间，纵轴表示您点击的概念，颜色表示维度', 'en': '💡 X-axis = time, Y-axis = concepts clicked, color = dimension', 'es': '💡 Eje X = tiempo, Eje Y = conceptos, color = dimensión'},
    'no_history': {'zh': '暂无探索历史数据', 'en': 'No exploration history yet', 'es': 'Sin historial aún'},
    'top_header': {'zh': '🔥 您最感兴趣的词汇 Top 10', 'en': '🔥 Your Top 10 Most Interesting Concepts', 'es': '🔥 Top 10 Conceptos Más Interesantes'},
    'top_title': {'zh': '最感兴趣的词汇（按点击次数）', 'en': 'Most Interesting Concepts (by clicks)', 'es': 'Conceptos Más Interesantes (por clics)'},
    'no_data': {'zh': '暂无数据', 'en': 'No data yet', 'es': 'Sin datos'},
    'ab_header': {'zh': '🧪 您的A/B测试组别', 'en': '🧪 Your A/B Test Group', 'es': '🧪 Tu Grupo de Prueba A/B'},
    'experiment_group': {'zh': '实验组（启用推荐）', 'en': 'Experiment Group (with recommendations)', 'es': 'Grupo Experimental (con recomendaciones)'},
    'control_group': {'zh': '对照组（无推荐）', 'en': 'Control Group (no recommendations)', 'es': 'Grupo de Control (sin recomendaciones)'},
    'your_group': {'zh': '您的分组', 'en': 'Your Group', 'es': 'Tu Grupo'},
    'diversity_score': {'zh': '探索多样性分数', 'en': 'Exploration Diversity Score', 'es': 'Puntuación de Diversidad'},
    'diversity_caption': {'zh': '探索了多少个不同维度 / 总维度数', 'en': 'Different dimensions explored / total dimensions', 'es': 'Dimensiones exploradas / total'},
    'metric': {'zh': '指标', 'en': 'Metric', 'es': 'Métrica'},
    'value': {'zh': '数值', 'en': 'Value', 'es': 'Valor'},
    'm_dim': {'zh': '探索维度数', 'en': 'Dimensions Explored', 'es': 'Dimensiones Exploradas'},
    'm_concepts': {'zh': '探索词汇数', 'en': 'Concepts Explored', 'es': 'Conceptos Explorados'},
    'm_clicks': {'zh': '总点击次数', 'en': 'Total Clicks', 'es': 'Clics Totales'},
    'm_session': {'zh': '会话时长(分钟)', 'en': 'Session Duration (min)', 'es': 'Duración (min)'},
    'ab_explanation': {
        'zh': '''
**关于A/B测试：**
- **实验组**：系统会推荐您未探索的维度中的概念（防信息茧房）
- **对照组**：不提供推荐，完全自由探索

这个实验用于评估推荐系统是否能提高探索多样性！
''',
        'en': '''
**About A/B Test:**
- **Experiment Group**: System recommends concepts from unexplored dimensions (anti-filter bubble)
- **Control Group**: No recommendations, completely free exploration

This experiment evaluates whether the recommendation system improves exploration diversity!
''',
        'es': '''
**Sobre la Prueba A/B:**
- **Grupo Experimental**: El sistema recomienda conceptos de dimensiones no exploradas
- **Grupo de Control**: Sin recomendaciones, exploración completamente libre

¡Este experimento evalúa si el sistema de recomendación mejora la diversidad de exploración!
'''
    },
    'pages_header': {'zh': '📑 页面访问统计', 'en': '📑 Page Visit Statistics', 'es': '📑 Estadísticas de Visitas'},
    'page': {'zh': '页面', 'en': 'Page', 'es': 'Página'},
    'visits': {'zh': '访问次数', 'en': 'Visit Count', 'es': 'Visitas'},
    'pages_title': {'zh': '各页面访问比例', 'en': 'Page Visit Ratio', 'es': 'Proporción de Visitas'},
    'no_pages': {'zh': '暂无页面访问数据', 'en': 'No page visit data yet', 'es': 'Sin datos de visitas aún'},
    'continue': {'zh': '🧭 继续探索', 'en': '🧭 Continue Exploring', 'es': '🧭 Continuar Explorando'},
    'nav_global': {'zh': '📊 全局语义偏移', 'en': '📊 Global Overview', 'es': '📊 Visión Global'},
    'nav_bloc': {'zh': '🌍 阵营对比分析', 'en': '🌍 Bloc Analysis', 'es': '🌍 Análisis de Bloques'},
    'nav_consistency': {'zh': '✅ 言行一致性', 'en': '✅ Consistency Check', 'es': '✅ Verificación'}
}

initialize_user_profile()
record_page_view("User Dashboard")

if 'user_profile' not in st.session_state:
    st.error(T['no_profile'][current_lang])
    st.stop()

profile = st.session_state.user_profile

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

st.markdown("---")

if len(profile.get('clicked_concepts', {})) == 0:
    st.info(T['no_exploration'][current_lang])
    st.stop()

# 1. 基本统计
st.header(T['stats_header'][current_lang])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(T['total_concepts'][current_lang], len(profile.get('clicked_concepts', {})))

with col2:
    total_clicks_val = profile.get('total_clicks', 0)
    if total_clicks_val == 0 and 'click_counts' in profile:
        total_clicks_val = sum(profile['click_counts'].values())
    st.metric(T['total_clicks'][current_lang], total_clicks_val)

with col3:
    explored_dims = sum(1 for v in profile.get('interest_weights', {}).values() if v > 0)
    st.metric(T['dimensions_explored'][current_lang], f"{explored_dims}/6")

with col4:
    session_start = profile.get('session_start', datetime.now())
    if isinstance(session_start, str):
        try:
            from dateutil import parser
            session_start = parser.parse(session_start)
        except:
            session_start = datetime.now()
    session_time_val = (datetime.now() - session_start).total_seconds() / 60
    st.metric(T['session_time'][current_lang], f"{session_time_val:.1f} {T['minutes'][current_lang]}")

st.markdown("---")

# 2. 兴趣雷达图
st.header(T['radar_header'][current_lang])

dimensions = list(profile.get('interest_weights', {}).keys())
values = list(profile.get('interest_weights', {}).values())

if values:
    max_value = max(values) if max(values) > 0 else 1
    normalized_values = [v / max_value * 100 for v in values]
    short_dims = [d.split(":")[0] for d in dimensions]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=short_dims,
        fill='toself',
        name=T['interest_intensity'][current_lang],
        line_color='#3498db',
        fillcolor='rgba(52, 152, 219, 0.3)'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=500,
        title=T['radar_title'][current_lang]
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.caption(T['radar_caption'][current_lang])

st.markdown("---")

# 3. 维度分布柱状图
st.header(T['distribution_header'][current_lang])

col1, col2 = st.columns(2)

with col1:
    short_dims = [d.split(":")[0] for d in dimensions]
    dim_df = pd.DataFrame({T['dimension'][current_lang]: short_dims, T['click_count'][current_lang]: values})
    
    fig_bar = px.bar(
        dim_df,
        x=T['dimension'][current_lang],
        y=T['click_count'][current_lang],
        color=T['click_count'][current_lang],
        color_continuous_scale='Blues',
        title=T['click_dist'][current_lang]
    )
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    dimensions_obj = get_six_dimensions()
    concept_counts = {}
    for dim, concepts in dimensions_obj.items():
        clicked_in_dim = [c for c in concepts if c in profile.get('clicked_concepts', {})]
        concept_counts[dim.split(":")[0]] = len(clicked_in_dim)
    
    count_df = pd.DataFrame({
        T['dimension'][current_lang]: list(concept_counts.keys()),
        T['concepts_count'][current_lang]: list(concept_counts.values())
    })
    
    fig_count = px.bar(
        count_df,
        x=T['dimension'][current_lang],
        y=T['concepts_count'][current_lang],
        color=T['concepts_count'][current_lang],
        color_continuous_scale='Greens',
        title=T['concepts_dist'][current_lang]
    )
    fig_count.update_layout(height=400)
    st.plotly_chart(fig_count, use_container_width=True)

st.markdown("---")

# 4. 探索时间线
st.header(T['timeline_header'][current_lang])

if len(profile.get('click_history', [])) > 0:
    timeline_data = []
    for item in profile['click_history']:
        timeline_data.append({
            T['time'][current_lang]: item['timestamp'],
            T['concept'][current_lang]: item['concept'],
            T['dimension'][current_lang]: item['dimension'].split(":")[0]
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    fig_timeline = px.scatter(
        timeline_df,
        x=T['time'][current_lang],
        y=T['concept'][current_lang],
        color=T['dimension'][current_lang],
        title=T['timeline_title'][current_lang],
        hover_data=[T['dimension'][current_lang]]
    )
    fig_timeline.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_timeline, use_container_width=True)
    st.caption(T['timeline_caption'][current_lang])
else:
    st.info(T['no_history'][current_lang])

st.markdown("---")

# 5. Top 10 词汇
st.header(T['top_header'][current_lang])

click_counts = profile.get('click_counts', {})
if not click_counts:
    # 尝试从clicked_concepts构建
    clicked = profile.get('clicked_concepts', {})
    if isinstance(clicked, dict):
        click_counts = clicked

if len(click_counts) > 0:
    sorted_concepts = sorted(click_counts.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 1, reverse=True)[:10]
    top_concepts = [c[0] for c in sorted_concepts]
    top_counts = [c[1] if isinstance(c[1], (int, float)) else 1 for c in sorted_concepts]
    
    fig_top = px.bar(
        x=top_counts,
        y=top_concepts,
        orientation='h',
        labels={'x': T['click_count'][current_lang], 'y': T['concept'][current_lang]},
        title=T['top_title'][current_lang],
        color=top_counts,
        color_continuous_scale='Reds'
    )
    fig_top.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.info(T['no_data'][current_lang])

st.markdown("---")

# 6. A/B测试指标
st.header(T['ab_header'][current_lang])

metrics = get_ab_test_metrics()

if metrics:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        group_name = T['experiment_group'][current_lang] if metrics.get('group') == 'experiment' else T['control_group'][current_lang]
        st.metric(T['your_group'][current_lang], group_name)
        st.metric(T['diversity_score'][current_lang], f"{metrics.get('diversity_score', 0):.2%}")
        st.caption(T['diversity_caption'][current_lang])
    
    with col2:
        metrics_df = pd.DataFrame({
            T['metric'][current_lang]: [
                T['m_dim'][current_lang],
                T['m_concepts'][current_lang],
                T['m_clicks'][current_lang],
                T['m_session'][current_lang]
            ],
            T['value'][current_lang]: [
                f"{metrics.get('explored_dimensions', 0)}/6",
                metrics.get('total_concepts', 0),
                metrics.get('total_clicks', 0),
                metrics.get('session_duration_minutes', 0)
            ]
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        st.info(T['ab_explanation'][current_lang])

st.markdown("---")

# 7. 页面访问统计
st.header(T['pages_header'][current_lang])

if len(profile.get('page_views', {})) > 0:
    page_df = pd.DataFrame({
        T['page'][current_lang]: list(profile['page_views'].keys()),
        T['visits'][current_lang]: list(profile['page_views'].values())
    })
    
    fig_pages = px.pie(
        page_df,
        names=T['page'][current_lang],
        values=T['visits'][current_lang],
        title=T['pages_title'][current_lang]
    )
    fig_pages.update_layout(height=400)
    st.plotly_chart(fig_pages, use_container_width=True)
else:
    st.info(T['no_pages'][current_lang])

st.markdown("---")
st.markdown(f"### {T['continue'][current_lang]}")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_📊_Global_Overview.py", label=T['nav_global'][current_lang])
with col2:
    st.page_link("pages/2_🌍_Bloc_Analysis.py", label=T['nav_bloc'][current_lang])
with col3:
    st.page_link("pages/3_✅_Consistency_Check.py", label=T['nav_consistency'][current_lang])
