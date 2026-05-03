"""用户登录系统 - 简化版（无需Google Sheets）"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import random

# 本地存储用户数据
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

def load_users():
    """加载用户数据"""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """保存用户数据"""
    USERS_FILE.parent.mkdir(exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def show_user_login_page(language='zh'):
    """显示登录/注册页面"""
    
    texts = {
        'zh': {
            'welcome': '欢迎使用联合国语义演变分析平台',
            'subtitle': '请选择您的角色和登录方式',
            'tab_login': '🔐 登录',
            'tab_register': '📝 注册新用户',
            'tab_demo': '🎮 演示模式',
            'username': '用户名',
            'password': '密码',
            'name': '姓名',
            'institution': '机构/学校',
            'role': '选择角色',
            'novice': '🎓 新手模式 - 简化界面，适合初学者',
            'expert': '🔬 专家模式 - 完整功能，适合研究者',
            'login_btn': '登录',
            'register_btn': '注册',
            'demo_novice': '👶 体验新手模式',
            'demo_expert': '🎓 体验专家模式',
            'login_success': '登录成功！',
            'wrong_pwd': '用户名或密码错误',
            'user_exists': '用户名已存在',
            'register_success': '注册成功！请登录',
            'fill_all': '请填写所有字段'
        },
        'en': {
            'welcome': 'Welcome to UN Semantic Evolution Analysis',
            'subtitle': 'Please select your role and login method',
            'tab_login': '🔐 Login',
            'tab_register': '📝 Register',
            'tab_demo': '🎮 Demo Mode',
            'username': 'Username',
            'password': 'Password',
            'name': 'Name',
            'institution': 'Institution',
            'role': 'Select Role',
            'novice': '🎓 Novice - Simplified interface for beginners',
            'expert': '🔬 Expert - Full features for researchers',
            'login_btn': 'Login',
            'register_btn': 'Register',
            'demo_novice': '👶 Try Novice Mode',
            'demo_expert': '🎓 Try Expert Mode',
            'login_success': 'Login successful!',
            'wrong_pwd': 'Wrong username or password',
            'user_exists': 'Username already exists',
            'register_success': 'Registration successful! Please login',
            'fill_all': 'Please fill all fields'
        },
        'es': {
            'welcome': 'Bienvenido al Análisis de Evolución Semántica ONU',
            'subtitle': 'Selecciona tu rol y método de inicio',
            'tab_login': '🔐 Iniciar Sesión',
            'tab_register': '📝 Registrarse',
            'tab_demo': '🎮 Modo Demo',
            'username': 'Usuario',
            'password': 'Contraseña',
            'name': 'Nombre',
            'institution': 'Institución',
            'role': 'Seleccionar Rol',
            'novice': '🎓 Principiante - Interfaz simplificada',
            'expert': '🔬 Experto - Funciones completas',
            'login_btn': 'Iniciar',
            'register_btn': 'Registrar',
            'demo_novice': '👶 Probar Principiante',
            'demo_expert': '🎓 Probar Experto',
            'login_success': '¡Inicio exitoso!',
            'wrong_pwd': 'Usuario o contraseña incorrectos',
            'user_exists': 'Usuario ya existe',
            'register_success': '¡Registro exitoso! Inicia sesión',
            'fill_all': 'Llena todos los campos'
        }
    }
    
    t = texts.get(language, texts['zh'])
    
    st.markdown(f"## {t['welcome']}")
    st.markdown(f"### {t['subtitle']}")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([t['tab_login'], t['tab_register'], t['tab_demo']])
    
    # Tab 1: 登录
    with tab1:
        with st.form("login_form"):
            username = st.text_input(t['username'], key="login_user")
            password = st.text_input(t['password'], type="password", key="login_pwd")
            submit = st.form_submit_button(t['login_btn'], type="primary")
            
            if submit:
                if not username or not password:
                    st.error(t['fill_all'])
                    return False
                
                users = load_users()
                if username in users and users[username]['password'] == password:
                    # 登录成功
                    user_data = users[username]
                    st.session_state.user_profile = {
                        'user_id': username,
                        'name': user_data.get('name', username),
                        'role': user_data.get('role', 'novice'),
                        'institution': user_data.get('institution', ''),
                        'ab_group': user_data.get('ab_group', random.choice(['experiment', 'control'])),
                        'login_time': datetime.now().isoformat(),
                        'clicked_concepts': {},
                        'viewed_pages': [],
                        'interest_weights': {},
                        'interactions': []
                    }
                    st.success(t['login_success'])
                    return True
                else:
                    st.error(t['wrong_pwd'])
                    return False
    
    # Tab 2: 注册
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input(t['username'], key="reg_user")
            new_password = st.text_input(t['password'], type="password", key="reg_pwd")
            new_name = st.text_input(t['name'], key="reg_name")
            new_institution = st.text_input(t['institution'], key="reg_inst")
            new_role = st.radio(
                t['role'],
                options=['novice', 'expert'],
                format_func=lambda x: t['novice'] if x == 'novice' else t['expert']
            )
            submit_reg = st.form_submit_button(t['register_btn'], type="primary")
            
            if submit_reg:
                if not all([new_username, new_password, new_name]):
                    st.error(t['fill_all'])
                    return False
                
                users = load_users()
                if new_username in users:
                    st.error(t['user_exists'])
                    return False
                
                users[new_username] = {
                    'password': new_password,
                    'name': new_name,
                    'institution': new_institution,
                    'role': new_role,
                    'ab_group': random.choice(['experiment', 'control']),
                    'created_at': datetime.now().isoformat()
                }
                save_users(users)
                st.success(t['register_success'])
                return False
    
    # Tab 3: 演示模式
    with tab3:
        st.info("🎮 " + ("快速体验，无需注册" if language == 'zh' else "Quick demo, no registration" if language == 'en' else "Demo rápido, sin registro"))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t['demo_novice'], use_container_width=True, type="primary"):
                st.session_state.user_profile = {
                    'user_id': f'demo_novice_{random.randint(1000, 9999)}',
                    'name': 'Demo User (Novice)',
                    'role': 'novice',
                    'institution': 'Demo',
                    'ab_group': 'experiment',
                    'login_time': datetime.now().isoformat(),
                    'clicked_concepts': {},
                    'viewed_pages': [],
                    'interest_weights': {},
                    'interactions': []
                }
                return True
        
        with col2:
            if st.button(t['demo_expert'], use_container_width=True, type="primary"):
                st.session_state.user_profile = {
                    'user_id': f'demo_expert_{random.randint(1000, 9999)}',
                    'name': 'Demo User (Expert)',
                    'role': 'expert',
                    'institution': 'Demo',
                    'ab_group': 'experiment',
                    'login_time': datetime.now().isoformat(),
                    'clicked_concepts': {},
                    'viewed_pages': [],
                    'interest_weights': {},
                    'interactions': []
                }
                return True
    
    return False

def update_user_activity(user_id):
    """更新用户活动"""
    pass  # 简化版

def record_user_interaction(user_id, action, page):
    """记录用户交互"""
    if 'user_profile' in st.session_state:
        if 'interactions' not in st.session_state.user_profile:
            st.session_state.user_profile['interactions'] = []
        st.session_state.user_profile['interactions'].append({
            'action': action,
            'page': page,
            'time': datetime.now().isoformat()
        })
