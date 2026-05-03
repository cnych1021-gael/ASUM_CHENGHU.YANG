"""用户中心 - 个人统计与学习路径"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.user_model import initialize_user_profile, get_user_stats, get_ab_test_metrics
from utils.data_loader import get_six_dimensions
from utils.language_manager import get_global_language

st.set_page_config(page_title="User Dashboard", page_icon="👤", layout="wide")

current_lang = get_global_language()
initialize_user_profile()

T = {
    'title': {'zh': '👤 用户中心', 'en': '👤 User Dashboard', 'es': '👤 Panel de Usuario'},
    'subtitle': {'zh': '您的探索数据与学习路径', 'en': 'Your Exploration Data', 'es': 'Tus Datos de Exploración'},
    'profile': {'zh': '📋 个人资料', 'en': '📋 Profile', 'es': '📋 Perfil'},
    'name': {'zh': '姓名', 'en': 'Name', 'es': 'Nombre'},
    'role': {'zh': '角色', 'en': 'Role', 'es': 'Rol'},
    'institution': {'zh': '机构', 'en': 'Institution', 'es': 'Institución'},
    'ab_group': {'zh': 'A/B 组', 'en': 'A/B Group', 'es': 'Grupo A/B'},
    'login_time': {'zh': '登录时间', 'en': 'Login Time', 'es': 'Hora'},
    'stats': {'zh': '📊 探索统计', 'en': '📊 Stats', 'es': '📊 Estadísticas'},
    'concepts_explored': {'zh': '探索的概念', 'en': 'Concepts Explored', 'es': 'Conceptos'},
    'pages_visited': {'zh': '访问的页面', 'en': 'Pages Visited', 'es': 'Páginas'},
    'total_clicks': {'zh': '总交互', 'en': 'Total Interactions', 'es': 'Total'},
    'top_concepts': {'zh': '🔥 最关注的概念 Top 10', 'en': '🔥 Top 10 Concepts', 'es': '🔥 Top 10'},
    'interest_dist': {'zh': '🎯 兴趣维度分布', 'en': '🎯 Interest Distribution', 'es': '🎯 Distribución'},
    'no_data': {'zh': '暂无数据，请先去探索！', 'en': 'No data yet, start exploring!', 'es': '¡Empieza a explorar!'},
    'recommend_path': {'zh': '🗺️ 推荐学习路径', 'en': '🗺️ Recommended Path', 'es': '🗺️ Ruta Recomendada'},
    'next_concepts': {'zh': '建议下一步探索：', 'en': 'Suggested next:', 'es': 'Siguiente:'},
}

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

profile = st.session_state.user_profile

# 个人资料
st.markdown("---")
st.header(T['profile'][current_lang])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(T['name'][current_lang], profile.get('name', 'N/A'))
    role_display = {
        'novice': '🎓 新手' if current_lang == 'zh' else '🎓 Novice' if current_lang == 'en' else '🎓 Principiante',
        'expert': '🔬 专家' if current_lang == 'zh' else '🔬 Expert' if current_lang == 'en' else '🔬 Experto'
    }
    st.metric(T['role'][current_lang], role_display.get(profile.get('role', 'novice')))
with col2:
    st.metric(T['institution'][current_lang], profile.get('institution', 'N/A'))
    st.metric(T['ab_group'][current_lang], profile.get('ab_group', 'unknown'))
with col3:
    login_time = profile.get('login_time', '')
    if login_time:
        login_time = login_time.split('T')[0] + ' ' + login_time.split('T')[1][:8]
    st.metric(T['login_time'][current_lang], login_time or 'N/A')

st.markdown("---")

# 探索统计
st.header(T['stats'][current_lang])

stats = get_user_stats()
col1, col2, col3 = st.columns(3)
col1.metric(T['concepts_explored'][current_lang], stats.get('已点击概念', 0))
col2.metric(T['pages_visited'][current_lang], stats.get('访问页面', 0))
col3.metric(T['total_clicks'][current_lang], stats.get('总交互', 0))

st.markdown("---")

# Top 概念
clicked_concepts = profile.get('clicked_concepts', {})
if clicked_concepts:
    st.header(T['top_concepts'][current_lang])
    
    sorted_concepts = sorted(clicked_concepts.items(), key=lambda x: x[1], reverse=True)[:10]
    df_top = pd.DataFrame(sorted_concepts, columns=['Concept', 'Clicks'])
    
    fig = px.bar(df_top, x='Clicks', y='Concept', orientation='h',
                 color='Clicks', color_continuous_scale='Viridis')
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(T['no_data'][current_lang])

# 兴趣分布
interest_weights = profile.get('interest_weights', {})
if interest_weights:
    st.markdown("---")
    st.header(T['interest_dist'][current_lang])
    
    df_interest = pd.DataFrame(list(interest_weights.items()), columns=['Dimension', 'Weight'])
    
    fig = px.pie(df_interest, values='Weight', names='Dimension',
                 title="兴趣维度分布")
    st.plotly_chart(fig, use_container_width=True)

# 学习路径推荐
st.markdown("---")
st.header(T['recommend_path'][current_lang])

dimensions = get_six_dimensions()
viewed = set(clicked_concepts.keys())
unexplored = []
for dim, concepts in dimensions.items():
    for c in concepts:
        if c not in viewed:
            unexplored.append((c, dim))
            if len(unexplored) >= 5:
                break
    if len(unexplored) >= 5:
        break

if unexplored:
    st.markdown(f"**{T['next_concepts'][current_lang]}**")
    for c, dim in unexplored[:5]:
        st.info(f"• **{c}** ({dim})")
