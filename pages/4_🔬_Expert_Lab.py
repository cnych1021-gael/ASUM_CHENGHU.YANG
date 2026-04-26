import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from utils.data_loader import (load_60_concepts, load_global_deviation, 
                                load_consistency_data, get_six_dimensions)
from utils.user_model import is_expert_mode
from utils.language_manager import get_global_language

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

st.set_page_config(page_title="Expert Lab", page_icon="🔬", layout="wide")

current_lang = get_global_language()

T = {
    'title': {'zh': '🔬 专家实验室', 'en': '🔬 Expert Laboratory', 'es': '🔬 Laboratorio Experto'},
    'subtitle': {'zh': '高级可视化与深度分析工具', 'en': 'Advanced Visualization & Deep Analysis Tools', 'es': 'Herramientas Avanzadas de Visualización'},
    'access_denied': {'zh': '🔒 此页面仅限专家模式访问', 'en': '🔒 Expert Mode Required', 'es': '🔒 Se Requiere Modo Experto'},
    'return_home': {'zh': '请返回首页重新选择用户类型', 'en': 'Please return to home page to switch user type', 'es': 'Por favor regrese para cambiar el tipo de usuario'},
    'back_home': {'zh': '🏠 返回首页', 'en': '🏠 Back to Home', 'es': '🏠 Volver al Inicio'},
    'analysis_tools': {'zh': '🛠️ 分析工具', 'en': '🛠️ Analysis Tools', 'es': '🛠️ Herramientas de Análisis'},
    'select_analysis': {'zh': '选择分析类型：', 'en': 'Select Analysis Type:', 'es': 'Seleccionar Tipo de Análisis:'},
    'opt1': {'zh': '1️⃣ 相关性矩阵热力图', 'en': '1️⃣ Correlation Matrix Heatmap', 'es': '1️⃣ Mapa de Calor de Correlación'},
    'opt2': {'zh': '2️⃣ 国家聚类树状图', 'en': '2️⃣ Country Clustering Dendrogram', 'es': '2️⃣ Dendrograma de Agrupación de Países'},
    'opt3': {'zh': '3️⃣ 3D词汇语义空间', 'en': '3️⃣ 3D Semantic Space', 'es': '3️⃣ Espacio Semántico 3D'},
    'opt4': {'zh': '4️⃣ Sankey流图（近义词演变）', 'en': '4️⃣ Sankey Flow (Synonym Evolution)', 'es': '4️⃣ Diagrama Sankey (Evolución de Sinónimos)'},
    'opt5': {'zh': '5️⃣ 异常值雷达（言行不一）', 'en': '5️⃣ Anomaly Radar (Speech-Action Gap)', 'es': '5️⃣ Radar de Anomalías (Brecha Discurso-Acción)'},
    'section1': {'zh': '1️⃣ 60个核心词汇的语义相关性矩阵', 'en': '1️⃣ Semantic Correlation Matrix of 60 Core Concepts', 'es': '1️⃣ Matriz de Correlación Semántica de 60 Conceptos'},
    'section2': {'zh': '2️⃣ 基于语义偏好的国家聚类分析', 'en': '2️⃣ Country Clustering Based on Semantic Preferences', 'es': '2️⃣ Agrupación de Países por Preferencias Semánticas'},
    'section3': {'zh': '3️⃣ 3D词汇语义空间', 'en': '3️⃣ 3D Semantic Space', 'es': '3️⃣ Espacio Semántico 3D'},
    'section4': {'zh': '4️⃣ Sankey流图：近义词演变', 'en': '4️⃣ Sankey Flow: Synonym Evolution', 'es': '4️⃣ Flujo Sankey: Evolución de Sinónimos'},
    'section5': {'zh': '5️⃣ 异常值雷达：言行不一国家', 'en': '5️⃣ Anomaly Radar: Inconsistent Countries', 'es': '5️⃣ Radar de Anomalías: Países Inconsistentes'},
    'select_dims': {'zh': '选择要分析的维度（可多选）：', 'en': 'Select dimensions to analyze (multi-select):', 'es': 'Seleccionar dimensiones a analizar (multi-selección):'},
}


# 检查权限
if not is_expert_mode():
    st.error(T["access_denied"][current_lang])
    st.info(T["return_home"][current_lang])
    st.page_link("app.py", label=T["back_home"][current_lang])
    st.stop()

# 加载数据
df_concepts = load_60_concepts()
df_global = load_global_deviation()
df_consistency = load_consistency_data()
dimensions = get_six_dimensions()

# 标题
st.title(T["title"][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")

st.markdown("---")

# 侧边栏：选择分析工具
with st.sidebar:
    st.header(T["analysis_tools"][current_lang])
    
    analysis_choice = st.radio(
        T["select_analysis"][current_lang],
        [
            T["opt1"][current_lang],
            T["opt2"][current_lang],
            T["opt3"][current_lang],
            T["opt4"][current_lang],
            T["opt5"][current_lang]
        ]
    )

st.markdown("---")

# ==================== 1. 相关性矩阵热力图 ====================
if analysis_choice == T["opt1"][current_lang]:
    st.header(T["section1"][current_lang])
    
    st.markdown("""
    **分析目标：** 展示60个核心概念之间的语义相似度关系，揭示哪些概念在全球话语中被绑定在一起。
    """)
    
    # 选择维度筛选
    selected_dims = st.multiselect(
        T["select_dims"][current_lang],
        list(dimensions.keys()),
        default=list(dimensions.keys())[:2]  # 默认选择前两个
    )
    
    if selected_dims:
        # 提取选中维度的词汇
        selected_concepts = []
        for dim in selected_dims:
            selected_concepts.extend(dimensions[dim])
        
        # 筛选数据中实际存在的词汇
        available_concepts = [c for c in selected_concepts if c in df_concepts['Concept'].values]
        
        if len(available_concepts) < 2:
            st.warning("选中的维度中可用词汇不足，请选择更多维度")
        else:
            # 创建相似度矩阵（使用语义偏移数据作为相似度的代理）
            # 注意：这里我们使用1-偏移度作为相似度
            concept_subset = df_concepts[df_concepts['Concept'].isin(available_concepts)].copy()
            concept_subset = concept_subset.dropna(subset=['Similarity'])
            
            # 创建矩阵
            matrix_data = []
            for c1 in concept_subset['Concept']:
                row = []
                sim1 = concept_subset[concept_subset['Concept']==c1]['Similarity'].values[0]
                for c2 in concept_subset['Concept']:
                    sim2 = concept_subset[concept_subset['Concept']==c2]['Similarity'].values[0]
                    # 使用相似度差异的倒数作为相关性指标
                    similarity = 1 - abs(sim1 - sim2)
                    row.append(similarity)
                matrix_data.append(row)
            
            # 绘制热力图
            fig = go.Figure(data=go.Heatmap(
                z=matrix_data,
                x=concept_subset['Concept'].tolist(),
                y=concept_subset['Concept'].tolist(),
                colorscale='RdYlGn',
                colorbar=dict(title="相似度")
            ))
            
            fig.update_layout(
                title="概念语义相关性热力图",
                xaxis_title="概念",
                yaxis_title="概念",
                height=max(600, len(available_concepts) * 20),
                width=max(800, len(available_concepts) * 20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **解读提示：** 颜色越深（绿色），表示两个概念的语义演变模式越相似")

# ==================== 2. 国家聚类树状图 ====================
elif analysis_choice == T["opt2"][current_lang]:
    st.header(T["section2"][current_lang])
    
    st.markdown("""
    **分析目标：** 根据各国在60个核心词汇上的语义偏好，自动分组出相似的国家集团。
    """)
    
    # 准备聚类数据
    # 创建国家×词汇的偏差矩阵
    pivot_data = df_global.pivot_table(
        index='ISO_Code',
        columns='Concept',
        values='Deviation_PostColdWar',
        aggfunc='mean'
    )
    
    # 移除缺失值过多的国家
    pivot_data = pivot_data.dropna(thresh=len(pivot_data.columns) * 0.5)
    
    # 填充剩余缺失值
    pivot_data = pivot_data.fillna(pivot_data.mean())
    
    if len(pivot_data) < 3:
        st.warning("数据不足，无法进行聚类分析")
    else:
        # 选择聚类方法
        linkage_method = st.selectbox(
            "选择聚类算法：",
            ["ward", "average", "complete", "single"],
            help="Ward方法通常效果最好"
        )
        
        # 计算聚类
        linkage_matrix = hierarchy.linkage(pivot_data.values, method=linkage_method)
        
        # 绘制树状图
        fig, ax = plt.subplots(figsize=(14, max(8, len(pivot_data) * 0.3)))
        
        # 设置颜色阈值用于自动分组
        color_threshold = 0.7 * max(linkage_matrix[:, 2])
        
        dendro = hierarchy.dendrogram(
            linkage_matrix,
            labels=pivot_data.index.tolist(),
            orientation='right',
            ax=ax,
            color_threshold=color_threshold,
            above_threshold_color='gray'
        )
        
        # 改进的标题
        ax.set_title(
            f'基于60个核心概念语义偏好的国家聚类分析\n聚类方法: {linkage_method.upper()}', 
            fontsize=16, 
            fontweight='bold',
            pad=20
        )
        ax.set_xlabel('欧氏距离（语义差异度）', fontsize=12, fontweight='bold')
        ax.set_ylabel('国家', fontsize=12, fontweight='bold')
        
        # 添加网格线
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 添加图例说明
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='gray', label='单一国家/小组'),
            Patch(facecolor='C0', label='主要聚类1'),
            Patch(facecolor='C1', label='主要聚类2'),
            Patch(facecolor='C2', label='主要聚类3'),
        ]
        
        ax.legend(
            handles=legend_elements,
            loc='lower right',
            title='聚类组别',
            frameon=True,
            fancybox=True,
            shadow=True
        )
        
        # 添加说明文字
        ax.text(
            0.02, 0.98,
            '💡 距离越近的国家，在语义使用上越相似',
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.info("💡 **解读提示：** 距离越近的国家，在语义使用上越相似。观察是否形成了地缘政治集团")
        
        # 显示主要聚类
        st.markdown("---")
        st.subheader("📊 主要聚类识别")
        
        # 自动识别聚类
        n_clusters = st.slider("聚类数量：", 2, 10, 3)
        cluster_labels = hierarchy.fcluster(linkage_matrix, n_clusters, criterion='maxclust')
        
        # 显示每个聚类的国家
        for i in range(1, n_clusters + 1):
            countries_in_cluster = pivot_data.index[cluster_labels == i].tolist()
            st.markdown(f"**聚类 {i}** ({len(countries_in_cluster)} 个国家):")
            st.write(", ".join(countries_in_cluster))

# ==================== 3. 3D词汇语义空间 ====================
elif analysis_choice == T["opt3"][current_lang]:
    st.header("3️⃣ 交互式3D词汇语义空间")
    
    st.markdown("""
    **分析目标：** 使用PCA降维将60个词汇在高维语义空间中的位置投影到3D空间，直观展示词汇间的距离关系。
    """)
    
    # 准备数据：使用偏移度和上下文信息
    # 这里我们简化处理，使用现有数据的特征
    concept_data = df_concepts.dropna(subset=['Similarity'])
    
    if len(concept_data) < 3:
        st.warning("数据不足以进行3D可视化")
    else:
        # 创建特征矩阵（简化版：使用相似度和维度编码）
        feature_matrix = []
        labels = []
        
        for _, row in concept_data.iterrows():
            # 找到该词所属的维度
            dim_vector = [0] * 6
            for idx, (dim_name, concepts) in enumerate(dimensions.items()):
                if row['Concept'] in concepts:
                    dim_vector[idx] = 1
                    break
            
            # 组合特征：[相似度, 维度one-hot编码]
            features = [row['Similarity']] + dim_vector
            feature_matrix.append(features)
            labels.append(row['Concept'])
        
        feature_matrix = np.array(feature_matrix)
        
        # PCA降维到3D
        pca = PCA(n_components=3)
        coords_3d = pca.fit_transform(feature_matrix)
        
        # 创建DataFrame
        df_3d = pd.DataFrame({
            'Concept': labels,
            'X': coords_3d[:, 0],
            'Y': coords_3d[:, 1],
            'Z': coords_3d[:, 2],
            'Similarity': concept_data['Similarity'].values
        })
        
        # 添加维度信息
        df_3d['Dimension'] = df_3d['Concept'].apply(
            lambda c: next((dim for dim, concepts in dimensions.items() if c in concepts), "未知")
        )
        
        # 3D散点图
        fig = px.scatter_3d(
            df_3d,
            x='X',
            y='Y',
            z='Z',
            color='Dimension',
            text='Concept',
            size='Similarity',
            title='60个核心词汇的3D语义空间分布',
            labels={'X': 'PC1', 'Y': 'PC2', 'Z': 'PC3'},
            height=700
        )
        
        fig.update_traces(textposition='top center', textfont_size=8)
        fig.update_layout(scene=dict(
            xaxis_title=f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
            yaxis_title=f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
            zaxis_title=f'PC3 ({pca.explained_variance_ratio_[2]:.1%})'
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"💡 **解读提示：** 前3个主成分解释了 {pca.explained_variance_ratio_.sum():.1%} 的方差。距离近的词汇在语义演变上更相似")

# ==================== 4. 各国语义偏移量对比 ====================
elif analysis_choice == T["opt4"][current_lang]:
    st.header("4️⃣ 各国语义偏移量对比")
    
    st.markdown("""
    **分析目标：** 展示各国在冷战与后冷战时期对某个概念的语义偏移量变化。
    """)
    
    # 选择词汇
    available_concepts = df_concepts['Concept'].dropna().unique().tolist()
    selected_concept = st.selectbox("选择要分析的核心词汇：", available_concepts)
    
    # 获取该概念的全球数据
    concept_global = df_global[df_global['Concept'] == selected_concept].copy()
    
    if concept_global.empty:
        st.warning(f"未找到 {selected_concept} 的数据")
    else:
        # 处理Camp/Bloc列名
        if 'Camp' in concept_global.columns and 'Bloc' not in concept_global.columns:
            concept_global = concept_global.rename(columns={'Camp': 'Bloc'})
        
        st.subheader(f"📊 {selected_concept.upper()} - 冷战 vs 后冷战语义偏移")
        
        # 创建散点图：冷战 vs 后冷战偏移
        fig = px.scatter(
            concept_global,
            x='Deviation_ColdWar',
            y='Deviation_PostColdWar',
            color='Bloc' if 'Bloc' in concept_global.columns else None,
            hover_data=['ISO_Code', 'Deviation_Shift'],
            title=f"{selected_concept.upper()} - 各国语义偏移对比",
            labels={
                'Deviation_ColdWar': '冷战时期偏移',
                'Deviation_PostColdWar': '后冷战时期偏移',
                'Bloc': '阵营',
                'ISO_Code': '国家'
            },
            color_discrete_map={
                'P5 (Major Powers)': '#e74c3c',
                'Global North (Western/Allies)': '#3498db',
                'Global South (G77/Rest of World)': '#2ecc71'
            } if 'Bloc' in concept_global.columns else None
        )
        
        # 添加对角线（无变化参考线）
        max_val = max(
            concept_global['Deviation_ColdWar'].max(),
            concept_global['Deviation_PostColdWar'].max()
        )
        
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(dash='dash', color='gray', width=2),
            name='无变化线',
            showlegend=True
        ))
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        💡 **如何解读：**
        - 点在对角线上方 = 后冷战偏移增大（含义变化）
        - 点在对角线下方 = 后冷战偏移减小（含义趋同）
        - 距离对角线越远 = 变化越显著
        """)
        
        # Top 10变化最大的国家
        st.markdown("---")
        st.subheader("📈 语义偏移变化最大的国家")
        
        top_shift = concept_global.nlargest(10, 'Deviation_Shift')[
            ['ISO_Code', 'Bloc', 'Deviation_ColdWar', 'Deviation_PostColdWar', 'Deviation_Shift']
        ] if 'Bloc' in concept_global.columns else concept_global.nlargest(10, 'Deviation_Shift')[
            ['ISO_Code', 'Deviation_ColdWar', 'Deviation_PostColdWar', 'Deviation_Shift']
        ]
        
        fig_bar = px.bar(
            top_shift,
            x='ISO_Code',
            y='Deviation_Shift',
            color='Bloc' if 'Bloc' in top_shift.columns else None,
            title="Top 10 语义偏移变化最大国家",
            labels={
                'ISO_Code': '国家',
                'Deviation_Shift': '偏移变化量',
                'Bloc': '阵营'
            }
        )
        
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # 语境对比（如果有数据）
        if 'Cold_War_Context' in df_concepts.columns and 'Post_Cold_War_Context' in df_concepts.columns:
            st.markdown("---")
            st.subheader("📖 语境演变")
            
            concept_row = df_concepts[df_concepts['Concept'] == selected_concept]
            
            if not concept_row.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**冷战时期语境**")
                    cw_context = concept_row['Cold_War_Context'].values[0]
                    if pd.notna(cw_context):
                        st.info(cw_context)
                    else:
                        st.warning("无数据")
                
                with col2:
                    st.markdown("**后冷战时期语境**")
                    pcw_context = concept_row['Post_Cold_War_Context'].values[0]
                    if pd.notna(pcw_context):
                        st.info(pcw_context)
                    else:
                        st.warning("无数据")



# ==================== 5. 异常值雷达 ====================
elif analysis_choice == T["opt5"][current_lang]:
    st.header("5️⃣ 言行极度不一致检测")
    
    st.markdown("""
    **分析目标：** 识别那些在演说中高频提及某概念，但在投票时却持反对立场的国家-概念组合。
    """)
    
    # 检查是否有必要的数据
    if 'Semantic_Cohesion' not in df_consistency.columns or 'vote_score' not in df_consistency.columns:
        st.error("数据缺少必要的列")
        st.stop()
    
    # 计算言行不一致度
    df_consistency['inconsistency'] = abs(
        df_consistency['Semantic_Cohesion'] - df_consistency['vote_score']
    )
    
    # 显示数据概况
    unique_concepts = df_consistency['Concept'].nunique() if 'Concept' in df_consistency.columns else 0
    st.info(f"""
    💡 **数据说明：**
    - 当前数据包含 **{unique_concepts}** 个概念
    - 总记录数：{len(df_consistency)}
    - 本分析基于这些概念的言行一致性数据
    """)
    
    # 筛选参数
    threshold = st.slider(
        "不一致度阈值：",
        0.0, 1.0, 0.5, 0.05,
        help="高于此值的被视为异常"
    )
    
    # 筛选异常值
    anomalies = df_consistency[df_consistency['inconsistency'] > threshold].copy()
    anomalies = anomalies.sort_values('inconsistency', ascending=False)
    
    if anomalies.empty:
        st.info(f"未发现不一致度高于 {threshold} 的案例，请降低阈值")
    else:
        st.warning(f"发现 {len(anomalies)} 个言行显著不一致的案例")
        
        # 动态确定显示数量
        display_count = min(20, len(anomalies))
        st.subheader(f"📊 言行不一致度排行榜（Top {display_count}）")
        
        top_anomalies = anomalies.head(display_count)
        
        # 如果有国家信息，显示国家-概念组合
        if 'country' in top_anomalies.columns and 'Concept' in top_anomalies.columns:
            # 创建组合标签
            top_anomalies['label'] = top_anomalies['country'] + ' - ' + top_anomalies['Concept']
            y_col = 'label'
            y_label = '国家-概念'
        elif 'Concept' in top_anomalies.columns:
            y_col = 'Concept'
            y_label = '概念'
        else:
            y_col = top_anomalies.index
            y_label = '记录'
        
        fig = px.bar(
            top_anomalies,
            x='inconsistency',
            y=y_col,
            orientation='h',
            color='inconsistency',
            color_continuous_scale='Reds',
            title=f'言行不一致度最高的 {display_count} 个案例',
            labels={'inconsistency': '不一致度', y_col: y_label},
            hover_data=['Semantic_Cohesion', 'vote_score'] if 'Semantic_Cohesion' in top_anomalies.columns else None
        )
        
        fig.update_layout(
            height=max(400, display_count * 25),
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"""
        💡 **如何解读：**
        - 不一致度 = |演说立场强度 - 投票赞成率|
        - 值越大 = 说的和做的差异越大
        - 当前显示前 {display_count} 个最不一致的案例
        """)
        
        # 详细数据表
        st.markdown("---")
        st.subheader("📋 详细异常数据")
        
        display_cols = ['Concept', 'Semantic_Cohesion', 'vote_score', 'inconsistency']
        if 'country' in anomalies.columns:
            display_cols.insert(0, 'country')
        if 'year' in anomalies.columns:
            display_cols.insert(1, 'year')
        
        available_cols = [col for col in display_cols if col in anomalies.columns]
        st.dataframe(
            anomalies[available_cols].head(50),  # 显示前50条
            use_container_width=True, 
            height=400
        )
        
        if len(anomalies) > 50:
            st.info(f"💡 表格显示前50条，共 {len(anomalies)} 条异常记录")
        
        # 下载
        csv = anomalies.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载全部异常值数据 (CSV)",
            data=csv,
            file_name="consistency_anomalies.csv",
            mime="text/csv"
        )

# 底部导航
st.markdown("---")
st.markdown("### 🧭 返回其他页面")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_📊_Global_Overview.py", label="📊 全局语义偏移")

with col2:
    st.page_link("pages/2_🌍_Bloc_Analysis.py", label="🌍 阵营对比分析")

with col3:
    st.page_link("pages/3_✅_Consistency_Check.py", label="✅ 言行一致性")
