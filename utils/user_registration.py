import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import random
from streamlit_gsheets import GSheetsConnection

# ... 前面的 import 保持不变 ...

# 建议在文件开头定义一下 URL，方便调用
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

def save_user_profile_to_sheets(user_profile):
    """将单个用户档案保存/更新到 Registry 表"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # 1. 读取现有数据（显式传 URL）
        existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Registry")
    except:
        existing_df = pd.DataFrame()
    
    new_entry = pd.DataFrame([user_profile])
    
    if existing_df.empty:
        updated_df = new_entry
    else:
        # 转换 ID 为字符串防止匹配失败
        existing_df['user_id'] = existing_df['user_id'].astype(str)
        user_profile_id = str(user_profile['user_id'])
        
        # 如果用户已存在，删掉旧的再加新的
        if user_profile_id in existing_df['user_id'].values:
            existing_df = existing_df[existing_df['user_id'] != user_profile_id]
        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    
    # 2. 【关键修改】显式传入 spreadsheet 参数
    conn.update(spreadsheet=SHEET_URL, worksheet="Registry", data=updated_df)

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
