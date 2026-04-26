"""
全局语言管理器

功能：
1. 统一语言设置存储
2. 跨页面语言同步
3. 语言切换组件
"""

import streamlit as st

def initialize_language():
    """初始化语言设置"""
    if 'global_language' not in st.session_state:
        st.session_state.global_language = 'zh'  # 默认中文

def get_global_language():
    """获取当前语言"""
    initialize_language()
    return st.session_state.global_language

def set_global_language(language):
    """设置全局语言"""
    st.session_state.global_language = language
    # 同步到用户profile
    if 'user_profile' in st.session_state and st.session_state.user_profile:
        st.session_state.user_profile['language'] = language

def show_language_selector():
    """
    显示语言选择器（放在页面顶部）
    
    Returns:
        str: 当前选择的语言
    """
    current_lang = get_global_language()
    
    # 语言选择按钮
    col1, col2, col3, col4 = st.columns([5, 1.2, 1.2, 1.2])
    
    with col2:
        if st.button(
            "🇨🇳 中文" if current_lang != 'zh' else "✅ 中文",
            key="lang_zh_selector",
            use_container_width=True
        ):
            set_global_language('zh')
            st.rerun()
    
    with col3:
        if st.button(
            "🇬🇧 English" if current_lang != 'en' else "✅ English",
            key="lang_en_selector",
            use_container_width=True
        ):
            set_global_language('en')
            st.rerun()
    
    with col4:
        if st.button(
            "🇪🇸 Español" if current_lang != 'es' else "✅ Español",
            key="lang_es_selector",
            use_container_width=True
        ):
            set_global_language('es')
            st.rerun()
    
    return current_lang

# 通用文本翻译
def get_text(key, lang=None):
    """
    获取翻译文本
    
    Args:
        key: 文本键
        lang: 语言（如果为None则使用全局语言）
    
    Returns:
        str: 翻译后的文本
    """
    if lang is None:
        lang = get_global_language()
    
    texts = {
        # 通用
        'app_title': {
            'zh': '🌐 联合国语义演变自适应分析平台',
            'en': '🌐 UN Semantic Evolution Analysis Platform',
            'es': '🌐 Plataforma de Análisis de Evolución Semántica de la ONU'
        },
        'app_subtitle': {
            'zh': 'UN General Debate Semantic Evolution Analysis (1971-2025)',
            'en': 'UN General Debate Semantic Evolution Analysis (1971-2025)',
            'es': 'Análisis de Evolución Semántica del Debate General de la ONU (1971-2025)'
        },
        
        # 导航
        'global_overview': {
            'zh': '📊 全局语义偏移',
            'en': '📊 Global Overview',
            'es': '📊 Visión General'
        },
        'bloc_analysis': {
            'zh': '🌍 阵营对比分析',
            'en': '🌍 Bloc Analysis',
            'es': '🌍 Análisis de Bloques'
        },
        'consistency_check': {
            'zh': '✅ 言行一致性',
            'en': '✅ Consistency Check',
            'es': '✅ Verificación de Consistencia'
        },
        'expert_lab': {
            'zh': '🔬 专家实验室',
            'en': '🔬 Expert Lab',
            'es': '🔬 Laboratorio Experto'
        },
        'user_dashboard': {
            'zh': '📈 用户仪表板',
            'en': '📈 User Dashboard',
            'es': '📈 Panel de Usuario'
        },
        'ab_test': {
            'zh': '🧪 A/B测试',
            'en': '🧪 A/B Test',
            'es': '🧪 Prueba A/B'
        },
        
        # 用户画像
        'your_profile': {
            'zh': '👤 您的画像',
            'en': '👤 Your Profile',
            'es': '👤 Tu Perfil'
        },
        'reset_profile': {
            'zh': '🔄 重置画像',
            'en': '🔄 Reset Profile',
            'es': '🔄 Restablecer Perfil'
        },
        'logout': {
            'zh': '🚪 退出登录',
            'en': '🚪 Logout',
            'es': '🚪 Cerrar Sesión'
        },
        
        # 统计
        'explore_count': {
            'zh': '探索次数',
            'en': 'Explorations',
            'es': 'Exploraciones'
        },
        'interest_dims': {
            'zh': '兴趣维度',
            'en': 'Interest Dimensions',
            'es': 'Dimensiones de Interés'
        },
        'session_time': {
            'zh': '会话时长',
            'en': 'Session Time',
            'es': 'Tiempo de Sesión'
        }
    }
    
    return texts.get(key, {}).get(lang, texts.get(key, {}).get('zh', key))

__all__ = [
    'initialize_language',
    'get_global_language',
    'set_global_language',
    'show_language_selector',
    'get_text'
]
