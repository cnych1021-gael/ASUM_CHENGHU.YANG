"""
Speech-Action Consistency Analysis - Multilingual (zh/en/es)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr
from utils.user_model import initialize_user_profile, is_expert_mode, record_page_view
from utils.data_loader import load_consistency_data, get_concept_definition
from utils.language_manager import get_global_language

st.set_page_config(page_title="Consistency Check", page_icon="✅", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '✅ 言行一致性分析', 'en': '✅ Speech-Action Consistency Analysis', 'es': '✅ Análisis de Consistencia Discurso-Acción'},
    'subtitle': {'zh': '各国演说立场 vs 实际投票行为对比', 'en': 'Comparing National Speech Stance vs Actual Voting Behavior', 'es': 'Comparación: Postura del Discurso vs Comportamiento de Votación'},
    'research_note': {
        'zh': '**📌 研究说明：**\n\n本分析选取了两个最具代表性的国际政治核心概念进行案例研究：\n- **主权 (sovereignty)** - 国际关系的基石原则\n- **人权 (human_right)** - 国际规范的重要议题\n\n通过对比P5五常国家在这两个议题上的演说立场（语义强度）与实际投票行为（赞成率），揭示各国"说与做"的一致性程度。',
        'en': '**📌 Research Note:**\n\nThis analysis selects two most representative core concepts in international politics for case study:\n- **Sovereignty** - The cornerstone principle of international relations\n- **Human Right** - An important issue in international norms\n\nBy comparing the speech stance (semantic intensity) and actual voting behavior (approval rate) of the P5 nations on these two topics, we reveal the consistency between what countries "say and do".',
        'es': '**📌 Nota de Investigación:**\n\nEste análisis selecciona dos conceptos centrales más representativos en política internacional:\n- **Soberanía (sovereignty)** - El principio fundamental de las relaciones internacionales\n- **Derechos Humanos (human_right)** - Un tema importante de las normas internacionales\n\nAl comparar la postura del discurso (intensidad semántica) y el comportamiento real de votación (tasa de aprobación) de las naciones P5 en estos dos temas, revelamos la consistencia entre lo que los países "dicen y hacen".'
    },
    'data_overview': {'zh': '📊 数据概况', 'en': '📊 Data Overview', 'es': '📊 Resumen de Datos'},
    'concepts_analyzed': {'zh': '分析概念', 'en': 'Concepts Analyzed', 'es': 'Conceptos Analizados'},
    'countries_covered': {'zh': '覆盖国家', 'en': 'Countries Covered', 'es': 'Países Cubiertos'},
    'time_range': {'zh': '时间跨度', 'en': 'Time Range', 'es': 'Rango de Tiempo'},
    'select_concept': {'zh': '🔍 选择分析概念', 'en': '🔍 Select Concept to Analyze', 'es': '🔍 Seleccionar Concepto'},
    'select_label': {'zh': '选择要分析的概念：', 'en': 'Select concept to analyze:', 'es': 'Seleccionar concepto:'},
    'sov_label': {'zh': '🏛️ 主权 (Sovereignty)', 'en': '🏛️ Sovereignty', 'es': '🏛️ Soberanía'},
    'hr_label': {'zh': '🤝 人权 (Human Right)', 'en': '🤝 Human Right', 'es': '🤝 Derechos Humanos'},
    'data_records': {'zh': '数据记录数', 'en': 'Data Records', 'es': 'Registros'},
    'concept_def': {'zh': '**📚 概念解释：**', 'en': '**📚 Concept Explanation:**', 'es': '**📚 Explicación:**'},
    'no_data': {'zh': '⚠️ 未找到 {} 的数据', 'en': '⚠️ No data found for {}', 'es': '⚠️ No hay datos para {}'},
    'insufficient': {'zh': '数据不足，无法进行相关性分析', 'en': 'Insufficient data for correlation analysis', 'es': 'Datos insuficientes'},
    'comparison': {'zh': '📊 P5五常言行对比', 'en': '📊 P5 Speech vs Action Comparison', 'es': '📊 Comparación Discurso vs Acción P5'},
    'chart_title': {'zh': '{} - 演说立场 vs 投票行为', 'en': '{} - Speech Stance vs Voting Behavior', 'es': '{} - Postura vs Comportamiento'},
    'speech_intensity': {'zh': '演说立场强度', 'en': 'Speech Stance Intensity', 'es': 'Intensidad del Discurso'},
    'voting_approval': {'zh': '投票赞成率', 'en': 'Voting Approval Rate', 'es': 'Tasa de Aprobación'},
    'country': {'zh': '国家', 'en': 'Country', 'es': 'País'},
    'trend_line': {'zh': '趋势线', 'en': 'Trend Line', 'es': 'Línea de Tendencia'},
    'chart_caption': {'zh': '💡 点击图例可以隐藏/显示特定国家', 'en': '💡 Click legend to hide/show specific countries', 'es': '💡 Haz clic en la leyenda para ocultar/mostrar países'},
    'stat_analysis': {'zh': '📈 统计分析', 'en': '📈 Statistical Analysis', 'es': '📈 Análisis Estadístico'},
    'corr_coef': {'zh': '相关系数', 'en': 'Correlation Coefficient', 'es': 'Coeficiente de Correlación'},
    'p_value': {'zh': 'P值', 'en': 'P-value', 'es': 'Valor P'},
    'high_cons': {'zh': '**✅ 言行较为一致**\n\n相关系数 > 0.5，说明演说立场与投票行为有较强的正相关。', 'en': '**✅ Highly Consistent**\n\nCorrelation > 0.5, indicating strong positive correlation between speech and voting.', 'es': '**✅ Altamente Consistente**\n\nCorrelación > 0.5, fuerte correlación positiva.'},
    'mod_cons': {'zh': '**ℹ️ 言行有一定一致性**\n\n存在正相关，但程度不强。', 'en': '**ℹ️ Moderate Consistency**\n\nPositive correlation exists, but not strong.', 'es': '**ℹ️ Consistencia Moderada**\n\nCorrelación positiva débil.'},
    'low_cons': {'zh': '**⚠️ 言行不一致**\n\n演说立场与实际投票行为关联性弱或负相关。', 'en': '**⚠️ Inconsistent**\n\nWeak or negative correlation between speech and voting.', 'es': '**⚠️ Inconsistente**\n\nCorrelación débil o negativa.'},
    'country_rank': {'zh': '**各国一致性排名：**', 'en': '**Country Consistency Ranking:**', 'es': '**Ranking por País:**'},
    'records_n': {'zh': '{} 条记录', 'en': '{} records', 'es': '{} registros'},
    'analysis_err': {'zh': '统计分析出错: {}', 'en': 'Analysis error: {}', 'es': 'Error de análisis: {}'},
    'detail_data': {'zh': '🔬 详细数据', 'en': '🔬 Detailed Data', 'es': '🔬 Datos Detallados'},
    'view_raw': {'zh': '查看原始数据', 'en': 'View Raw Data', 'es': 'Ver Datos Originales'},
    'download': {'zh': '📥 下载数据', 'en': '📥 Download Data', 'es': '📥 Descargar Datos'},
    'continue': {'zh': '🧭 继续探索', 'en': '🧭 Continue Exploring', 'es': '🧭 Continuar Explorando'},
    'nav_global': {'zh': '📊 全局语义偏移', 'en': '📊 Global Overview', 'es': '📊 Visión Global'},
    'nav_bloc': {'zh': '🌍 阵营对比分析', 'en': '🌍 Bloc Analysis', 'es': '🌍 Análisis de Bloques'},
    'nav_expert': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'}
}

initialize_user_profile()
record_page_view("Consistency Check")

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

st.info(T['research_note'][current_lang])

st.markdown("---")

df_consistency = load_consistency_data()
expert_mode = is_expert_mode()

with st.expander(T['data_overview'][current_lang]):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(T['concepts_analyzed'][current_lang], "2")
    with col2:
        st.metric(T['countries_covered'][current_lang], "5 (P5)")
    with col3:
        st.metric(T['time_range'][current_lang], "1971-2025")

st.markdown("---")

st.subheader(T['select_concept'][current_lang])

col1, col2 = st.columns([2, 1])

with col1:
    concept_choice = st.radio(
        T['select_label'][current_lang],
        ["sovereignty", "human_right"],
        format_func=lambda x: {"sovereignty": T['sov_label'][current_lang], "human_right": T['hr_label'][current_lang]}[x]
    )

with col2:
    st.metric(T['data_records'][current_lang], len(df_consistency[df_consistency['Concept'] == concept_choice]))

st.markdown(T['concept_def'][current_lang])
st.info(get_concept_definition(concept_choice))

st.markdown("---")

concept_data = df_consistency[df_consistency['Concept'] == concept_choice].copy()

if concept_data.empty:
    st.error(T['no_data'][current_lang].format(concept_choice))
    st.stop()

concept_data = concept_data.dropna(subset=['Semantic_Cohesion', 'vote_score'])

if len(concept_data) < 2:
    st.warning(T['insufficient'][current_lang])
    st.stop()

st.header(T['comparison'][current_lang])

fig = px.scatter(
    concept_data,
    x='Semantic_Cohesion',
    y='vote_score',
    color='country',
    hover_data=['year'],
    title=T['chart_title'][current_lang].format(concept_choice.upper()),
    labels={
        'Semantic_Cohesion': T['speech_intensity'][current_lang],
        'vote_score': T['voting_approval'][current_lang],
        'country': T['country'][current_lang]
    },
    color_discrete_map={'USA': '#1f77b4', 'CHN': '#ff7f0e', 'RUS': '#2ca02c', 'GBR': '#d62728', 'FRA': '#9467bd'}
)

if len(concept_data) > 2:
    try:
        import numpy as np
        z = np.polyfit(concept_data['Semantic_Cohesion'], concept_data['vote_score'], 1)
        p = np.poly1d(z)
        x_trend = [concept_data['Semantic_Cohesion'].min(), concept_data['Semantic_Cohesion'].max()]
        y_trend = [p(x) for x in x_trend]
        fig.add_trace(go.Scatter(x=x_trend, y=y_trend, mode='lines',
                                 line=dict(dash='dash', color='gray', width=2),
                                 name=T['trend_line'][current_lang]))
    except:
        pass

fig.update_layout(height=500, showlegend=True,
                  legend=dict(title=T['country'][current_lang], orientation="v",
                              yanchor="top", y=1, xanchor="left", x=1.02))

st.plotly_chart(fig, use_container_width=True)
st.caption(T['chart_caption'][current_lang])

st.markdown("---")
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
            country_df = concept_data[concept_data['country'] == country]
            if len(country_df) > 1:
                corr, _ = pearsonr(country_df['Semantic_Cohesion'], country_df['vote_score'])
                country_consistency.append({'country': country, 'correlation': corr, 'records': len(country_df)})
        
        if country_consistency:
            consistency_df = pd.DataFrame(country_consistency).sort_values('correlation', ascending=False)
            for idx, row in consistency_df.iterrows():
                st.metric(row['country'], f"{row['correlation']:.3f}",
                          delta=T['records_n'][current_lang].format(row['records']))

except Exception as e:
    st.error(T['analysis_err'][current_lang].format(str(e)))

if expert_mode:
    st.markdown("---")
    st.header(T['detail_data'][current_lang])
    
    with st.expander(T['view_raw'][current_lang]):
        st.dataframe(concept_data, use_container_width=True)
    
    csv = concept_data.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, f"{concept_choice}_consistency.csv", "text/csv")

st.markdown("---")
st.markdown(f"### {T['continue'][current_lang]}")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_📊_Global_Overview.py", label=T['nav_global'][current_lang])
with col2:
    st.page_link("pages/2_🌍_Bloc_Analysis.py", label=T['nav_bloc'][current_lang])
with col3:
    if expert_mode:
        st.page_link("pages/4_🔬_Expert_Lab.py", label=T['nav_expert'][current_lang])
