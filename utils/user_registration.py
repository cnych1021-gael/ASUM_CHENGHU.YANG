import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

try:
    SHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"]
except Exception:
    SHEET_ID = ""

def get_gsheets_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def save_user_profile_to_sheets(user_profile):
    conn = get_gsheets_conn()
    try:
        try:
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Registry", ttl=0)
        except Exception:
            existing_df = pd.DataFrame()
        
        new_entry = pd.DataFrame([user_profile]).astype(str)
        
        if not existing_df.empty:
            existing_df['user_id'] = existing_df['user_id'].astype(str)
            user_id_str = str(user_profile['user_id'])
            if user_id_str in existing_df['user_id'].values:
                existing_df = existing_df[existing_df['user_id'] != user_id_str]
            updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
        else:
            updated_df = new_entry
        
        conn.update(spreadsheet=SHEET_ID, worksheet="Registry", data=updated_df)
        return True
    except Exception as e:
        # 【关键修改】如果错误信息里包含 200，说明其实是成功写入了！直接放行！
        if "200" in str(e):
            return True
        st.error(f"写入 Registry 失败: {e}")
        return False

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    conn = get_gsheets_conn()
    try:
        user_profile = st.session_state.get('user_profile', {})
        ab_group = user_profile.get('ab_group', 'unknown')
        
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
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Interactions", ttl=0)
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
        except Exception:
            updated_df = new_record
            
        conn.update(spreadsheet=SHEET_ID, worksheet="Interactions", data=updated_df)
    except Exception:
        # 这里哪怕遇到 200 也会静默跳过，不影响用户体验
        pass

def update_user_activity(user_id):
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
        'user_id': user_id, 
        'name': name, 
        'institution': institution,
        'role': role, 
        'language': language, 
        'ab_group': ab_group,
        'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if save_user_profile_to_sheets(user_profile):
        return user_id, ab_group
    return None, None

def show_user_login_page(language='zh'):
    st.header("用户注册 / Registration")
    user_name = st.text_input("您的姓名 / Your Name", key="u_name")
    user_inst = st.text_input("您的机构 / Your Institution", key="u_inst")
    mode = st.selectbox("模式 / Mode", ["新手 / Novice", "专家 / Expert"])
    
    if st.button("进入 / Enter", type="primary"):
        if user_name and user_inst:
            role = 'novice' if "新手" in mode else 'expert'
            user_id, ab_group = register_user(user_name, user_inst, role, language)
            if user_id:
                st.session_state.user_profile = {
                    'user_id': user_id, 'name': user_name, 'institution': user_inst,
                    'role': role, 'language': language, 'ab_group': ab_group
                }
                st.success("✅ 登录成功！")
                st.rerun()
        else:
            st.warning("⚠️ 请完整填写。")
    return False

def get_ab_test_statistics():
    return {}    except Exception as e:
        st.error(f"写入 Registry 失败: {e}")
        return False

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    conn = get_gsheets_conn()
    try:
        user_profile = st.session_state.get('user_profile', {})
        ab_group = user_profile.get('ab_group', 'unknown')
        
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
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Interactions", ttl=0)
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
        except Exception:
            updated_df = new_record
            
        conn.update(spreadsheet=SHEET_ID, worksheet="Interactions", data=updated_df)
    except Exception:
        pass

def update_user_activity(user_id):
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
        'user_id': user_id, 
        'name': name, 
        'institution': institution,
        'role': role, 
        'language': language, 
        'ab_group': ab_group,
        'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if save_user_profile_to_sheets(user_profile):
        return user_id, ab_group
    return None, None

def show_user_login_page(language='zh'):
    st.header("用户注册 / Registration")
    user_name = st.text_input("您的姓名 / Your Name", key="u_name")
    user_inst = st.text_input("您的机构 / Your Institution", key="u_inst")
    mode = st.selectbox("模式 / Mode", ["新手 / Novice", "专家 / Expert"])
    
    if st.button("进入 / Enter", type="primary"):
        if user_name and user_inst:
            role = 'novice' if "新手" in mode else 'expert'
            user_id, ab_group = register_user(user_name, user_inst, role, language)
            if user_id:
                st.session_state.user_profile = {
                    'user_id': user_id, 'name': user_name, 'institution': user_inst,
                    'role': role, 'language': language, 'ab_group': ab_group
                }
                st.success("✅ 登录成功！")
                st.rerun()
        else:
            st.warning("⚠️ 请完整填写。")
    return False

def get_ab_test_statistics():
    return {}
