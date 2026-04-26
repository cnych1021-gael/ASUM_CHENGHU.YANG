import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

# 从 Secrets 中获取表格 URL
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# ==================== 数据库读写逻辑 ====================

def get_gsheets_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def load_user_registry_from_sheets():
    conn = get_gsheets_conn()
    try:
        # 显式传递 spreadsheet 参数以防止 UnsupportedOperationError
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Registry")
        if df.empty: return {}
        df['user_id'] = df['user_id'].astype(str)
        return df.set_index('user_id').to_dict('index')
    except Exception:
        return {}

def save_user_profile_to_sheets(user_profile):
    conn = get_gsheets_conn()
    try:
        existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Registry")
    except:
        existing_df = pd.DataFrame()
    
    new_entry = pd.DataFrame([user_profile])
    if not existing_df.empty:
        existing_df['user_id'] = existing_df['user_id'].astype(str)
        user_id_str = str(user_profile['user_id'])
        if user_id_str in existing_df['user_id'].values:
            existing_df = existing_df[existing_df['user_id'] != user_id_str]
        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    else:
        updated_df = new_entry
    
    # 显式传递 spreadsheet 修复权限报错
    conn.update(spreadsheet=SHEET_URL, worksheet="Registry", data=updated_df)

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    conn = get_gsheets_conn()
    user_profile = st.session_state.get('user_profile', {})
    ab_group = user_profile.get('ab_group', 'unknown')
    
    new_record = pd.DataFrame([{
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_id': str(user_id),
        'action': action,
        'concept': concept,
        'dimension': dimension,
        'page': page,
        'ab_group': ab_group
    }])
    
    try:
        existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Interactions")
        updated_df = pd.concat([existing_df, new_record], ignore_index=True)
    except:
        updated_df = new_record
        
    conn.update(spreadsheet=SHEET_URL, worksheet="Interactions", data=updated_df)

# ==================== 用户逻辑 ====================

def update_user_activity(user_id):
    """更新活跃时间（已改为通过 Interactions 记录，此处留空防止报错）"""
    pass

def generate_user_id(name, institution):
    raw = f"{name}_{institution}_{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def assign_ab_group():
    return 'experiment' if random.random() > 0.5 else 'control'

def register_user(name, institution, role, language='zh'):
    user_id = generate_user_id(name, institution)
    ab_group = assign_ab_group()
    user_profile = {
        'user_id': user_id, 'name': name, 'institution': institution,
        'role': role, 'language': language, 'ab_group': ab_group,
        'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_user_profile_to_sheets(user_profile)
    return user_id, ab_group

# ==================== UI 界面 ====================

def show_user_login_page(language='zh'):
    texts = {
        'zh': {
            'welcome': '欢迎！请先告诉我们关于您的信息', 'identity': '您的身份是？',
            'name': '您的姓名：', 'institution': '您的机构：', 'start': '开始探索',
            'novice': '🎓 学生/新手', 'expert': '👔 研究员/专家',
            'required': '⚠️ 请填写所有项', 'welcome_back': '欢迎回来',
            'novice_desc': '新手模式：包含简化图表和推荐。',
            'expert_desc': '专家模式：包含完整分析工具。'
        },
        'en': {
            'welcome': 'Welcome!', 'identity': 'Your profile:',
            'name': 'Name:', 'institution': 'Institution:', 'start': 'Start',
            'novice': '🎓 Novice', 'expert': '👔 Expert',
            'required': '⚠️ Required fields', 'welcome_back': 'Welcome',
            'novice_desc': 'Novice: Simple charts & reco.',
            'expert_desc': 'Expert: Full tools.'
        }
    }
    t = texts.get(language, texts['zh'])
    st.header(t['welcome'])
    
    identity = st.radio(t['identity'], [t['novice'], t['expert']])
    selected_role = 'novice' if t['novice'] in identity else 'expert'
    st.info(t['novice_desc'] if selected_role == 'novice' else t['expert_desc'])
    
    user_name = st.text_input(t['name'], key="reg_name")
    user_inst = st.text_input(t['institution'], key="reg_inst")
    
    if st.button(t['start'], type="primary"):
        if not user_name or not user_inst:
            st.error(t['required'])
            return False
        
        user_id, ab_group = register_user(user_name, user_inst, selected_role, language)
        st.session_state.user_profile = {
            'user_id': user_id, 'name': user_name, 'institution': user_inst,
            'role': selected_role, 'language': language, 'ab_group': ab_group
        }
        return True
    return False

def get_ab_test_statistics():
    return {} # 简化版    conn.update(spreadsheet=SHEET_URL, worksheet="Registry", data=updated_df)

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    """记录交互到 Interactions 表"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 获取 AB 组（从 session 拿，减少读取次数）
    user_profile = st.session_state.get('user_profile', {})
    ab_group = user_profile.get('ab_group', 'unknown')
    
    new_record = pd.DataFrame([{
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_id': str(user_id),
        'action': action,
        'concept': concept,
        'dimension': dimension,
        'page': page,
        'ab_group': ab_group
    }])
    
    try:
        # 同样显式传 URL
        existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Interactions")
        updated_df = pd.concat([existing_df, new_record], ignore_index=True)
    except:
        updated_df = new_record
        
    # 【关键修改】显式传入 spreadsheet 参数
    conn.update(spreadsheet=SHEET_URL, worksheet="Interactions", data=updated_df)
