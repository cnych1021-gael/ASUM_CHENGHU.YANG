"""
演示模式用户切换器

用于课程展示时快速切换不同用户，查看A/B测试效果
"""

import streamlit as st
import json
from pathlib import Path

def load_demo_users():
    """加载演示用户数据"""
    try:
        users_file = Path('data/ab_test_users/users_full.json')
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"加载演示用户失败: {e}")
        return []

def demo_user_switcher():
    """在侧边栏显示用户切换器（仅演示模式）"""
    
    # 检查是否启用演示模式
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
    # 演示模式切换
    with st.sidebar:
        st.markdown("---")
        demo_mode = st.checkbox(
            "🎓 演示模式",
            value=st.session_state.demo_mode,
            help="启用后可快速切换不同用户查看A/B测试效果"
        )
        
        if demo_mode != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_mode
            st.rerun()
        
        if st.session_state.demo_mode:
            st.markdown("### 👤 用户切换")
            
            # 加载演示用户
            demo_users = load_demo_users()
            
            if not demo_users:
                st.warning("⚠️ 未找到演示用户数据")
                st.info("""
                请先运行：
                ```bash
                python generate_ab_test_users.py
                ```
                """)
                return
            
            # 创建用户选择器
            user_options = {}
            for user in demo_users:
                label = (
                    f"{user['user_id']} "
                    f"({'实验组' if user['ab_group'] == 'experiment' else '对照组'}) "
                    f"- {user['user_type']}"
                )
                user_options[label] = user
            
            selected_label = st.selectbox(
                "选择用户：",
                options=list(user_options.keys()),
                key='demo_user_selector'
            )
            
            selected_user = user_options[selected_label]
            
            # 显示用户信息
            st.markdown(f"""
            **用户信息：**
            - ID: {selected_user['user_id']}
            - 分组: {'🧪 实验组' if selected_user['ab_group'] == 'experiment' else '🔬 对照组'}
            - 类型: {selected_user['user_type']}
            - 点击数: {len(selected_user['click_history'])}
            - 探索维度: {selected_user['explored_dimensions']}/6
            - 多样性: {selected_user['diversity_score']:.2f}
            """)
            
            # 加载该用户的数据到session_state
            if st.button("切换到此用户", key='switch_user_btn'):
                load_demo_user_data(selected_user)
                st.success(f"✅ 已切换到 {selected_user['user_id']}")
                st.rerun()
            
            # 快速对比按钮
            st.markdown("---")
            st.markdown("**快速对比：**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("对照组示例", key='ctrl_example'):
                    ctrl_user = next((u for u in demo_users if u['ab_group'] == 'control'), None)
                    if ctrl_user:
                        load_demo_user_data(ctrl_user)
                        st.rerun()
            
            with col2:
                if st.button("实验组示例", key='exp_example'):
                    exp_user = next((u for u in demo_users if u['ab_group'] == 'experiment'), None)
                    if exp_user:
                        load_demo_user_data(exp_user)
                        st.rerun()

def load_demo_user_data(user_data):
    """加载演示用户数据到session_state"""
    
    # 基本信息
    st.session_state.user_profile = {
        'role': user_data['user_type'],
        'language': 'zh',
        'ab_group': user_data['ab_group'],
        'diversity_score': user_data['diversity_score'],
        'explored_dimensions': user_data['explored_dimensions'],
        'session_duration': user_data['session_duration']
    }
    
    # 点击历史
    click_history = {}
    for click in user_data['click_history']:
        concept = click['concept']
        if concept not in click_history:
            click_history[concept] = 0
        click_history[concept] += 1
    
    st.session_state.click_history = click_history
    
    # 探索的概念
    st.session_state.explored_concepts = set(user_data['explored_concepts'])
    
    # 页面访问记录
    st.session_state.page_views = {
        'Global_Overview': 3,
        'Bloc_Analysis': 2,
        'Consistency_Check': 1,
        'User_Dashboard': 1
    }
    
    # 演示标记
    st.session_state.demo_user_id = user_data['user_id']
    st.session_state.demo_user_group = user_data['ab_group']

# 在app.py中调用
if __name__ == '__main__':
    st.sidebar.markdown("# 用户切换器测试")
    demo_user_switcher()
