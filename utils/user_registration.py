simport streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from streamlit_gsheets import GSheetsConnection

# 直接从 Secrets 获取 ID 或 URL
SHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"]

def get_gsheets_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def save_user_profile_to_sheets(user_profile):
    """保存用户档案"""
    conn = get_gsheets_conn()
    try:
        # 1. 读取现有数据
        try:
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Registry")
        except:
            existing_df = pd.DataFrame()
        
        # 2. 准备新数据，强制全部转为字符串（防止日期格式导致报错）
        new_entry = pd.DataFrame([user_profile]).astype(str)
        
        if not existing_df.empty:
            existing_df['user_id'] = existing_df['user_id'].astype(str)
            user_id_str = str(user_profile['user_id'])
            if user_id_str in existing_df['user_id'].values:
                existing_df = existing_df[existing_df['user_id'] != user_id_str]
            updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
        else:
            updated_df = new_entry
        
        # 3. 写入（显式指定参数）
        conn.update(spreadsheet=SHEET_ID, worksheet="Registry", data=updated_df)
        return True
    except Exception as e:
        st.error(f"写入 Registry 失败: {str(e)}")
        return False

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    """记录交互"""
    conn = get_gsheets_conn()
    try:
        user_profile = st.session_state.get('user_profile', {})
        ab_group = user_profile.get('ab_group', 'unknown')
        
        # 强制所有字段为字符串
        new_record = pd.DataFrame([{
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_id': str(user_id),
            'action': str(action),
            'concept': str(concept) if concept else "",
            'dimension': str(dimension) if dimension else "",
            'page': str(page) if page else "",
            'ab_group': str(ab_group)
        }]).astype(str)
        
        try:
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Interactions")
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
        except:
            updated_df = new_record
            
        conn.update(spreadsheet=SHEET_ID, worksheet="Interactions", data=updated_df)
    except Exception as e:
        st.write(f"日志记录后台跳过: {e}")

# ==================== 必须保留的其他函数 ====================

def update_user_activity(user_id):
    pass

def generate_user_id(name, institution):
    raw = f"{name}_{institution}_{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def assign_ab_group():
    import random
    return 'experiment' if random.random() > 0.5 else 'control'

def register_user(name, institution, role, language='zh'):
    user_id = generate_user_id(name, institution)
    ab_group = assign_ab_group()
    user_profile = {
        'user_id': user_id, 'name': name, 'institution': institution,
        'role': role, 'language': language, 'ab_group': ab_group,
        'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if save_user_profile_to_sheets(user_profile):
        return user_id, ab_group
    return None, None

def show_user_login_page(language='zh'):
    st.header("用户注册 / User Registration")
    user_name = st.text_input("姓名 / Name", key="reg_name_final")
    user_inst = st.text_input("机构 / Institution", key="reg_inst_final")
    role = st.selectbox("模式 / Mode", ["新手 / Novice", "专家 / Expert"])
    
    if st.button("开始 / Start", type="primary"):
        if user_name and user_inst:
            selected_role = 'novice' if "新手" in role else 'expert'
            user_id, ab_group = register_user(user_name, user_inst, selected_role, language)
            if user_id:
                st.session_state.user_profile = {
                    'user_id': user_id, 'name': user_name, 'institution': user_inst,
                    'role': selected_role, 'language': language, 'ab_group': ab_group
                }
                st.success("注册成功！数据已同步至云端。")
                st.rerun()
        else:
            st.warning("请填写完整信息。")
    return False

def get_ab_test_statistics():
    return {}
