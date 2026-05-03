"""用户行为追踪"""
import streamlit as st
from datetime import datetime

def init_user_session():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'viewed_concepts': set(),
            'ai_requests': [],
            'interactions': []
        }

def record_concept_view(concept):
    init_user_session()
    st.session_state.user_data['viewed_concepts'].add(concept)
    st.session_state.user_data['interactions'].append({
        'type': 'view', 'concept': concept, 'time': datetime.now().isoformat()
    })

def record_ai_request(concept):
    init_user_session()
    st.session_state.user_data['ai_requests'].append({
        'concept': concept, 'time': datetime.now().isoformat()
    })

def get_user_stats():
    init_user_session()
    data = st.session_state.user_data
    return {
        'total_concepts_viewed': len(data['viewed_concepts']),
        'ai_requests_count': len(data['ai_requests']),
        'total_interactions': len(data['interactions'])
    }

def get_recommended_concepts(current=None):
    init_user_session()
    viewed = st.session_state.user_data['viewed_concepts']
    all_concepts = ["sovereignty", "democracy", "human_right", "globalization", "peace", "climate"]
    return [c for c in all_concepts if c not in viewed and c != current][:3]
