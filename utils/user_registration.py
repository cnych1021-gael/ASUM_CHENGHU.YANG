import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

# ==================== 核心：Google Sheets 连接 ====================

def get_gsheets_conn():
    """建立与 Google Sheets 的连接"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_user_registry_from_sheets():
    """从 Google Sheets 读取 Registry 表并转为字典格式"""
    conn = get_gsheets_conn()
    try:
        df = conn.read(worksheet="Registry")
        if df.empty:
            return {}
        # 确保 user_id 是字符串并设为索引
        df['user_id'] = df['user_id'].astype(str)
        return df.set_index('user_id').to_dict('index')
    except Exception:
        return {}

def save_user_profile_to_sheets(user_profile):
    """将单个用户档案保存/更新到 Registry 表"""
    conn = get_gsheets_conn()
    try:
        existing_df = conn.read(worksheet="Registry")
    except:
        existing_df = pd.DataFrame()
    
    new_entry = pd.DataFrame([user_profile])
    
    if existing_df.empty:
        updated_df = new_entry
    else:
        # 如果用户已存在则更新，不存在则追加
        existing_df['user_id'] = existing_df['user_id'].astype(str)
        if user_profile['user_id'] in existing_df['user_id'].values:
            existing_df = existing_df[existing_df['user_id'] != user_profile['user_id']]
        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    
    conn.update(worksheet="Registry", data=updated_df)

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    """【核心写入函数】记录交互到 Interactions 表"""
    conn = get_gsheets_conn()
    
    # 获取 AB 组信息
    user_profile = st.session_state.get('user_profile', {})
    ab_group = user_profile.get('ab_group', 'unknown')
    
    # 准备新记录
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
        existing_df = conn.read(worksheet="Interactions")
        updated_df = pd.concat([existing_df, new_record], ignore_index=True)
    except:
        updated_df = new_record
        
    conn.update(worksheet="Interactions", data=updated_df)

# ==================== 用户逻辑函数 ====================

def generate_user_id(name, institution):
    raw = f"{name}_{institution}_{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def assign_ab_group():
    return 'experiment' if random.random() > 0.5 else 'control'

def register_user(name, institution, role, language='zh'):
    user_id = generate_user_id(name, institution)
    ab_group = assign_ab_group()
    
    user_profile = {
        'user_id': user_id,
        'name': name,
        'institution': institution,
        'role': role,
        'language': language,
        'ab_group': ab_group,
        'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_active': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_sessions': 1,
        'total_clicks': 0
    }
    
    save_user_profile_to_sheets(user_profile)
    return user_id, ab_group

def update_user_activity(user_id):
    # 云端环境下，此功能可简化，主要通过 Interactions 表记录活跃
    pass

# ==================== UI 界面函数 ====================

def show_user_login_page(language='zh'):
    # ... (这里保留你原本的所有 texts 字典内容) ...
    texts = {
        'zh': {
            'welcome': '欢迎！请先告诉我们关于您的信息',
            'identity': '您的身份是？',
            'name': '您的姓名：',
            'institution': '您的机构（学校/企业）：',
            'name_help': '请输入您的真实姓名',
            'institution_help': '例如：马德里康普顿斯大学',
            'novice': '🎓 学生 / 记者（新手模式）',
            'expert': '👔 研究员 / 外交官（专家模式）',
            'start': '开始探索',
            'novice_desc': '**✨ 新手模式包含：**\n- 简化的图表和解释\n- 完整的概念定义\n- 词云可视化\n- 推荐系统',
            'expert_desc': '**🔬 专家模式包含：**\n- 完整的数据分析工具\n- 7个高级页面（含A/B测试）\n- 可下载原始数据\n- 统计显著性检验',
            'required': '⚠️ 请填写所有必填项',
            'welcome_back': '欢迎回来',
            'assigned_group': '您已被分配到',
            'control_group': '对照组（无推荐）',
            'experiment_group': '实验组（有推荐）'
        },
        'en': { 'welcome': 'Welcome!', 'identity': 'Your profile:', 'name': 'Your name:', 'institution': 'Your institution:', 'name_help': 'Enter name', 'institution_help': 'e.g. UCM', 'novice': '🎓 Novice', 'expert': '👔 Expert', 'start': 'Start', 'novice_desc': 'Novice info', 'expert_desc': 'Expert info', 'required': 'Required', 'welcome_back': 'Welcome back', 'assigned_group': 'Group', 'control_group': 'Control', 'experiment_group': 'Experiment' },
        'es': { 'welcome': '¡Bienvenido!', 'identity': 'Tu perfil:', 'name': 'Tu nombre:', 'institution': 'Tu institución:', 'name_help': 'Tu nombre', 'institution_help': 'ej. UCM', 'novice': '🎓 Principiante', 'expert': '👔 Experto', 'start': 'Comenzar', 'novice_desc': 'Info Principiante', 'expert_desc': 'Info Experto', 'required': 'Requerido', 'welcome_back': 'Bienvenido', 'assigned_group': 'Asignado al', 'control_group': 'Control', 'experiment_group': 'Experimental' }
    }
    
    t = texts.get(language, texts['zh'])
    st.markdown("---")
    st.header(f"👤 {t['welcome']}")
    
    identity = st.radio(t['identity'], [t['novice'], t['expert']], key="login_identity")
    selected_role = 'novice' if t['novice'] in identity else 'expert'
    st.info(t['novice_desc'] if selected_role == 'novice' else t['expert_desc'])
    
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input(t['name'], placeholder="Name", key="login_name")
    with col2:
        user_inst = st.text_input(t['institution'], placeholder="Institution", key="login_inst")
    
    if st.button(t['start'], type="primary", use_container_width=True):
        if not user_name or not user_inst:
            st.error(t['required'])
            return False
        
        user_id, ab_group = register_user(user_name, user_inst, selected_role, language)
        st.session_state.user_profile = {
            'user_id': user_id, 'name': user_name, 'institution': user_inst,
            'role': selected_role, 'language': language, 'ab_group': ab_group
        }
        st.success(f"✅ {t['welcome_back']}, {user_name}!")
        st.balloons()
        return True
    return False

def get_ab_test_statistics():
    registry = load_user_registry_from_sheets()
    if not registry: return None
    # ... (保留原有的统计计算逻辑) ...
    return {"total": len(registry)}
