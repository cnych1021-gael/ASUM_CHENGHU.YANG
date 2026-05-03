"""数据加载器"""
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

@st.cache_data
def load_60_concepts():
    return pd.read_csv(DATA_DIR / "TFM_60_Concepts_Shift_Ranked.csv")

@st.cache_data
def load_global_deviation():
    df = pd.read_csv(DATA_DIR / "TFM_Global_Deviation_All_Countries_60_Concepts_WITH_BLOC.csv")
    if 'Camp' in df.columns and 'Bloc' not in df.columns:
        df = df.rename(columns={'Camp': 'Bloc'})
    return df

@st.cache_data
def load_voting_data():
    return pd.read_parquet(DATA_DIR / "un_voting_annual_cleaned.parquet")

@st.cache_data
def load_consistency_data():
    return pd.read_csv(DATA_DIR / "TFM_Speech_Action_Consistency.csv")

@st.cache_data
def load_p5_cohesion():
    return pd.read_csv(DATA_DIR / "TFM_P5_Semantic_Cohesion_60.csv")

def get_six_dimensions():
    return {
        "维度一: 政治法律": ["sovereignty", "democracy", "human_right", "self_determination", "rule_of_law", "freedom", "justice", "pluralism", "election", "constitution"],
        "维度二: 安全冲突": ["war", "peace", "terrorism", "security", "conflict", "weapon", "nuclear", "military", "violence", "threat"],
        "维度三: 经济发展": ["economy", "development", "trade", "poverty", "globalization", "investment", "growth", "inequality", "industry", "market"],
        "维度四: 国际秩序": ["multilateralism", "cooperation", "diplomacy", "alliance", "treaty", "negotiation", "agreement", "partnership", "dialogue", "consensus"],
        "维度五: 人文社会": ["education", "culture", "religion", "gender", "youth", "minority", "migration", "refugee", "identity", "diversity"],
        "维度六: 环境科技": ["climate", "environment", "energy", "sustainability", "technology", "innovation", "biodiversity", "pollution", "resource", "ocean"]
    }

def get_concept_definition(concept, lang='zh'):
    defs = {
        'sovereignty': {'zh': '主权 - 国家最高权威', 'en': 'Sovereignty - Supreme state authority', 'es': 'Soberanía - Autoridad suprema'},
        'democracy': {'zh': '民主 - 人民行使权力的政治制度', 'en': 'Democracy - Power by the people', 'es': 'Democracia - Poder del pueblo'},
        'human_right': {'zh': '人权 - 人作为人的基本权利', 'en': 'Human Rights - Fundamental human rights', 'es': 'Derechos Humanos'},
        'globalization': {'zh': '全球化 - 国家间紧密联系', 'en': 'Globalization', 'es': 'Globalización'},
        'climate': {'zh': '气候 - 长期天气模式', 'en': 'Climate', 'es': 'Clima'},
        'peace': {'zh': '和平 - 无战争状态', 'en': 'Peace', 'es': 'Paz'},
        'war': {'zh': '战争 - 武装冲突', 'en': 'War', 'es': 'Guerra'},
        'terrorism': {'zh': '恐怖主义', 'en': 'Terrorism', 'es': 'Terrorismo'},
    }
    if isinstance(defs.get(concept), dict):
        return defs[concept].get(lang, defs[concept].get('zh', concept))
    return f"{concept} - 暂无详细定义"
