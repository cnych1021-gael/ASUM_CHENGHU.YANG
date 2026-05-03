"""言行一致性分析 - 多语言 + AI"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr
import numpy as np
from utils.user_model import is_expert_mode, record_page_view
from utils.data_loader import load_consistency_data, get_concept_definition
from utils.language_manager import get_global_language
from utils.ai_explainer import answer_question, is_ai_available

st.set_page_config(page_title="Consistency Check", page_icon="✅", layout="wide")

current_lang = get_global_language()
record_page_view("Consistency Check")

T = {
    'title': {'zh': '✅ 言行一致性分析', 'en': '✅ Speech-Action Consistency', 'es': '✅ Consistencia Discurso-Acción'},
    'subtitle': {'zh': '各国演说立场 vs 实际投票行为', 'en': 'Speech Stance vs Voting Behavior', 'es': 'Postura vs Votación'},
    'research_note': {
        'zh': '**📌 研究说明：** 本分析选取两个最具代表性的国际政治概念：\n- **主权 (sovereignty)** - 国际关系基石原则\n- **人权 (human_right)** - 国际规范重要议题\n\n通过对比P5五常的演说立场（语义强度）与实际投票行为（赞成率），揭示"说与做"的一致性。',
        'en': '**📌 Research Note:** This analysis selects two representative concepts:\n- **Sovereignty** - Cornerstone of IR\n- **Human Rights** - Key international norm\n\nComparing P5 speech stance vs voting to reveal consistency.',
        'es': '**📌 Nota:** Análisis de dos conceptos:\n- **Soberanía** - Principio fundamental\n- **Derechos Humanos** - Norma clave\n\nComparando postura P5 vs votación.'
    },
    'concepts_analyzed': {'zh': '分析概念', 'en': 'Concepts', 'es': 'Conceptos'},
    'countries': {'zh': '覆盖国家', 'en': 'Countries', 'es': 'Países'},
    'time_range': {'zh': '时间跨度', 'en': 'Time Range', 'es': 'Tiempo'},
    'select_concept': {'zh': '🔍 选择分析概念：', 'en': '🔍 Select concept:', 'es': '🔍 Concepto:'},
    'sov': {'zh': '🏛️ 主权', 'en': '🏛️ Sovereignty', 'es': '🏛️ Soberanía'},
    'hr': {'zh': '🤝 人权', 'en': '🤝 Human Rights', 'es': '🤝 Derechos Humanos'},
    'data_records': {'zh': '数据记录', 'en': 'Records', 'es': 'Registros'},
    'concept_def': {'zh': '📚 概念解释：', 'en': '📚 Definition:', 'es': '📚 Definición:'},
    'no_data': {'zh': '⚠️ 未找到 {} 的数据', 'en': '⚠️ No data for {}', 'es': '⚠️ Sin datos para {}'},
    'comparison': {'zh': '📊 P5五常言行对比', 'en': '📊 P5 Speech vs Action', 'es': '📊 Comparación P5'},
    'speech_intensity': {'zh': '演说立场强度', 'en': 'Speech Intensity', 'es': 'Intensidad'},
    'voting_approval': {'zh': '投票赞成率', 'en': 'Voting Approval', 'es': 'Aprobación'},
    'country': {'zh': '国家', 'en': 'Country', 'es': 'País'},
    'trend_line': {'zh': '趋势线', 'en': 'Trend', 'es': 'Tendencia'},
    'stat_analysis': {'zh': '📈 统计分析', 'en': '📈 Statistics', 'es': '📈 Estadísticas'},
    'corr_coef': {'zh': '相关系数', 'en': 'Correlation', 'es': 'Correlación'},
    'p_value': {'zh': 'P值', 'en': 'P-value', 'es': 'Valor P'},
    'high_cons': {'zh': '✅ **言行较为一致**\n\n相关系数 > 0.5', 'en': '✅ **Highly Consistent**\n\nCorrelation > 0.5', 'es': '✅ **Consistente**\n\nCorrelación > 0.5'},
    'mod_cons': {'zh': 'ℹ️ **一定一致性**\n\n弱正相关', 'en': 'ℹ️ **Moderate**\n\nWeak positive correlation', 'es': 'ℹ️ **Moderado**'},
    'low_cons': {'zh': '⚠️ **言行不一致**\n\n弱或负相关', 'en': '⚠️ **Inconsistent**\n\nWeak/negative', 'es': '⚠️ **Inconsistente**'},
    'country_rank': {'zh': '**各国一致性排名：**', 'en': '**Country Ranking:**', 'es': '**Ranking:**'},
    'records_n': {'zh': '{} 条', 'en': '{} records', 'es': '{} registros'},
    'ai_question': {'zh': '💬 向AI提问', 'en': '💬 Ask AI', 'es': '💬 Preguntar IA'},
    'ai_placeholder': {'zh': '例如：为什么美国在人权问题上言行不一？', 'en': 'e.g., Why is US inconsistent on HR?', 'es': 'ej: ¿Por qué inconsistencia?'},
    'ai_ask_btn': {'zh': '🤖 提问', 'en': '🤖 Ask', 'es': '🤖 Preguntar'},
    'ai_loading': {'zh': '🤖 AI思考中...', 'en': '🤖 Thinking...', 'es': '🤖 Pensando...'},
    'ai_disclaimer': {'zh': '💡 由Google Gemini AI生成', 'en': '💡 By Gemini', 'es': '💡 Por Gemini'},
    'detail_data': {'zh': '🔬 详细数据', 'en': '🔬 Details', 'es': '🔬 Detalles'},
    'download': {'zh': '📥 下载', 'en': '📥 Download', 'es': '📥 Descargar'},
}

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

st.info(T['research_note'][current_lang])

st.markdown("---")

df_consistency = load_consistency_data()
expert_mode = is_expert_mode()

# 数据概况
col1, col2, col3 = st.columns(3)
col1.metric(T['concepts_analyzed'][current_lang], "2")
col2.metric(T['countries'][current_lang], "5 (P5)")
col3.metric(T['time_range'][current_lang], "1971-2025")

st.markdown("---")

# 选择概念
concept_choice = st.radio(
    T['select_concept'][current_lang],
    ["sovereignty", "human_right"],
    format_func=lambda x: T['sov'][current_lang] if x == 'sovereignty' else T['hr'][current_lang],
    horizontal=True
)

st.info(f"{T['concept_def'][current_lang]} {get_concept_definition(concept_choice, current_lang)}")

st.markdown("---")

# 过滤数据
concept_data = df_consistency[df_consistency['Concept'] == concept_choice].copy()
concept_data = concept_data.dropna(subset=['Semantic_Cohesion', 'vote_score'])

if len(concept_data) < 2:
    st.warning(T['no_data'][current_lang].format(concept_choice))
    st.stop()

# ===== 散点图 =====
st.header(T['comparison'][current_lang])

fig = px.scatter(
    concept_data,
    x='Semantic_Cohesion', y='vote_score',
    color='country', hover_data=['year'],
    title=f"{concept_choice.upper()}",
    labels={
        'Semantic_Cohesion': T['speech_intensity'][current_lang],
        'vote_score': T['voting_approval'][current_lang],
        'country': T['country'][current_lang]
    },
    color_discrete_map={'USA': '#1f77b4', 'CHN': '#ff7f0e', 'RUS': '#2ca02c', 'GBR': '#d62728', 'FRA': '#9467bd'}
)

# 趋势线
if len(concept_data) > 2:
    try:
        z = np.polyfit(concept_data['Semantic_Cohesion'], concept_data['vote_score'], 1)
        p = np.poly1d(z)
        x_trend = [concept_data['Semantic_Cohesion'].min(), concept_data['Semantic_Cohesion'].max()]
        y_trend = [p(x) for x in x_trend]
        fig.add_trace(go.Scatter(x=x_trend, y=y_trend, mode='lines',
                                 line=dict(dash='dash', color='gray'),
                                 name=T['trend_line'][current_lang]))
    except:
        pass

fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===== 统计分析 =====
st.header(T['stat_analysis'][current_lang])

col1, col2 = st.columns(2)

try:
    correlation, p_value = pearsonr(concept_data['Semantic_Cohesion'], concept_data['vote_score'])
    
    with col1:
        st.metric(T['corr_coef'][current_lang], f"{correlation:.3f}")
        st.metric(T['p_value'][current_lang], f"{p_value:.4f}")
        
        if correlation > 0.5:
            st.success(T['high_cons'][current_lang])
        elif correlation > 0:
            st.info(T['mod_cons'][current_lang])
        else:
            st.warning(T['low_cons'][current_lang])
    
    with col2:
        st.markdown(T['country_rank'][current_lang])
        country_consistency = []
        for country in concept_data['country'].unique():
            cdf = concept_data[concept_data['country'] == country]
            if len(cdf) > 1:
                corr, _ = pearsonr(cdf['Semantic_Cohesion'], cdf['vote_score'])
                country_consistency.append({'country': country, 'corr': corr, 'n': len(cdf)})
        
        if country_consistency:
            consistency_df = pd.DataFrame(country_consistency).sort_values('corr', ascending=False)
            for _, row in consistency_df.iterrows():
                st.metric(row['country'], f"{row['corr']:.3f}",
                          delta=T['records_n'][current_lang].format(row['n']))
except Exception as e:
    st.error(f"分析错误: {e}")

st.markdown("---")

# ===== AI 提问 =====
if is_ai_available():
    st.header(T['ai_question'][current_lang])
    
    user_q = st.text_input(
        T['ai_question'][current_lang],
        placeholder=T['ai_placeholder'][current_lang],
        key="cons_ai_q"
    )
    
    if st.button(T['ai_ask_btn'][current_lang], type="primary"):
        if user_q:
            with st.spinner(T['ai_loading'][current_lang]):
                context = f"概念: {concept_choice}\n相关系数: {correlation:.3f}\nP值: {p_value:.4f}\n国家一致性数据已计算"
                answer = answer_question(user_q, context, current_lang)
                st.success("✨ AI回答")
                st.markdown(answer)
                st.caption(T['ai_disclaimer'][current_lang])

# ===== 专家模式 =====
if expert_mode:
    st.markdown("---")
    st.header(T['detail_data'][current_lang])
    st.dataframe(concept_data, use_container_width=True)
    csv = concept_data.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, f"{concept_choice}_consistency.csv", "text/csv")
