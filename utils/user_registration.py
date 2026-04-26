import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

# 1. 从 Secrets 获取表格 ID
SHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"]

def get_gsheets_conn():
    """建立连接：会自动读取 Secrets 中 connections.gsheets 下的所有平铺参数"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_user_registry_from_sheets():
    conn = get_gsheets_conn()
    try:
        # 使用 ttl=0 确保每次都读到最新数据，不使用缓存
        df = conn.read(spreadsheet=SHEET_ID, worksheet="Registry", ttl=0)
        if df.empty:
            return {}
        df['user_id'] = df['user_id'].astype(str)
        return df.set_index('user_id').to_dict('index')
    except Exception:
        return {}

def save_user_profile_to_sheets(user_profile):
    conn = get_gsheets_conn()
    try:
        # 读取现有数据
        try:
            existing_df = conn.read(spreadsheet=SHEET_ID, worksheet="Registry", ttl=0)
        except:
            existing_df = pd.DataFrame()
        
        # 强制将新数据转为字符串，避免类型不兼容
        new_entry = pd.DataFrame([user_profile]).astype(str)
        
        if not existing_df.empty:
            existing_df['user_id'] = existing_df['user_id'].astype(str)
            user_id_str = str(user_profile['user_id'])
            # 如果 ID 已存在则替换
            if user_id_str in existing_df['user_id'].values:
                existing_df = existing_df[existing_df['user_id'] != user_id_str]
            updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
        else:
            updated_df = new_entry
        
        # 执行更新
        conn.update(spreadsheet=SHEET_ID, worksheet="Registry", data=updated_df)
        return True
    except Exception as e:
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
        except:
            updated_df = new_record
            
        conn.update(spreadsheet=SHEET_ID, worksheet="Interactions", data=updated_df)
    except Exception:
        pass

def update_user_activity(user_id):
    """保留接口防止 app.py 报错"""
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
    st.header("用户注册 / User Registration")
    
    # 简单的 UI 逻辑
    user_name = st.text_input("您的姓名 / Your Name", key="login_name_v3")
    user_inst = st.text_input("您的机构 / Your Institution", key="login_inst_v3")
    mode = st.selectbox("选择模式 / Select Mode", ["新手模式 / Novice", "专家模式 / Expert"])
    
    if st.button("进入系统 / Enter System", type="primary", use_container_width=True):
        if user_name and user_inst:
            role = 'novice' if "新手" in mode else 'expert'
            user_id, ab_group = register_user(user_name, user_inst, role, language)
            
            if user_id:
                st.session_state.user_profile = {
                    'user_id': user_id,
                    'name': user_name,
                    'institution': user_inst,
                    'role': role,
                    'language': language,
                    'ab_group': ab_group
                }
                st.success("✅ 登录成功！数据已同步至 Google Sheets。")
                st.balloons()
                st.rerun()
        else:
            st.warning("⚠️ 请填写姓名和机构。")
    return False

def get_ab_test_statistics():
    """获取统计数据的空接口"""
    return {}        return True
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
