"""
Geopolitical Bloc Comparison Analysis - Multilingual (zh/en/es)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_global_deviation, get_six_dimensions, get_concept_definition
from utils.user_model import is_expert_mode, record_concept_click
from utils.language_manager import get_global_language

st.set_page_config(page_title="Bloc Analysis", page_icon="🌍", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '🌍 地缘政治阵营对比分析', 'en': '🌍 Geopolitical Bloc Comparison', 'es': '🌍 Comparación de Bloques Geopolíticos'},
    'subtitle': {'zh': 'P5 vs 全球北方 vs 全球南方', 'en': 'P5 vs Global North vs Global South', 'es': 'P5 vs Norte Global vs Sur Global'},
    'select_dim': {'zh': '选择维度：', 'en': 'Select Dimension:', 'es': 'Seleccionar Dimensión:'},
    'select_concept': {'zh': '选择要分析的概念：', 'en': 'Select concept to analyze:', 'es': 'Seleccionar concepto:'},
    'current_dim': {'zh': '当前维度', 'en': 'Current Dimension', 'es': 'Dimensión Actual'},
    'mark_interest': {'zh': '🔖 标记为感兴趣', 'en': '🔖 Mark as Interesting', 'es': '🔖 Marcar como Interesante'},
    'recorded': {'zh': '✅ 已记录您对 {} 的兴趣！', 'en': '✅ Recorded your interest in {}!', 'es': '✅ ¡Interés en {} registrado!'},
    'no_data': {'zh': '⚠️ 未找到 {} 的数据', 'en': '⚠️ No data found for {}', 'es': '⚠️ Sin datos para {}'},
    'camp_mapped': {'zh': "💡 数据使用 'Camp' 列，已自动映射为 'Bloc'", 'en': "💡 Data uses 'Camp' column, auto-mapped to 'Bloc'", 'es': "💡 Datos usan 'Camp', mapeado a 'Bloc'"},
    'debug_info': {'zh': '🔍 数据调试信息', 'en': '🔍 Data Debug Info', 'es': '🔍 Información de Depuración'},
    'columns_label': {'zh': '**数据列名：**', 'en': '**Data Columns:**', 'es': '**Columnas:**'},
    'rows_label': {'zh': '**数据行数：**', 'en': '**Number of Rows:**', 'es': '**Filas:**'},
    'first_5': {'zh': '**前5行数据：**', 'en': '**First 5 Rows:**', 'es': '**Primeras 5 Filas:**'},
    'missing_bloc': {
        'zh': '''
❌ **数据文件缺少阵营分类列**

**当前数据包含的列：**
```
{}
```

**需要的列：**
- Bloc 或 Camp (阵营分类)
- Concept (概念名称)
- Deviation_ColdWar (冷战偏差)
- Deviation_PostColdWar (后冷战偏差)
- Deviation_Shift (偏差变化)
''',
        'en': '''
❌ **Data file missing bloc classification column**

**Current columns:**
```
{}
```

**Required columns:**
- Bloc or Camp (bloc classification)
- Concept (concept name)
- Deviation_ColdWar (Cold War deviation)
- Deviation_PostColdWar (Post-Cold War deviation)
- Deviation_Shift (deviation change)
''',
        'es': '''
❌ **Archivo de datos sin columna de clasificación**

**Columnas actuales:**
```
{}
```

**Columnas requeridas:**
- Bloc o Camp (clasificación)
- Concept (nombre del concepto)
- Deviation_ColdWar (desviación Guerra Fría)
- Deviation_PostColdWar (desviación Post-Guerra Fría)
- Deviation_Shift (cambio de desviación)
'''
    },
    'bloc_empty': {'zh': '⚠️ {} 的所有记录Bloc列都为空，无法进行阵营对比分析', 'en': '⚠️ All Bloc records for {} are empty', 'es': '⚠️ Todos los registros de Bloc para {} están vacíos'},
    'bloc_empty_info': {'zh': '💡 这可能是因为该概念的数据没有包含阵营分类信息', 'en': '💡 This concept may not have bloc classification data', 'es': '💡 Este concepto puede no tener datos de clasificación'},
    'bloc_count': {'zh': '💡 当前数据包含 {} 个阵营：{}', 'en': '💡 Current data contains {} blocs: {}', 'es': '💡 Datos contienen {} bloques: {}'},
    'about_concept': {'zh': '📖 关于 {}', 'en': '📖 About {}', 'es': '📖 Sobre {}'},
    'concept_explanation': {'zh': '**📚 概念解释：**', 'en': '**📚 Concept Explanation:**', 'es': '**📚 Explicación:**'},
    'max_bloc': {'zh': '最大偏差阵营', 'en': 'Maximum Deviation Bloc', 'es': 'Bloque de Mayor Desviación'},
    'stats_error': {'zh': '无法计算阵营统计: {}', 'en': 'Cannot compute bloc statistics: {}', 'es': 'No se pueden calcular estadísticas: {}'},
    'three_bloc_compare': {'zh': '📊 三大阵营对比', 'en': '📊 Three Major Blocs Comparison', 'es': '📊 Comparación de Tres Bloques'},
    'avg_deviation_title': {'zh': '{} - 各阵营后冷战时期平均偏差', 'en': '{} - Average Post-Cold War Deviation by Bloc', 'es': '{} - Desviación Promedio Post-Guerra Fría por Bloque'},
    'bloc_label': {'zh': '地缘政治阵营', 'en': 'Geopolitical Bloc', 'es': 'Bloque Geopolítico'},
    'avg_deviation': {'zh': '平均语义偏差', 'en': 'Average Semantic Deviation', 'es': 'Desviación Semántica Promedio'},
    'interpret_help': {
        'zh': '''
💡 **如何解读：**
- 偏差越大 = 该阵营对这个概念的理解与全球平均差异越大
- P5 (五常): 美、中、俄、英、法
- 全球北方: 西方发达国家联盟
- 全球南方: G77发展中国家
''',
        'en': '''
💡 **How to interpret:**
- Larger deviation = greater difference from global average
- P5 (Permanent 5): USA, China, Russia, UK, France
- Global North: Western developed nations
- Global South: G77 developing countries
''',
        'es': '''
💡 **Cómo interpretar:**
- Mayor desviación = mayor diferencia con el promedio global
- P5: EE.UU., China, Rusia, Reino Unido, Francia
- Norte Global: Países desarrollados occidentales
- Sur Global: Países en desarrollo G77
'''
    },
    'plot_error': {'zh': '绘图出错: {}', 'en': 'Plot error: {}', 'es': 'Error de gráfico: {}'},
    'deep_analysis': {'zh': '🔬 {} 深度分析', 'en': '🔬 {} Deep Analysis', 'es': '🔬 Análisis Profundo de {}'},
    'tab_deviation': {'zh': '📊 偏差对比', 'en': '📊 Deviation Comparison', 'es': '📊 Comparación de Desviación'},
    'tab_evolution': {'zh': '📈 时间演变', 'en': '📈 Time Evolution', 'es': '📈 Evolución Temporal'},
    'tab_countries': {'zh': '🗺️ 国家分布', 'en': '🗺️ Country Distribution', 'es': '🗺️ Distribución por País'},
    'three_bloc_dev': {'zh': '三大阵营语义偏差对比', 'en': 'Three Blocs Semantic Deviation', 'es': 'Desviación Semántica de Tres Bloques'},
    'box_title': {'zh': '{} - 后冷战时期偏差分布', 'en': '{} - Post-Cold War Deviation Distribution', 'es': '{} - Distribución de Desviación Post-Guerra Fría'},
    'deviation_y': {'zh': '语义偏差', 'en': 'Semantic Deviation', 'es': 'Desviación Semántica'},
    'stats_data': {'zh': '**统计数据：**', 'en': '**Statistical Data:**', 'es': '**Datos Estadísticos:**'},
    'analysis_error': {'zh': '分析出错: {}', 'en': 'Analysis error: {}', 'es': 'Error de análisis: {}'},
    'deviation_trend': {'zh': '偏差变化趋势', 'en': 'Deviation Trend', 'es': 'Tendencia de Desviación'},
    'cold_war': {'zh': '冷战时期偏差', 'en': 'Cold War Deviation', 'es': 'Desviación Guerra Fría'},
    'post_cold_war': {'zh': '后冷战时期偏差', 'en': 'Post-Cold War Deviation', 'es': 'Desviación Post-Guerra Fría'},
    'scatter_title': {'zh': '{} - 冷战 vs 后冷战偏差', 'en': '{} - Cold War vs Post-Cold War Deviation', 'es': '{} - Guerra Fría vs Post-Guerra Fría'},
    'no_change_line': {'zh': '无变化线', 'en': 'No-change Line', 'es': 'Línea Sin Cambio'},
    'country_dist': {'zh': '各国偏差分布', 'en': 'Country Deviation Distribution', 'es': 'Distribución por País'},
    'top10_title': {'zh': '{} - Top 10 偏差最大国家', 'en': '{} - Top 10 Most Deviated Countries', 'es': '{} - Top 10 Países con Mayor Desviación'},
    'iso_code': {'zh': '国家代码', 'en': 'Country Code', 'es': 'Código de País'},
    'view_full_data': {'zh': '查看完整数据', 'en': 'View Full Data', 'es': 'Ver Datos Completos'},
    'display_error': {'zh': '显示出错: {}', 'en': 'Display error: {}', 'es': 'Error de visualización: {}'},
    'continue': {'zh': '🧭 继续探索', 'en': '🧭 Continue Exploring', 'es': '🧭 Continuar Explorando'},
    'nav_global': {'zh': '📊 全局语义偏移', 'en': '📊 Global Overview', 'es': '📊 Visión Global'},
    'nav_consistency': {'zh': '✅ 言行一致性', 'en': '✅ Consistency Check', 'es': '✅ Verificación'},
    'nav_expert': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Lab', 'es': '🔬 Laboratorio Experto'}
}

df_global = load_global_deviation()
dimensions = get_six_dimensions()

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

expert_mode = is_expert_mode()

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    dimension_choice = st.selectbox(T['select_dim'][current_lang], list(dimensions.keys()))
    concepts_in_dim = dimensions[dimension_choice]
    available_concepts = [c for c in concepts_in_dim if c in df_global['Concept'].values]
    selected_concept = st.selectbox(T['select_concept'][current_lang], available_concepts)

with col2:
    st.metric(T['current_dim'][current_lang], dimension_choice.split(":")[0])

if st.button(T['mark_interest'][current_lang], key="bookmark"):
    record_concept_click(selected_concept, dimension_choice)
    st.success(T['recorded'][current_lang].format(selected_concept))

st.markdown("---")

concept_data = df_global[df_global['Concept'] == selected_concept].copy()

if concept_data.empty:
    st.error(T['no_data'][current_lang].format(selected_concept))
    st.stop()

if 'Camp' in concept_data.columns and 'Bloc' not in concept_data.columns:
    concept_data = concept_data.rename(columns={'Camp': 'Bloc'})
    st.info(T['camp_mapped'][current_lang])

if expert_mode:
    with st.expander(T['debug_info'][current_lang]):
        st.write(T['columns_label'][current_lang])
        st.code(', '.join(concept_data.columns.tolist()))
        st.write(f"{T['rows_label'][current_lang]} {len(concept_data)}")
        st.write(T['first_5'][current_lang])
        st.dataframe(concept_data.head())

has_bloc = 'Bloc' in concept_data.columns

if not has_bloc:
    st.error(T['missing_bloc'][current_lang].format(', '.join(concept_data.columns.tolist())))
    st.stop()

if concept_data['Bloc'].isna().all():
    st.warning(T['bloc_empty'][current_lang].format(selected_concept))
    st.info(T['bloc_empty_info'][current_lang])
    st.stop()

bloc_counts = concept_data['Bloc'].value_counts()
st.caption(T['bloc_count'][current_lang].format(len(bloc_counts), ', '.join(bloc_counts.index.tolist())))

if not expert_mode:
    st.header(T['about_concept'][current_lang].format(selected_concept.upper()))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(T['concept_explanation'][current_lang])
        st.info(get_concept_definition(selected_concept))
    
    with col2:
        try:
            avg_by_bloc = concept_data.groupby('Bloc')['Deviation_PostColdWar'].mean().to_dict()
            
            if avg_by_bloc:
                max_bloc = max(avg_by_bloc, key=avg_by_bloc.get)
                max_value = avg_by_bloc[max_bloc]
                
                st.metric(T['max_bloc'][current_lang], max_bloc.split("(")[0].strip(), f"{max_value:.3f}")
        except Exception as e:
            st.warning(T['stats_error'][current_lang].format(str(e)))
    
    st.markdown("---")
    
    st.subheader(T['three_bloc_compare'][current_lang])
    
    try:
        bloc_summary = concept_data.groupby('Bloc').agg({
            'Deviation_PostColdWar': 'mean',
            'Deviation_Shift': 'mean'
        }).reset_index()
        
        fig = px.bar(
            bloc_summary,
            x='Bloc',
            y='Deviation_PostColdWar',
            title=T['avg_deviation_title'][current_lang].format(selected_concept.upper()),
            labels={'Bloc': T['bloc_label'][current_lang], 'Deviation_PostColdWar': T['avg_deviation'][current_lang]},
            color='Bloc',
            color_discrete_map={
                'P5 (Major Powers)': '#e74c3c',
                'Global North (Western/Allies)': '#3498db',
                'Global South (G77/Rest of World)': '#2ecc71'
            }
        )
        
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(T['interpret_help'][current_lang])
    except Exception as e:
        st.error(T['plot_error'][current_lang].format(str(e)))
        if expert_mode:
            st.exception(e)

else:
    st.header(T['deep_analysis'][current_lang].format(selected_concept.upper()))
    
    tab1, tab2, tab3 = st.tabs([T['tab_deviation'][current_lang], T['tab_evolution'][current_lang], T['tab_countries'][current_lang]])
    
    with tab1:
        st.subheader(T['three_bloc_dev'][current_lang])
        
        try:
            bloc_stats = concept_data.groupby('Bloc').agg({
                'Deviation_ColdWar': ['mean', 'std'],
                'Deviation_PostColdWar': ['mean', 'std'],
                'Deviation_Shift': ['mean', 'std']
            }).reset_index()
            
            bloc_stats.columns = ['_'.join(col).strip('_') for col in bloc_stats.columns.values]
            
            fig = go.Figure()
            
            for bloc in concept_data['Bloc'].unique():
                bloc_data = concept_data[concept_data['Bloc'] == bloc]
                
                fig.add_trace(go.Box(y=bloc_data['Deviation_PostColdWar'], name=bloc, boxmean='sd'))
            
            fig.update_layout(
                title=T['box_title'][current_lang].format(selected_concept.upper()),
                yaxis_title=T['deviation_y'][current_lang],
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(T['stats_data'][current_lang])
            st.dataframe(bloc_stats, use_container_width=True)
        except Exception as e:
            st.error(T['analysis_error'][current_lang].format(str(e)))
            if expert_mode:
                st.exception(e)
    
    with tab2:
        st.subheader(T['deviation_trend'][current_lang])
        
        try:
            fig = px.scatter(
                concept_data,
                x='Deviation_ColdWar',
                y='Deviation_PostColdWar',
                color='Bloc',
                hover_data=['ISO_Code'],
                title=T['scatter_title'][current_lang].format(selected_concept.upper()),
                labels={
                    'Deviation_ColdWar': T['cold_war'][current_lang],
                    'Deviation_PostColdWar': T['post_cold_war'][current_lang]
                }
            )
            
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name=T['no_change_line'][current_lang],
                showlegend=True
            ))
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(T['plot_error'][current_lang].format(str(e)))
    
    with tab3:
        st.subheader(T['country_dist'][current_lang])
        
        try:
            top_countries = concept_data.nlargest(10, 'Deviation_PostColdWar')
            
            fig = px.bar(
                top_countries,
                x='ISO_Code',
                y='Deviation_PostColdWar',
                color='Bloc',
                title=T['top10_title'][current_lang].format(selected_concept.upper()),
                labels={
                    'ISO_Code': T['iso_code'][current_lang],
                    'Deviation_PostColdWar': T['post_cold_war'][current_lang]
                }
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander(T['view_full_data'][current_lang]):
                st.dataframe(
                    concept_data[['ISO_Code', 'Bloc', 'Deviation_ColdWar', 
                                  'Deviation_PostColdWar', 'Deviation_Shift']]
                    .sort_values('Deviation_PostColdWar', ascending=False),
                    use_container_width=True
                )
        except Exception as e:
            st.error(T['display_error'][current_lang].format(str(e)))

st.markdown("---")
st.markdown(f"### {T['continue'][current_lang]}")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_📊_Global_Overview.py", label=T['nav_global'][current_lang])

with col2:
    st.page_link("pages/3_✅_Consistency_Check.py", label=T['nav_consistency'][current_lang])

with col3:
    if expert_mode:
        st.page_link("pages/4_🔬_Expert_Lab.py", label=T['nav_expert'][current_lang])
