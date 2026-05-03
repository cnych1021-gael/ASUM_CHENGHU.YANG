"""多语言管理器 - 完整版"""
import streamlit as st

def initialize_language():
    """初始化语言设置"""
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'

def set_global_language(lang='zh'):
    st.session_state.language = lang

def get_global_language():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    return st.session_state.language

def show_language_selector():
    """顶部语言选择器"""
    initialize_language()
    
    col1, col2, col3 = st.columns([6, 2, 1])
    with col3:
        lang_options = {'🇨🇳 中文': 'zh', '🇬🇧 EN': 'en', '🇪🇸 ES': 'es'}
        current_idx = list(lang_options.values()).index(st.session_state.language)
        selected = st.selectbox(
            "Lang",
            list(lang_options.keys()),
            index=current_idx,
            label_visibility="collapsed"
        )
        st.session_state.language = lang_options[selected]
    
    return st.session_state.language

TRANSLATIONS = {
    'app_title': {'zh': '🌐 联合国语义演变分析平台', 'en': '🌐 UN Semantic Evolution Analysis', 'es': '🌐 Análisis de Evolución Semántica ONU'},
    'app_subtitle': {'zh': '基于Word2Vec的60个核心政治概念历时分析（1971-2025）', 'en': 'Word2Vec-based Diachronic Analysis of 60 Political Concepts (1971-2025)', 'es': 'Análisis Diacrónico de 60 Conceptos Políticos basado en Word2Vec (1971-2025)'},
    'global_overview': {'zh': '📊 全局语义偏移', 'en': '📊 Global Overview', 'es': '📊 Visión Global'},
    'bloc_analysis': {'zh': '🌍 阵营对比分析', 'en': '🌍 Bloc Analysis', 'es': '🌍 Análisis de Bloques'},
    'consistency_check': {'zh': '✅ 言行一致性', 'en': '✅ Consistency Check', 'es': '✅ Consistencia'},
    'expert_lab': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'},
    'user_dashboard': {'zh': '👤 用户中心', 'en': '👤 Dashboard', 'es': '👤 Panel'},
    'ab_test': {'zh': '🧪 A/B测试', 'en': '🧪 A/B Test', 'es': '🧪 Prueba A/B'},
    'your_profile': {'zh': '👤 您的账户', 'en': '👤 Your Profile', 'es': '👤 Tu Perfil'},
    'logout': {'zh': '🚪 退出登录', 'en': '🚪 Logout', 'es': '🚪 Cerrar Sesión'},
    'login': {'zh': '🔐 登录', 'en': '🔐 Login', 'es': '🔐 Iniciar Sesión'},
    'register': {'zh': '📝 注册', 'en': '📝 Register', 'es': '📝 Registrarse'},
    'select_role': {'zh': '选择您的角色', 'en': 'Select Your Role', 'es': 'Selecciona Tu Rol'},
    'novice_mode': {'zh': '🎓 新手模式', 'en': '🎓 Novice Mode', 'es': '🎓 Modo Principiante'},
    'expert_mode': {'zh': '🔬 专家模式', 'en': '🔬 Expert Mode', 'es': '🔬 Modo Experto'},
    'ai_explain': {'zh': '🤖 AI深度解释', 'en': '🤖 AI Explanation', 'es': '🤖 Explicación IA'},
    'ai_loading': {'zh': '🤖 AI正在分析...', 'en': '🤖 AI analyzing...', 'es': '🤖 IA analizando...'},
    'ai_generated': {'zh': '✨ AI生成的解释', 'en': '✨ AI-Generated', 'es': '✨ Generado por IA'},
    'ai_disclaimer': {'zh': '💡 由Google Gemini AI生成。仅供学术参考。', 'en': '💡 By Google Gemini AI. Academic reference only.', 'es': '💡 Por Google Gemini IA. Solo referencia académica.'},
}

def get_text(key, lang=None):
    if lang is None:
        lang = get_global_language()
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key]['zh'])
    return key
