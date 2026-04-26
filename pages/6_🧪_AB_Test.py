"""
A/B Test Evaluation Framework - Multilingual (zh/en/es)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.user_model import initialize_user_profile, is_expert_mode
from utils.language_manager import get_global_language
import json
from datetime import datetime

st.set_page_config(page_title="A/B Test", page_icon="🧪", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '🧪 A/B测试评估框架', 'en': '🧪 A/B Test Evaluation Framework', 'es': '🧪 Marco de Evaluación A/B'},
    'subtitle': {'zh': '评估推荐系统对用户探索行为的影响', 'en': 'Evaluating Recommendation System Impact on Exploration', 'es': 'Evaluando el Impacto del Sistema de Recomendación'},
    'access_denied': {'zh': '🔒 此页面仅限专家模式访问', 'en': '🔒 Expert Mode Required', 'es': '🔒 Se Requiere Modo Experto'},
    'expert_required': {'zh': 'A/B测试评估需要专业知识，请返回首页切换为专家模式', 'en': 'A/B Test evaluation requires expertise. Please return to home and switch to Expert Mode.', 'es': 'La evaluación A/B requiere experiencia. Por favor regrese a inicio y cambie al Modo Experto.'},
    'back_home': {'zh': '🏠 返回首页', 'en': '🏠 Back to Home', 'es': '🏠 Volver al Inicio'},
    'about_test': {'zh': '📖 关于这个A/B测试', 'en': '📖 About This A/B Test', 'es': '📖 Sobre Esta Prueba A/B'},
    'test_design': {
        'zh': '''
## 实验设计

**研究问题：** 防信息茧房推荐系统是否能提高用户的探索多样性？

**实验组设置：**
- **实验组 (Experiment)**：启用serendipity推荐，系统会主动推荐用户未探索的维度
- **对照组 (Control)**：不提供推荐，用户完全自由探索

**关键指标（KPI）：**
1. **探索多样性分数**：用户探索了多少个不同维度 (0-1)
2. **跨维度点击率**：点击来自不同维度的概念的比例
3. **会话时长**：用户在系统中停留的总时间
4. **总探索词汇数**：用户点击的不同概念数量

**假设（Hypothesis）：**
- H0（零假设）：推荐系统不影响探索多样性
- H1（备择假设）：推荐系统显著提高探索多样性
''',
        'en': '''
## Experiment Design

**Research Question:** Can anti-filter-bubble recommendation systems increase user exploration diversity?

**Group Setup:**
- **Experiment Group**: Serendipity recommendations enabled, system actively recommends unexplored dimensions
- **Control Group**: No recommendations provided, completely free exploration

**Key Performance Indicators (KPIs):**
1. **Exploration Diversity Score**: How many different dimensions explored (0-1)
2. **Cross-Dimension Click Rate**: Proportion of clicks from different dimensions
3. **Session Duration**: Total time spent in the system
4. **Total Concepts Explored**: Number of distinct concepts clicked

**Hypothesis:**
- H0 (Null): The recommendation system does not affect exploration diversity
- H1 (Alternative): The recommendation system significantly improves exploration diversity
''',
        'es': '''
## Diseño del Experimento

**Pregunta de Investigación:** ¿Puede el sistema de recomendación anti-burbuja aumentar la diversidad de exploración?

**Configuración de Grupos:**
- **Grupo Experimental**: Recomendaciones de serendipia activadas, el sistema recomienda dimensiones no exploradas
- **Grupo de Control**: Sin recomendaciones, exploración completamente libre

**Indicadores Clave (KPI):**
1. **Puntuación de Diversidad**: Cuántas dimensiones diferentes exploradas (0-1)
2. **Tasa de Clics Inter-dimensión**: Proporción de clics de diferentes dimensiones
3. **Duración de Sesión**: Tiempo total en el sistema
4. **Conceptos Totales Explorados**: Número de conceptos distintos clicados

**Hipótesis:**
- H0 (Nula): El sistema no afecta la diversidad de exploración
- H1 (Alternativa): El sistema mejora significativamente la diversidad
'''
    },
    'experiment_data': {'zh': '📊 实验数据', 'en': '📊 Experiment Data', 'es': '📊 Datos del Experimento'},
    'simulate_check': {'zh': '📊 生成模拟数据（用于演示）', 'en': '📊 Generate Simulated Data (for demo)', 'es': '📊 Generar Datos Simulados (demo)'},
    'simulate_success': {'zh': '✅ 已生成 50 个模拟用户数据', 'en': '✅ Generated 50 simulated user data', 'es': '✅ Generados 50 usuarios simulados'},
    'current_data': {'zh': '📊 当前实验数据：共 {} 位用户', 'en': '📊 Current data: {} users total', 'es': '📊 Datos actuales: {} usuarios'},
    'insufficient_data': {'zh': "⚠️ 数据量不足，请勾选上方'生成模拟数据'或等待更多真实用户使用系统", 'en': "⚠️ Insufficient data. Please check 'Generate Simulated Data' above or wait for more real users", 'es': "⚠️ Datos insuficientes. Marque 'Generar Datos Simulados' o espere más usuarios"},
    'comparison_analysis': {'zh': '📈 对比分析', 'en': '📈 Comparative Analysis', 'es': '📈 Análisis Comparativo'},
    'key_metrics': {'zh': '🎯 关键指标对比', 'en': '🎯 Key Metrics Comparison', 'es': '🎯 Comparación de Métricas'},
    'control_users': {'zh': '对照组用户数', 'en': 'Control Group Users', 'es': 'Usuarios Grupo Control'},
    'experiment_users': {'zh': '实验组用户数', 'en': 'Experiment Group Users', 'es': 'Usuarios Grupo Experimental'},
    'diversity_improvement': {'zh': '多样性提升', 'en': 'Diversity Improvement', 'es': 'Mejora de Diversidad'},
    'distribution_compare': {'zh': '📦 探索多样性分布对比', 'en': '📦 Diversity Distribution Comparison', 'es': '📦 Comparación de Distribución de Diversidad'},
    'control': {'zh': '对照组', 'en': 'Control', 'es': 'Control'},
    'experiment': {'zh': '实验组', 'en': 'Experiment', 'es': 'Experimental'},
    'box_title': {'zh': '探索多样性分数分布（箱线图）', 'en': 'Diversity Score Distribution (Box Plot)', 'es': 'Distribución de Puntuación de Diversidad (Diagrama de Caja)'},
    'diversity_score_label': {'zh': '多样性分数 (0-1)', 'en': 'Diversity Score (0-1)', 'es': 'Puntuación de Diversidad (0-1)'},
    'avg_metrics': {'zh': '📊 平均指标对比', 'en': '📊 Average Metrics Comparison', 'es': '📊 Comparación de Métricas Promedio'},
    'metric': {'zh': '指标', 'en': 'Metric', 'es': 'Métrica'},
    'control_avg': {'zh': '对照组均值', 'en': 'Control Mean', 'es': 'Media Control'},
    'experiment_avg': {'zh': '实验组均值', 'en': 'Experiment Mean', 'es': 'Media Experimental'},
    'difference': {'zh': '差异', 'en': 'Difference', 'es': 'Diferencia'},
    'm_diversity': {'zh': '探索多样性分数', 'en': 'Diversity Score', 'es': 'Puntuación de Diversidad'},
    'm_dim': {'zh': '探索维度数', 'en': 'Dimensions Explored', 'es': 'Dimensiones Exploradas'},
    'm_concepts': {'zh': '探索词汇数', 'en': 'Concepts Explored', 'es': 'Conceptos Explorados'},
    'm_clicks': {'zh': '总点击次数', 'en': 'Total Clicks', 'es': 'Clics Totales'},
    'm_session': {'zh': '会话时长(分钟)', 'en': 'Session Duration (min)', 'es': 'Duración (min)'},
    'scatter_header': {'zh': '🔍 探索多样性 vs 探索数量', 'en': '🔍 Diversity vs Quantity', 'es': '🔍 Diversidad vs Cantidad'},
    'concepts_total': {'zh': '探索词汇总数', 'en': 'Total Concepts', 'es': 'Total Conceptos'},
    'group': {'zh': '分组', 'en': 'Group', 'es': 'Grupo'},
    'scatter_title': {'zh': '探索数量与多样性的关系', 'en': 'Relationship between Quantity and Diversity', 'es': 'Relación entre Cantidad y Diversidad'},
    'scatter_caption': {'zh': '💡 观察：实验组用户是否在探索数量相近的情况下，多样性更高？', 'en': '💡 Observation: Does the experiment group show higher diversity at similar exploration counts?', 'es': '💡 Observación: ¿El grupo experimental muestra mayor diversidad?'},
    'significance': {'zh': '📊 统计显著性检验', 'en': '📊 Statistical Significance Test', 'es': '📊 Prueba de Significancia Estadística'},
    't_stat': {'zh': 'T统计量', 'en': 'T-statistic', 'es': 'Estadístico T'},
    'p_value': {'zh': 'P值', 'en': 'P-value', 'es': 'Valor P'},
    'significant': {
        'zh': '✅ **结果显著！** (p < 0.05)\n\n在95%置信水平下，我们可以拒绝零假设。\n**结论：推荐系统显著提高了用户的探索多样性。**',
        'en': '✅ **Significant Result!** (p < 0.05)\n\nAt 95% confidence level, we reject the null hypothesis.\n**Conclusion: The recommendation system significantly improves exploration diversity.**',
        'es': '✅ **¡Resultado Significativo!** (p < 0.05)\n\nAl nivel de confianza del 95%, rechazamos la hipótesis nula.\n**Conclusión: El sistema mejora significativamente la diversidad.**'
    },
    'not_significant': {
        'zh': '⚠️ **结果不显著** (p ≥ 0.05)\n\n无法拒绝零假设。\n**结论：推荐系统对探索多样性的影响不显著，可能需要更多数据或改进算法。**',
        'en': '⚠️ **Not Significant** (p ≥ 0.05)\n\nCannot reject null hypothesis.\n**Conclusion: The impact is not significant, may need more data or algorithm improvement.**',
        'es': '⚠️ **No Significativo** (p ≥ 0.05)\n\nNo se puede rechazar la hipótesis nula.\n**Conclusión: Impacto no significativo, se necesitan más datos.**'
    },
    'no_scipy': {'zh': '💡 需要安装 scipy 库才能进行统计检验。当前显示描述性统计。', 'en': '💡 scipy library required for statistical tests. Showing descriptive statistics.', 'es': '💡 Se requiere scipy. Mostrando estadísticas descriptivas.'},
    'export': {'zh': '📥 导出数据', 'en': '📥 Export Data', 'es': '📥 Exportar Datos'},
    'download': {'zh': '📥 下载实验数据 (CSV)', 'en': '📥 Download Experiment Data (CSV)', 'es': '📥 Descargar Datos (CSV)'},
    'continue': {'zh': '🧭 返回其他页面', 'en': '🧭 Back to Other Pages', 'es': '🧭 Volver a Otras Páginas'},
    'nav_dashboard': {'zh': '📈 用户画像仪表板', 'en': '📈 User Dashboard', 'es': '📈 Panel de Usuario'},
    'nav_global': {'zh': '📊 全局语义偏移', 'en': '📊 Global Overview', 'es': '📊 Visión Global'},
    'nav_expert': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'}
}

if not is_expert_mode():
    st.error(T['access_denied'][current_lang])
    st.info(T['expert_required'][current_lang])
    st.page_link("app.py", label=T['back_home'][current_lang])
    st.stop()

initialize_user_profile()

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

st.markdown("---")

with st.expander(T['about_test'][current_lang], expanded=True):
    st.markdown(T['test_design'][current_lang])

st.markdown("---")

st.header(T['experiment_data'][current_lang])

if 'ab_test_data' not in st.session_state:
    st.session_state.ab_test_data = {'users': {}, 'last_update': datetime.now()}

# 添加当前用户数据
if 'user_profile' in st.session_state:
    current_user_id = id(st.session_state.user_profile)
    profile = st.session_state.user_profile
    
    interest_weights = profile.get('interest_weights', {})
    explored_dims = sum(1 for v in interest_weights.values() if v > 0)
    
    session_start = profile.get('session_start')
    if session_start:
        if isinstance(session_start, str):
            try:
                from dateutil import parser
                session_start = parser.parse(session_start)
            except:
                session_start = datetime.now()
        session_time = (datetime.now() - session_start).total_seconds() / 60
    else:
        session_time = 0.0
    
    st.session_state.ab_test_data['users'][current_user_id] = {
        'group': profile.get('ab_group', 'control'),
        'role': profile.get('role', 'novice'),
        'explored_dimensions': explored_dims,
        'total_concepts': len(profile.get('clicked_concepts', {})),
        'total_clicks': profile.get('total_clicks', 0),
        'session_duration': session_time,
        'diversity_score': explored_dims / 6 if explored_dims else 0,
        'timestamp': datetime.now()
    }

simulate_data = st.checkbox(T['simulate_check'][current_lang], value=False)

if simulate_data:
    import random
    import numpy as np
    
    st.session_state.ab_test_data['users'] = {}
    
    for i in range(50):
        group = random.choice(['control', 'experiment'])
        
        if group == 'experiment':
            diversity = random.gauss(0.72, 0.15)
            explored_dims = int(diversity * 6)
            total_concepts = random.randint(15, 35)
        else:
            diversity = random.gauss(0.55, 0.18)
            explored_dims = int(diversity * 6)
            total_concepts = random.randint(10, 25)
        
        explored_dims = max(1, min(6, explored_dims))
        diversity = explored_dims / 6
        
        st.session_state.ab_test_data['users'][f'sim_user_{i}'] = {
            'group': group,
            'role': random.choice(['novice', 'expert']),
            'explored_dimensions': explored_dims,
            'total_concepts': total_concepts,
            'total_clicks': total_concepts + random.randint(0, 10),
            'session_duration': random.gauss(12, 5),
            'diversity_score': diversity,
            'timestamp': datetime.now()
        }
    
    st.success(T['simulate_success'][current_lang])

st.info(T['current_data'][current_lang].format(len(st.session_state.ab_test_data['users'])))

st.markdown("---")

if len(st.session_state.ab_test_data['users']) < 5:
    st.warning(T['insufficient_data'][current_lang])
    st.stop()

st.header(T['comparison_analysis'][current_lang])

users_data = st.session_state.ab_test_data['users']
df = pd.DataFrame.from_dict(users_data, orient='index')

control_df = df[df['group'] == 'control']
experiment_df = df[df['group'] == 'experiment']

st.subheader(T['key_metrics'][current_lang])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(T['control_users'][current_lang], len(control_df))

with col2:
    st.metric(T['experiment_users'][current_lang], len(experiment_df))

with col3:
    if len(control_df) > 0 and len(experiment_df) > 0:
        improvement = ((experiment_df['diversity_score'].mean() - control_df['diversity_score'].mean()) / control_df['diversity_score'].mean()) * 100
        st.metric(T['diversity_improvement'][current_lang], f"{improvement:.1f}%",
                  delta=f"{improvement:.1f}%" if improvement > 0 else None)
    else:
        st.metric(T['diversity_improvement'][current_lang], "N/A")

st.markdown("---")

st.subheader(T['distribution_compare'][current_lang])

fig_box = go.Figure()
fig_box.add_trace(go.Box(y=control_df['diversity_score'], name=T['control'][current_lang], marker_color='#e74c3c'))
fig_box.add_trace(go.Box(y=experiment_df['diversity_score'], name=T['experiment'][current_lang], marker_color='#2ecc71'))
fig_box.update_layout(title=T['box_title'][current_lang], yaxis_title=T['diversity_score_label'][current_lang], height=500)
st.plotly_chart(fig_box, use_container_width=True)

st.subheader(T['avg_metrics'][current_lang])

metrics_comparison = pd.DataFrame({
    T['metric'][current_lang]: [T['m_diversity'][current_lang], T['m_dim'][current_lang], T['m_concepts'][current_lang], T['m_clicks'][current_lang], T['m_session'][current_lang]],
    T['control_avg'][current_lang]: [
        f"{control_df['diversity_score'].mean():.3f}",
        f"{control_df['explored_dimensions'].mean():.2f}",
        f"{control_df['total_concepts'].mean():.2f}",
        f"{control_df['total_clicks'].mean():.2f}",
        f"{control_df['session_duration'].mean():.2f}"
    ],
    T['experiment_avg'][current_lang]: [
        f"{experiment_df['diversity_score'].mean():.3f}",
        f"{experiment_df['explored_dimensions'].mean():.2f}",
        f"{experiment_df['total_concepts'].mean():.2f}",
        f"{experiment_df['total_clicks'].mean():.2f}",
        f"{experiment_df['session_duration'].mean():.2f}"
    ],
    T['difference'][current_lang]: [
        f"{(experiment_df['diversity_score'].mean() - control_df['diversity_score'].mean()):.3f}",
        f"{(experiment_df['explored_dimensions'].mean() - control_df['explored_dimensions'].mean()):.2f}",
        f"{(experiment_df['total_concepts'].mean() - control_df['total_concepts'].mean()):.2f}",
        f"{(experiment_df['total_clicks'].mean() - control_df['total_clicks'].mean()):.2f}",
        f"{(experiment_df['session_duration'].mean() - control_df['session_duration'].mean()):.2f}"
    ]
})

st.dataframe(metrics_comparison, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader(T['scatter_header'][current_lang])

fig_scatter = px.scatter(
    df,
    x='total_concepts',
    y='diversity_score',
    color='group',
    color_discrete_map={'control': '#e74c3c', 'experiment': '#2ecc71'},
    labels={
        'total_concepts': T['concepts_total'][current_lang],
        'diversity_score': T['m_diversity'][current_lang],
        'group': T['group'][current_lang]
    },
    title=T['scatter_title'][current_lang],
    hover_data=['explored_dimensions']
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)
st.caption(T['scatter_caption'][current_lang])

st.markdown("---")

st.subheader(T['significance'][current_lang])

try:
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(experiment_df['diversity_score'], control_df['diversity_score'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(T['t_stat'][current_lang], f"{t_stat:.4f}")
    with col2:
        st.metric(T['p_value'][current_lang], f"{p_value:.4f}")
    
    if p_value < 0.05:
        st.success(T['significant'][current_lang])
    else:
        st.warning(T['not_significant'][current_lang])
except ImportError:
    st.info(T['no_scipy'][current_lang])

st.markdown("---")

st.subheader(T['export'][current_lang])

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label=T['download'][current_lang],
    data=csv,
    file_name=f"ab_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown(f"### {T['continue'][current_lang]}")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/5_📈_User_Dashboard.py", label=T['nav_dashboard'][current_lang])
with col2:
    st.page_link("pages/1_📊_Global_Overview.py", label=T['nav_global'][current_lang])
with col3:
    st.page_link("pages/4_🔬_Expert_Lab.py", label=T['nav_expert'][current_lang])
