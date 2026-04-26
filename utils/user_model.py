"""
用户模型 - 最终完整版
包含所有页面需要的函数
"""

import streamlit as st
from datetime import datetime
import random

def initialize_user_profile():
    """初始化用户画像（完整版）"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            # 基本信息
            'user_id': None,
            'name': None,
            'institution': None,
            'role': None,
            'language': 'zh',
            'ab_group': 'control',
            'expertise_level': None,
            
            # 时间信息
            'registered_at': None,
            'last_active': None,
            'session_start': datetime.now(),
            
            # 统计信息
            'total_sessions': 0,
            'total_clicks': 0,
            'explored_concepts': [],
            'explored_dimensions': [],
            'clicked_concepts': {},
            'page_views': {},
            'interest_weights': {},
            
            # 分析指标
            'diversity_score': 0.0,
            'session_duration': 0.0
        }
    
    # 确保所有必需的键都存在（向后兼容）
    required_keys = {
        'user_id': None,
        'name': None,
        'institution': None,
        'role': None,
        'language': 'zh',
        'ab_group': 'control',
        'expertise_level': None,
        'registered_at': None,
        'last_active': None,
        'session_start': datetime.now(),
        'total_sessions': 0,
        'total_clicks': 0,
        'explored_concepts': [],
        'explored_dimensions': [],
        'clicked_concepts': {},
        'page_views': {},
        'interest_weights': {},
        'diversity_score': 0.0,
        'session_duration': 0.0
    }
    
    for key, default_value in required_keys.items():
        if key not in st.session_state.user_profile:
            st.session_state.user_profile[key] = default_value
    
    # 确保session_start是datetime对象
    if st.session_state.user_profile.get('session_start') is None:
        st.session_state.user_profile['session_start'] = datetime.now()
    elif isinstance(st.session_state.user_profile['session_start'], str):
        try:
            from dateutil import parser
            st.session_state.user_profile['session_start'] = parser.parse(
                st.session_state.user_profile['session_start']
            )
        except:
            st.session_state.user_profile['session_start'] = datetime.now()

def get_user_stats():
    """获取用户统计信息"""
    if 'user_profile' not in st.session_state:
        return None
    
    profile = st.session_state.user_profile
    
    # 计算探索维度数
    explored_dims = profile.get('explored_dimensions', [])
    if isinstance(explored_dims, set):
        explored_dims = list(explored_dims)
    
    stats = {
        '探索次数': profile.get('total_clicks', 0),
        '兴趣维度': f"{len(explored_dims)}/6",
        '会话时长': f"{profile.get('session_duration', 0):.1f}分钟"
    }
    
    return stats

def get_current_language():
    """获取当前语言"""
    # 优先使用全局语言
    if 'global_language' in st.session_state:
        return st.session_state.global_language
    
    # 其次使用用户profile中的语言
    if 'user_profile' in st.session_state:
        return st.session_state.user_profile.get('language', 'zh')
    
    return 'zh'

def set_language(lang):
    """设置语言"""
    # 设置全局语言
    st.session_state.global_language = lang
    
    # 同步到用户profile
    if 'user_profile' in st.session_state:
        st.session_state.user_profile['language'] = lang

def record_page_view(page_name):
    """记录页面访问"""
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    if 'page_views' not in st.session_state.user_profile:
        st.session_state.user_profile['page_views'] = {}
    
    page_views = st.session_state.user_profile['page_views']
    
    if page_name not in page_views:
        page_views[page_name] = 0
    
    page_views[page_name] += 1

def record_concept_click(concept, dimension=None):
    """记录概念点击"""
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    
    # 点击计数
    if 'clicked_concepts' not in profile:
        profile['clicked_concepts'] = {}
    
    if concept not in profile['clicked_concepts']:
        profile['clicked_concepts'][concept] = 0
    
    profile['clicked_concepts'][concept] += 1
    
    # 总点击数
    profile['total_clicks'] = profile.get('total_clicks', 0) + 1
    
    # 探索的概念
    if 'explored_concepts' not in profile:
        profile['explored_concepts'] = []
    
    if concept not in profile['explored_concepts']:
        profile['explored_concepts'].append(concept)
    
    # 探索的维度
    if dimension:
        if 'explored_dimensions' not in profile:
            profile['explored_dimensions'] = []
        
        if dimension not in profile['explored_dimensions']:
            profile['explored_dimensions'].append(dimension)
    
    # 更新兴趣权重
    if 'interest_weights' not in profile:
        profile['interest_weights'] = {}
    
    if dimension:
        if dimension not in profile['interest_weights']:
            profile['interest_weights'][dimension] = 0
        profile['interest_weights'][dimension] += 1

def get_serendipity_recommendations(all_concepts, n=2):
    """
    获取意外发现推荐
    
    Args:
        all_concepts: 所有可用概念列表
        n: 推荐数量
    
    Returns:
        推荐的概念列表
    """
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    
    # 只为实验组提供推荐
    if profile.get('ab_group') != 'experiment':
        return []
    
    # 获取已探索的概念
    explored = profile.get('explored_concepts', [])
    
    # 未探索的概念
    unexplored = [c for c in all_concepts if c not in explored]
    
    # 随机推荐
    if len(unexplored) > n:
        return random.sample(unexplored, n)
    else:
        return unexplored

def get_collaborative_recommendations(simulated_users=None, all_concepts=None, user_interests=None, n=2):
    """
    获取协同过滤推荐
    
    Args:
        simulated_users: 模拟用户数据（可选）
        all_concepts: 所有可用概念列表
        user_interests: 用户兴趣（可选）
        n: 推荐数量
    
    Returns:
        推荐的概念列表
    """
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    
    # 只为实验组提供推荐
    if profile.get('ab_group') != 'experiment':
        return []
    
    # 如果没有提供all_concepts，使用空列表
    if all_concepts is None:
        all_concepts = []
    
    # 获取已探索的概念
    explored = profile.get('explored_concepts', [])
    
    # 未探索的概念
    unexplored = [c for c in all_concepts if c not in explored]
    
    # 随机推荐
    if len(unexplored) > n:
        return random.sample(unexplored, n)
    else:
        return unexplored

def is_expert_mode():
    """
    检查是否是专家模式
    
    Returns:
        bool: True if expert mode, False otherwise
    """
    if 'user_profile' not in st.session_state:
        return False
    
    profile = st.session_state.user_profile
    return profile.get('role') == 'expert'

def get_user_role():
    """
    获取用户角色
    
    Returns:
        str: 'novice', 'expert', or None
    """
    if 'user_profile' not in st.session_state:
        return None
    
    return st.session_state.user_profile.get('role')

def get_ab_group():
    """
    获取A/B测试分组
    
    Returns:
        str: 'control' or 'experiment'
    """
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    return st.session_state.user_profile.get('ab_group', 'control')

def get_ab_test_metrics():
    """
    获取A/B测试指标
    
    Returns:
        dict: 包含各种指标的字典
    """
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    
    # 计算多样性得分
    explored_dims = profile.get('explored_dimensions', [])
    if isinstance(explored_dims, set):
        explored_dims = list(explored_dims)
    
    diversity_score = len(explored_dims) / 6.0 if explored_dims else 0.0
    
    # 计算会话时长
    session_start = profile.get('session_start')
    if session_start:
        if isinstance(session_start, str):
            try:
                from dateutil import parser
                session_start = parser.parse(session_start)
            except:
                session_start = datetime.now()
        
        try:
            session_time = (datetime.now() - session_start).total_seconds() / 60
        except:
            session_time = 0.0
    else:
        session_time = 0.0
    
    metrics = {
        'total_clicks': profile.get('total_clicks', 0),
        'explored_concepts': len(profile.get('explored_concepts', [])),
        'explored_dimensions': len(explored_dims),
        'diversity_score': diversity_score,
        'session_time': session_time,
        'ab_group': profile.get('ab_group', 'control')
    }
    
    return metrics

def update_diversity_score():
    """更新多样性得分"""
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    explored_dims = profile.get('explored_dimensions', [])
    
    if isinstance(explored_dims, set):
        explored_dims = list(explored_dims)
    
    profile['diversity_score'] = len(explored_dims) / 6.0 if explored_dims else 0.0

def update_session_duration():
    """更新会话时长"""
    if 'user_profile' not in st.session_state:
        initialize_user_profile()
    
    profile = st.session_state.user_profile
    session_start = profile.get('session_start')
    
    if session_start:
        if isinstance(session_start, str):
            try:
                from dateutil import parser
                session_start = parser.parse(session_start)
            except:
                session_start = datetime.now()
        
        try:
            duration = (datetime.now() - session_start).total_seconds() / 60
            profile['session_duration'] = duration
        except:
            profile['session_duration'] = 0.0

# 导出所有函数
__all__ = [
    'initialize_user_profile',
    'get_user_stats',
    'get_current_language',
    'set_language',
    'record_page_view',
    'record_concept_click',
    'get_serendipity_recommendations',
    'get_collaborative_recommendations',
    'is_expert_mode',
    'get_user_role',
    'get_ab_group',
    'get_ab_test_metrics',
    'update_diversity_score',
    'update_session_duration'
]
