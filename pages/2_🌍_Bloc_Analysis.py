"""地缘政治阵营对比分析 - 多语言 + AI"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_global_deviation, get_six_dimensions, get_concept_definition
from utils.user_model import is_expert_mode, record_concept_click, record_page_view
from utils.language_manager import get_global_language
from utils.ai_explainer import answer_question, is_ai_available

st.set_page_config(page_title="Bloc Analysis", page_icon="🌍", layout="wide")

current_lang = get_global_language()
record_page_view("Bloc Analysis")

T = {
    'title': {'zh': '🌍 地缘政治阵营对比分析', 'en': '🌍 Geopolitical Bloc Comparison', 'es': '🌍 Comparación de Bloques'},
    'subtitle': {'zh': 'P5 vs 全球北方 vs 全球南方', 'en': 'P5 vs Global North vs Global South', 'es': 'P5 vs Norte Global vs Sur Global'},
    'select_dim': {'zh': '选择维度：', 'en': 'Select Dimension:', 'es': 'Seleccionar Dimensión:'},
    'select_concept': {'zh': '选择概念：', 'en': 'Select concept:', 'es': 'Seleccionar concepto:'},
    'mark_interest': {'zh': '🔖 标记为感兴趣', 'en': '🔖 Mark as Interesting', 'es': '🔖 Marcar Interesante'},
    'recorded': {'zh': '✅ 已记录', 'en': '✅ Recorded', 'es': '✅ Registrado'},
    'no_data': {'zh': '⚠️ 未找到数据', 'en': '⚠️ No data', 'es': '⚠️ Sin datos'},
    'definition': {'zh': '📚 概念定义', 'en': '📚 Definition', 'es': '📚 Definición'},
    'bloc_compare': {'zh': '📊 阵营对比', 'en': '📊 Bloc Comparison', 'es': '📊 Comparación'},
    'cold_war_dev': {'zh': '冷战时期偏差', 'en': 'Cold War Deviation', 'es': 'Desviación Guerra Fría'},
    'post_cold_dev': {'zh': '后冷战偏差', 'en': 'Post-Cold War Deviation', 'es': 'Desviación Post-Guerra Fría'},
    'shift': {'zh': '偏差变化', 'en': 'Deviation Shift', 'es': 'Cambio'},
    'ai_question': {'zh': '💬 向AI提问', 'en': '💬 Ask AI', 'es': '💬 Preguntar IA'},
    'ai_placeholder': {'zh': '例如：为什么中美在主权问题上分歧这么大？', 'en': 'e.g., Why do China and US differ on sovereignty?', 'es': 'ej: ¿Por qué China y EEUU difieren?'},
    'ai_ask_btn': {'zh': '🤖 提问', 'en': '🤖 Ask', 'es': '🤖 Preguntar'},
    'ai_loading': {'zh': '🤖 AI正在思考...', 'en': '🤖 AI thinking...', 'es': '🤖 IA pensando...'},
    'ai_disclaimer': {'zh': '💡 由Google Gemini AI生成', 'en': '💡 By Google Gemini', 'es': '💡 Por Google Gemini'},
    'detail_data': {'zh': '🔬 详细数据', 'en': '🔬 Detailed Data', 'es': '🔬 Datos Detallados'},
    'download': {'zh': '📥 下载', 'en': '📥 Download', 'es': '📥 Descargar'},
}

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

df_global = load_global_deviation()
dimensions = get_six_dimensions()
expert_mode = is_expert_mode()

# 检查 Bloc 列
if 'Bloc' not in df_global.columns:
    st.error(T['no_data'][current_lang])
    st.dataframe(df_global.head())
    st.stop()

# 选择维度和概念
col1, col2 = st.columns(2)
with col1:
    selected_dim = st.selectbox(T['select_dim'][current_lang], list(dimensions.keys()))
with col2:
    concepts_in_dim = dimensions[selected_dim]
    available_concepts = [c for c in concepts_in_dim if c in df_global['Concept'].unique()]
    if not available_concepts:
        st.warning(T['no_data'][current_lang])
        st.stop()
    selected_concept = st.selectbox(T['select_concept'][current_lang], available_concepts)

# 显示定义
with st.expander(T['definition'][current_lang]):
    st.write(get_concept_definition(selected_concept, current_lang))
    
    if st.button(T['mark_interest'][current_lang], key=f"mark_{selected_concept}"):
        record_concept_click(selected_concept, selected_dim)
        st.success(T['recorded'][current_lang])

st.markdown("---")

# 过滤数据
concept_df = df_global[df_global['Concept'] == selected_concept].copy()

if concept_df.empty:
    st.warning(T['no_data'][current_lang])
    st.stop()

# ===== 阵营对比图 =====
st.header(T['bloc_compare'][current_lang])

# 按 Bloc 聚合
bloc_stats = concept_df.groupby('Bloc').agg({
    'Deviation_ColdWar': 'mean',
    'Deviation_PostColdWar': 'mean'
}).reset_index() if 'Deviation_ColdWar' in concept_df.columns else None

if bloc_stats is not None and not bloc_stats.empty:
    # 双柱图
    fig = px.bar(
        bloc_stats.melt(id_vars='Bloc', var_name='Period', value_name='Deviation'),
        x='Bloc', y='Deviation', color='Period', barmode='group',
        title=f"{selected_concept.upper()} - {T['bloc_compare'][current_lang]}",
        color_discrete_map={
            'Deviation_ColdWar': '#ff7f0e',
            'Deviation_PostColdWar': '#1f77b4'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.dataframe(concept_df, use_container_width=True)

st.markdown("---")

# ===== AI 自然语言问答 =====
if is_ai_available():
    st.header(T['ai_question'][current_lang])
    
    user_question = st.text_input(
        T['ai_question'][current_lang],
        placeholder=T['ai_placeholder'][current_lang],
        key="bloc_ai_question"
    )
    
    if st.button(T['ai_ask_btn'][current_lang], type="primary"):
        if user_question:
            with st.spinner(T['ai_loading'][current_lang]):
                # 准备上下文数据
                context = f"概念: {selected_concept}\n维度: {selected_dim}\n"
                if bloc_stats is not None:
                    context += f"\n阵营对比数据:\n{bloc_stats.to_string()}\n"
                
                answer = answer_question(user_question, context, current_lang)
                
                st.success("✨ AI回答")
                st.markdown(answer)
                st.caption(T['ai_disclaimer'][current_lang])

# ===== 专家模式：详细数据 =====
if expert_mode:
    st.markdown("---")
    st.header(T['detail_data'][current_lang])
    st.dataframe(concept_df, use_container_width=True)
    
    csv = concept_df.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, f"{selected_concept}_bloc.csv", "text/csv")
