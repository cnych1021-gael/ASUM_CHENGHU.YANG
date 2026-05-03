"""联合国语义演变分析平台 - 主应用"""
import streamlit as st
from utils.user_model import initialize_user_profile, get_user_stats
from utils.user_registration import show_user_login_page, update_user_activity, record_user_interaction
from utils.demo_user_switcher import demo_user_switcher
from utils.language_manager import initialize_language, get_global_language, show_language_selector, get_text
from utils.ai_explainer import is_ai_available, get_ai_status

st.set_page_config(
    page_title="联合国语义演变分析平台",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化
initialize_language()
initialize_user_profile()

# 顶部语言选择器
current_lang = show_language_selector()

# 主标题
st.title(get_text('app_title', current_lang))
st.markdown(f"### {get_text('app_subtitle', current_lang)}")

# 检查登录状态
show_login = (
    'user_profile' not in st.session_state or 
    not st.session_state.user_profile or
    st.session_state.user_profile.get('user_id') is None
)

if show_login:
    # 显示登录页面
    login_success = show_user_login_page(language=current_lang)
    
    if login_success:
        st.rerun()
    
    st.stop()

# 已登录
role = st.session_state.user_profile.get('role', 'novice')
user_name = st.session_state.user_profile.get('name', 'User')
user_id = st.session_state.user_profile['user_id']
ab_group = st.session_state.user_profile.get('ab_group', 'unknown')

# 侧边栏
with st.sidebar:
    st.header(get_text('your_profile', current_lang))
    
    role_label = {
        'zh': {'novice': '🎓 新手模式', 'expert': '🔬 专家模式'},
        'en': {'novice': '🎓 Novice', 'expert': '🔬 Expert'},
        'es': {'novice': '🎓 Principiante', 'expert': '🔬 Experto'}
    }
    
    ab_label = {
        'zh': {'experiment': '🧪 实验组（含推荐）', 'control': '📊 对照组（无推荐）'},
        'en': {'experiment': '🧪 Experiment (with rec)', 'control': '📊 Control (no rec)'},
        'es': {'experiment': '🧪 Experimento', 'control': '📊 Control'}
    }
    
    st.markdown(f"""
    **👤 {user_name}**  
    🏢 {st.session_state.user_profile.get('institution', 'N/A')}  
    🎭 {role_label[current_lang][role]}  
    🎯 {ab_label[current_lang][ab_group]}
    """)
    
    st.markdown("---")
    
    # AI 状态
    st.info(get_ai_status(current_lang))
    
    st.markdown("---")
    
    # 用户统计
    stats = get_user_stats()
    if stats:
        for key, value in stats.items():
            st.metric(key, value)
    
    st.markdown("---")
    
    # 退出登录
    if st.button(get_text('logout', current_lang)):
        st.session_state.user_profile = {}
        st.rerun()
    
    # 演示模式
    demo_user_switcher()

# 主内容
welcome_msg = {
    'zh': f"✅ 欢迎回来，**{user_name}**！" + ("您将获得个性化推荐 🎯" if ab_group == 'experiment' else ""),
    'en': f"✅ Welcome back, **{user_name}**!" + (" You'll get personalized recommendations 🎯" if ab_group == 'experiment' else ""),
    'es': f"✅ ¡Bienvenido, **{user_name}**!" + (" Recibirás recomendaciones 🎯" if ab_group == 'experiment' else "")
}
st.success(welcome_msg[current_lang])

st.markdown("---")

# 项目介绍
col1, col2 = st.columns([2, 1])

with col1:
    intro = {
        'zh': {
            'novice': """
### 📊 关于本平台

这个平台帮助你理解：**联合国各国在过去50年里，关注的话题是如何变化的？**

比如：
- 🌡️ "气候变化"这个词，在1970年代和今天的含义一样吗？
- 🕊️ 中美俄英法五大国，谁说的和做的最一致？
- 🌍 发达国家和发展中国家，在人权问题上的立场差距有多大？

我们用 AI 分析了半个世纪的联合国演讲记录，用简单的图表+AI解释告诉你答案！

**🆕 新功能：AI 深度解释** - 点击任何概念旁的 🤖 按钮，让 AI 为你深入解读！
""",
            'expert': """
### 📊 关于本平台

本平台基于 **Word2Vec** 词嵌入模型和 **Procrustes 对齐算法**，对 1971-2025 年间联合国大会一般性辩论的语料库进行历时性语义建模。

**核心功能：**
- 🔬 语义空间对齐与偏移计算（60个核心概念）
- 🌍 地缘政治阵营对比分析（P5、Global North/South）
- ✅ 言行一致性交叉验证（演说 vs 投票）
- 🤖 **AI 深度解释**（Google Gemini）
- 📈 高级可视化：聚类、3D空间、Sankey流图等
"""
        },
        'en': {
            'novice': """
### 📊 About This Platform

This platform helps you understand: **How have UN countries' priorities changed over 50 years?**

Examples:
- 🌡️ Does "climate change" mean the same today as in the 1970s?
- 🕊️ Which P5 power is most consistent between words and actions?
- 🌍 How wide is the gap between developed and developing nations?

We use **AI** to analyze 50 years of UN speeches with simple charts + AI explanations!

**🆕 New: AI Deep Explanation** - Click 🤖 button next to any concept!
""",
            'expert': """
### 📊 About This Platform

This platform uses **Word2Vec** embeddings and **Procrustes alignment** to model semantic evolution in UN General Assembly debates (1971-2025).

**Core Features:**
- 🔬 Semantic space alignment & shift calculation (60 concepts)
- 🌍 Geopolitical bloc comparison (P5, Global North/South)
- ✅ Speech-action consistency verification
- 🤖 **AI Deep Explanation** (Google Gemini)
- 📈 Advanced visualizations
"""
        },
        'es': {
            'novice': """
### 📊 Sobre Esta Plataforma

Esta plataforma te ayuda a entender: **¿Cómo han cambiado las prioridades de los países de la ONU en 50 años?**

Por ejemplo:
- 🌡️ ¿"Cambio climático" significa lo mismo hoy que en los años 70?
- 🕊️ ¿Cuál de las P5 es más consistente?
- 🌍 ¿Cuán grande es la brecha entre países?

¡Usamos **IA** para analizarlo con gráficos simples + explicaciones de IA!

**🆕 Nuevo: Explicación Profunda IA** - ¡Haz clic en 🤖!
""",
            'expert': """
### 📊 Sobre Esta Plataforma

Plataforma con **Word2Vec** y **Procrustes** para modelar evolución semántica en discursos ONU (1971-2025).

**Funciones:**
- 🔬 Cálculo de cambio semántico (60 conceptos)
- 🌍 Comparación de bloques geopolíticos
- ✅ Verificación discurso-acción
- 🤖 **Explicación IA** (Google Gemini)
- 📈 Visualizaciones avanzadas
"""
        }
    }
    st.markdown(intro[current_lang][role])

with col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/UN_emblem_blue.svg/1200px-UN_emblem_blue.svg.png", width=200)

st.markdown("---")

# 快速导航
nav_title = {'zh': '🧭 从这里开始探索', 'en': '🧭 Start Exploring', 'es': '🧭 Comienza a Explorar'}
st.header(nav_title[current_lang])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/1_📊_Global_Overview.py", 
                 label=get_text('global_overview', current_lang))

with col2:
    st.page_link("pages/2_🌍_Bloc_Analysis.py", 
                 label=get_text('bloc_analysis', current_lang))

with col3:
    st.page_link("pages/3_✅_Consistency_Check.py", 
                 label=get_text('consistency_check', current_lang))

with col4:
    if role == 'expert':
        st.page_link("pages/4_🔬_Expert_Lab.py", 
                     label=get_text('expert_lab', current_lang))
    else:
        locked = {'zh': '🔒 专家模式专享', 'en': '🔒 Expert Only', 'es': '🔒 Solo Experto'}
        st.info(locked[current_lang])

# 第二行导航
col5, col6 = st.columns(2)
with col5:
    st.page_link("pages/5_👤_User_Dashboard.py", 
                 label=get_text('user_dashboard', current_lang))
with col6:
    if role == 'expert':
        st.page_link("pages/6_🧪_AB_Test.py", 
                     label=get_text('ab_test', current_lang))

st.markdown("---")
st.caption({
    'zh': '💡 提示：本平台使用 Google Gemini AI 提供深度解释。所有AI内容仅供学术参考。',
    'en': '💡 Tip: Uses Google Gemini AI for deep explanations. AI content for academic reference only.',
    'es': '💡 Consejo: Usa Google Gemini IA. Contenido solo para referencia académica.'
}[current_lang])
