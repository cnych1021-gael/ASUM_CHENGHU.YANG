"""用户模型 - 简化版"""
import streamlit as st
from datetime import datetime
import random

def initialize_user_profile():
    """初始化用户档案"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'user_id': None,
            'name': None,
            'role': 'novice',  # novice 或 expert
            'institution': None,
            'ab_group': 'experiment',  # experiment 或 control
            'login_time': None,
            'clicked_concepts': {},  # {concept: count}
            'viewed_pages': [],
            'interest_weights': {},  # {dimension: weight}
            'interactions': []
        }

def is_expert_mode():
    """是否为专家模式"""
    initialize_user_profile()
    return st.session_state.user_profile.get('role') == 'expert'

def record_concept_click(concept, dimension=None):
    """记录概念点击"""
    initialize_user_profile()
    profile = st.session_state.user_profile
    
    if 'clicked_concepts' not in profile:
        profile['clicked_concepts'] = {}
    
    profile['clicked_concepts'][concept] = profile['clicked_concepts'].get(concept, 0) + 1
    
    if dimension:
        if 'interest_weights' not in profile:
            profile['interest_weights'] = {}
        profile['interest_weights'][dimension] = profile['interest_weights'].get(dimension, 0) + 1
    
    profile['interactions'].append({
        'type': 'concept_click',
        'concept': concept,
        'dimension': dimension,
        'time': datetime.now().isoformat()
    })

def record_page_view(page):
    """记录页面访问"""
    initialize_user_profile()
    profile = st.session_state.user_profile
    profile['viewed_pages'].append({
        'page': page,
        'time': datetime.now().isoformat()
    })

def get_user_stats():
    """获取用户统计"""
    initialize_user_profile()
    profile = st.session_state.user_profile
    return {
        '已点击概念': len(profile.get('clicked_concepts', {})),
        '访问页面': len(set([p['page'] for p in profile.get('viewed_pages', [])])),
        '总交互': len(profile.get('interactions', []))
    }

def get_serendipity_recommendations(all_concepts, n=2):
    """惊喜推荐：从未探索的维度推荐"""
    initialize_user_profile()
    profile = st.session_state.user_profile
    
    # 用户已点击的概念
    clicked = set(profile.get('clicked_concepts', {}).keys())
    
    # 找未探索的维度
    interest_weights = profile.get('interest_weights', {})
    unexplored_dims = [dim for dim in all_concepts.keys() if dim not in interest_weights]
    
    recommendations = []
    
    if unexplored_dims:
        # 从未探索的维度选概念
        for dim in unexplored_dims:
            for concept in all_concepts[dim]:
                if concept not in clicked:
                    recommendations.append(concept)
                    if len(recommendations) >= n:
                        return recommendations
    
    # 如果未探索维度不够，从所有维度找
    if len(recommendations) < n:
        for dim, concepts in all_concepts.items():
            for concept in concepts:
                if concept not in clicked and concept not in recommendations:
                    recommendations.append(concept)
                    if len(recommendations) >= n:
                        return recommendations
    
    return recommendations

def get_collaborative_recommendations(simulated_users, all_concepts, user_weights, n=2):
    """协同过滤推荐"""
    if not user_weights:
        return []
    
    # 找相似用户
    similarities = []
    for uid, udata in simulated_users.items():
        sim_weights = udata.get('interest_weights', {})
        # 简单相似度：共同维度数
        common = set(user_weights.keys()) & set(sim_weights.keys())
        if common:
            similarities.append((uid, len(common), udata))
    
    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # 从最相似的用户那里获取推荐
    initialize_user_profile()
    clicked = set(st.session_state.user_profile.get('clicked_concepts', {}).keys())
    
    recommendations = []
    for uid, sim, udata in similarities[:3]:
        for concept in udata.get('clicked_concepts', []):
            if concept not in clicked and concept not in recommendations:
                recommendations.append(concept)
                if len(recommendations) >= n:
                    return recommendations
    
    return recommendations

def get_ab_test_metrics():
    """获取A/B测试指标"""
    initialize_user_profile()
    profile = st.session_state.user_profile
    return {
        'group': profile.get('ab_group', 'unknown'),
        'concepts_clicked': len(profile.get('clicked_concepts', {})),
        'pages_viewed': len(set([p['page'] for p in profile.get('viewed_pages', [])])),
        'session_duration_minutes': 0  # 简化
    }
