"""演示用户切换器 - 用于快速测试不同角色"""
import streamlit as st
from datetime import datetime
import random

def demo_user_switcher():
    """侧边栏的演示用户切换器"""
    with st.expander("🎮 演示模式（开发用）"):
        st.caption("快速切换用户角色和A/B组测试")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎓 切到新手", use_container_width=True, key="demo_novice_btn"):
                st.session_state.user_profile['role'] = 'novice'
                st.rerun()
        
        with col2:
            if st.button("🔬 切到专家", use_container_width=True, key="demo_expert_btn"):
                st.session_state.user_profile['role'] = 'expert'
                st.rerun()
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🧪 实验组", use_container_width=True, key="demo_exp_btn"):
                st.session_state.user_profile['ab_group'] = 'experiment'
                st.rerun()
        with col4:
            if st.button("📊 对照组", use_container_width=True, key="demo_ctrl_btn"):
                st.session_state.user_profile['ab_group'] = 'control'
                st.rerun()
