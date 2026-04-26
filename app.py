import streamlit as st
from utils.user_model import initialize_user_profile, get_user_stats
from utils.data_loader import get_six_dimensions
from utils.demo_user_switcher import demo_user_switcher
from utils.user_registration import show_user_login_page, update_user_activity, record_user_interaction
from utils.language_manager import initialize_language, get_global_language, show_language_selector, get_text

# 页面配置
st.set_page_config(
    page_title="联合国语义演变分析平台",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化
initialize_language()
initialize_user_profile()

# 语言选择器（全局，顶部）
current_lang = show_language_selector()

# 主标题
st.title(get_text('app_title', current_lang))
st.markdown(f"### {get_text('app_subtitle', current_lang)}")

# ==================== 用户登录检查 ====================
# 检查是否需要显示登录页面
show_login = (
    'user_profile' not in st.session_state or 
    not st.session_state.user_profile or
    st.session_state.user_profile.get('user_id') is None  # 改为检查值是否为None
)

if show_login:
    # 显示登录页面
    login_success = show_user_login_page(language=current_lang)
    
    if login_success:
        # 更新用户活跃度
        update_user_activity(st.session_state.user_profile['user_id'])
        # 记录登录事件
        record_user_interaction(
            user_id=st.session_state.user_profile['user_id'],
            action='login',
            page='app'
        )
        st.rerun()
    
    st.stop()  # 登录完成前不显示主页内容

# ==================== 用户已登录 ====================
else:
    role = st.session_state.user_profile['role']
    user_name = st.session_state.user_profile.get('name', 'User')
    user_id = st.session_state.user_profile['user_id']
    ab_group = st.session_state.user_profile.get('ab_group', 'unknown')
    
    # 侧边栏：用户信息
    with st.sidebar:
        st.header(get_text('your_profile', current_lang))
        
        # 显示用户信息
        st.markdown(f"""
        **👤 {user_name}** 🏢 {st.session_state.user_profile.get('institution', 'N/A')}  
        🎭 {'专家模式' if role == 'expert' else '新手模式'}  
        🎯 {f"实验组 (推荐)" if ab_group == 'experiment' else "对照组 (无推荐)"}
        """)
        
        st.markdown("---")
        
        # 用户统计
        stats = get_user_stats()
        if stats:
            for key, value in stats.items():
                st.metric(key, value)
        
        st.markdown("---")
        
        # 退出登录按钮
        if st.button(get_text('logout', current_lang)):
            # 记录登出事件
            record_user_interaction(
                user_id=user_id,
                action='logout',
                page='app'
            )
            # 清除session
            st.session_state.user_profile = {}
            st.rerun()
        
        # 演示模式（仅用于开发测试）
        demo_user_switcher()
    
    # 主页内容
    if ab_group == 'experiment':
        st.success(f"✅ 欢迎回来，{user_name}！您将获得个性化推荐。")
    else:
        st.success(f"✅ 欢迎回来，{user_name}！")
    
    st.markdown("---")
    
    # 项目介绍
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if current_lang == 'zh':
            st.header("📊 关于本平台")
            
            if role == 'expert':
                st.markdown("""
                本平台基于 **Word2Vec** 词嵌入模型和 **Procrustes 对齐算法**，对 1971-2025 年间联合国大会一般性辩论的
                语料库进行历时性语义建模。通过量化 60 个核心政治概念的语义偏移轨迹，系统性比较 P5 国家、全球北方与
                全球南方在国际叙事上的分歧演变。
                
                **核心功能：**
                - 🔬 语义空间对齐与偏移计算
                - 🌍 地缘政治阵营对比分析
                - ✅ 言行一致性交叉验证（演说 vs 投票）
                - 📈 高级可视化：聚类、3D空间、Sankey流图等
                """)
            else:
                st.markdown("""
                这个平台帮助你理解：**联合国各国在过去50年里，关注的话题是如何变化的？**
                
                比如：
                - 🌡️ "气候变化"这个词，在1970年代和今天的含义一样吗？
                - 🕊️ 中美俄英法五大国，谁说的和做的最一致？
                - 🌍 发达国家和发展中国家，在人权问题上的立场差距有多大？
                
                我们用人工智能分析了半个世纪的联合国演讲记录，用简单的图表告诉你答案！
                """)
        
        elif current_lang == 'en':
            st.header("📊 About This Platform")
            
            if role == 'expert':
                st.markdown("""
                This platform uses **Word2Vec** embeddings and **Procrustes alignment** to model semantic evolution
                in UN General Assembly debates (1971-2025). We quantify semantic shifts of 60 core political concepts
                to compare how P5 nations, Global North, and Global South frame international narratives.
                
                **Core Features:**
                - 🔬 Semantic space alignment & shift calculation
                - 🌍 Geopolitical bloc comparison analysis
                - ✅ Speech-action consistency verification
                - 📈 Advanced visualizations: clustering, 3D space, Sankey diagrams
                """)
            else:
                st.markdown("""
                This platform helps you understand: **How have UN countries' priorities changed over 50 years?**
                
                For example:
                - 🌡️ Does "climate change" mean the same today as in the 1970s?
                - 🕊️ Which of the P5 powers shows the most consistency between words and actions?
                - 🌍 How large is the gap between developed and developing nations on human rights?
                
                We use AI to analyze half a century of UN speeches and show you the answers in simple charts!
                """)
        
        else:  # Spanish
            st.header("📊 Sobre Esta Plataforma")
            
            if role == 'expert':
                st.markdown("""
                Esta plataforma utiliza **Word2Vec** y **alineación de Procrustes** para modelar la evolución semántica
                en los debates de la Asamblea General de la ONU (1971-2025). Cuantificamos cambios semánticos de 60
                conceptos políticos para comparar cómo las potencias P5, el Norte Global y el Sur Global enmarcan narrativas.
                
                **Funciones Principales:**
                - 🔬 Alineación de espacios semánticos y cálculo de desplazamiento
                - 🌍 Análisis comparativo de bloques geopolíticos
                - ✅ Verificación de consistencia discurso-acción
                - 📈 Visualizaciones avanzadas: clustering, espacio 3D, diagramas Sankey
                """)
            else:
                st.markdown("""
                Esta plataforma te ayuda a entender: **¿Cómo han cambiado las prioridades de los países de la ONU en 50 años?**
                
                Por ejemplo:
                - 🌡️ ¿"Cambio climático" significa lo mismo hoy que en los años 70?
                - 🕊️ ¿Cuál de las P5 muestra más consistencia entre palabras y acciones?
                - 🌍 ¿Cuán grande es la brecha entre países desarrollados y en desarrollo sobre derechos humanos?
                
                ¡Usamos IA para analizar medio siglo de discursos de la ONU y te mostramos las respuestas en gráficos simples!
                """)
    
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/UN_emblem_blue.svg/1200px-UN_emblem_blue.svg.png", 
                 width=200)
    
    st.markdown("---")
    
    # 快速导航
    nav_texts = {
        'zh': {
            'title': '🧭 从这里开始探索',
            'global': '查看60个核心词汇的整体变化趋势',
            'bloc': 'P5 vs 全球北方 vs 全球南方',
            'consistency': '各国说的和做的是否匹配？',
            'expert': '高级可视化与深度分析',
            'locked': '🔒 专家实验室需要专家模式'
        },
        'en': {
            'title': '🧭 Start Exploring',
            'global': 'View overall trends of 60 core concepts',
            'bloc': 'P5 vs Global North vs Global South',
            'consistency': 'Do countries walk the talk?',
            'expert': 'Advanced visualizations & deep analysis',
            'locked': '🔒 Expert Lab requires Expert Mode'
        },
        'es': {
            'title': '🧭 Comienza a Explorar',
            'global': 'Ver tendencias globales de 60 conceptos',
            'bloc': 'P5 vs Norte Global vs Sur Global',
            'consistency': '¿Los países cumplen lo que dicen?',
            'expert': 'Visualizaciones avanzadas y análisis profundo',
            'locked': '🔒 Laboratorio Experto requiere Modo Experto'
        }
    }
    
    nav_t = nav_texts[current_lang]
    
    st.header(nav_t['title'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.page_link("pages/1_📊_Global_Overview.py", 
                     label=get_text('global_overview', current_lang),
                     help=nav_t['global'])
    
    with col2:
        st.page_link("pages/2_🌍_Bloc_Analysis.py", 
                     label=get_text('bloc_analysis', current_lang),
                     help=nav_t['bloc'])
    
    with col3:
        st.page_link("pages/3_✅_Consistency_Check.py", 
                     label=get_text('consistency_check', current_lang),
                     help=nav_t['consistency'])
    
    with col4:
        if role == 'expert':
            st.page_link("pages/4_🔬_Expert_Lab.py", 
                         label=get_text('expert_lab', current_lang),
                         help=nav_t['expert'])
        else:
            st.info(nav_t['locked'])
    
    # 底部信息
    st.markdown("---")
