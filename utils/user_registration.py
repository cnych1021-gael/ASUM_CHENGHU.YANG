import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

# --- 建立连接 ---
def get_gsheets_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def load_user_registry():
    """从 Google Sheets 读取用户注册表"""
    conn = get_gsheets_conn()
    try:
        # 读取 Registry 工作表
        df = conn.read(worksheet="Registry")
        # 将 DataFrame 转换为以 user_id 为键的字典，模拟之前的 json 格式
        if df.empty: return {}
        return df.set_index('user_id').to_dict('index')
    except Exception:
        return {}

def save_user_registry(registry_dict):
    """将整个注册表写回 Google Sheets"""
    conn = get_gsheets_conn()
    # 将字典转回 DataFrame
    df = pd.DataFrame.from_dict(registry_dict, orient='index').reset_index()
    df.rename(columns={'index': 'user_id'}, inplace=True)
    conn.update(worksheet="Registry", data=df)

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    """将交互行为记录到 Google Sheets 的 Interactions 工作表"""
    conn = get_gsheets_conn()
    
    # 1. 获取用户 AB 组信息
    registry = load_user_registry()
    ab_group = registry.get(user_id, {}).get('ab_group', 'unknown')
    
    # 2. 读取现有记录
    try:
        existing_df = conn.read(worksheet="Interactions")
    except:
        existing_df = pd.DataFrame()

    # 3. 创建新记录
    new_record = pd.DataFrame([{
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_id': user_id,
        'action': action,
        'concept': concept,
        'dimension': dimension,
        'page': page,
        'ab_group': ab_group
    }])
    
    # 4. 合并并更新到云端
    updated_df = pd.concat([existing_df, new_record], ignore_index=True)
    conn.update(worksheet="Interactions", data=updated_df)
    
    # 5. 同时更新 Registry 里的点击统计 (可选)
    if concept and user_id in registry:
        registry[user_id]['total_clicks'] = registry[user_id].get('total_clicks', 0) + 1
        save_user_registry(registry)

# --- 保留你原来的逻辑函数，但内部改用云端存储 ---

def generate_user_id(name, institution):
    raw = f"{name}_{institution}_{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def assign_ab_group():
    return 'experiment' if random.random() > 0.5 else 'control'

def register_user(name, institution, role, language='zh'):
    registry = load_user_registry()
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
    
    registry[user_id] = user_profile
    save_user_registry(registry)
    return user_id, ab_group

# --- 你原本的 UI 函数 show_user_login_page 保持不变，它会自动调用上面的新函数 ---
# (此处省略你代码后半部分的 show_user_login_page 内容，保持原样即可)
