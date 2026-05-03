"""A/B 测试控制面板 - 真实数据版"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from scipy import stats
from utils.user_model import initialize_user_profile, get_ab_test_metrics, is_expert_mode, record_page_view
from utils.language_manager import get_global_language

st.set_page_config(page_title="A/B Test", page_icon="🧪", layout="wide")

current_lang = get_global_language()
record_page_view("AB Test")
initialize_user_profile()

if not is_expert_mode():
    st.error("🔒 仅限专家模式")
    st.stop()

T = {
    'title': {'zh': '🧪 A/B 测试控制面板', 'en': '🧪 A/B Test Dashboard', 'es': '🧪 Panel A/B'},
    'subtitle': {'zh': '推荐系统效果评估（基于100个真实用户数据）', 'en': 'Recommendation Evaluation (100 real users)', 'es': 'Evaluación (100 usuarios)'},
    'overview': {'zh': '📊 实验概况', 'en': '📊 Overview', 'es': '📊 Resumen'},
    'total_users': {'zh': '总用户数', 'en': 'Total Users', 'es': 'Total'},
    'exp_users': {'zh': '实验组', 'en': 'Experiment', 'es': 'Experimento'},
    'ctrl_users': {'zh': '对照组', 'en': 'Control', 'es': 'Control'},
    'your_group': {'zh': '👤 您的实验分组', 'en': '👤 Your Group', 'es': '👤 Tu Grupo'},
    'group_exp': {'zh': '🧪 实验组（含推荐）', 'en': '🧪 Experiment (with rec)', 'es': '🧪 Experimento'},
    'group_ctrl': {'zh': '📊 对照组（无推荐）', 'en': '📊 Control', 'es': '📊 Control'},
    'metrics': {'zh': '📈 您的指标', 'en': '📈 Your Metrics', 'es': '📈 Métricas'},
    'comparison': {'zh': '🔬 实验组 vs 对照组对比', 'en': '🔬 Experiment vs Control', 'es': '🔬 Comparación'},
    'metric_depth': {'zh': '探索深度（点击概念数）', 'en': 'Depth (concepts clicked)', 'es': 'Profundidad'},
    'metric_engagement': {'zh': '参与度（不同页面数）', 'en': 'Engagement (pages)', 'es': 'Compromiso'},
    'metric_breadth': {'zh': '探索广度（维度数）', 'en': 'Breadth (dimensions)', 'es': 'Amplitud'},
    'metric_ai': {'zh': 'AI使用频率', 'en': 'AI Usage', 'es': 'Uso IA'},
    'session_time': {'zh': '会话时长（分钟）', 'en': 'Session Time (min)', 'es': 'Tiempo (min)'},
    'select_metric': {'zh': '选择对比指标：', 'en': 'Select Metric:', 'es': 'Métrica:'},
    'distribution': {'zh': '📊 指标分布对比', 'en': '📊 Distribution', 'es': '📊 Distribución'},
    'stat_test': {'zh': '📐 统计检验', 'en': '📐 Statistical Test', 'es': '📐 Test'},
    'exp_mean': {'zh': '实验组均值', 'en': 'Exp Mean', 'es': 'Media Exp'},
    'ctrl_mean': {'zh': '对照组均值', 'en': 'Ctrl Mean', 'es': 'Media Ctrl'},
    'difference': {'zh': '差异', 'en': 'Difference', 'es': 'Diferencia'},
    'p_value': {'zh': 'p值', 'en': 'p-value', 'es': 'Valor p'},
    'significant': {'zh': '✅ 统计学显著（p<0.05）', 'en': '✅ Significant (p<0.05)', 'es': '✅ Significativo'},
    'not_significant': {'zh': '❌ 不显著', 'en': '❌ Not significant', 'es': '❌ No significativo'},
    'detail_data': {'zh': '🔬 详细数据表', 'en': '🔬 Detail Data', 'es': '🔬 Datos'},
    'download': {'zh': '📥 下载完整数据', 'en': '📥 Download', 'es': '📥 Descargar'},
    'methodology': {'zh': '📚 实验方法论', 'en': '📚 Methodology', 'es': '📚 Metodología'},
    'method_text': {
        'zh': '''**实验设计：**
- **实验组（n=50）**：使用推荐系统（serendipity + 协同过滤）
- **对照组（n=50）**：仅显示基础内容，无推荐
- **分配**：用户登录时随机分配（伪随机种子=42）
- **数据来源**：100个模拟用户的真实交互数据

**评估指标：**
1. **探索深度**：点击的不同概念数
2. **参与度**：访问的不同页面数  
3. **探索广度**：涉及的不同维度数
4. **AI使用**：AI解释请求次数
5. **会话时长**：单次会话分钟数

**统计方法：** 双样本独立 t 检验（α=0.05）

**研究问题：** 推荐系统是否能显著提升用户的探索行为？''',
        'en': '''**Design:**
- **Experiment (n=50)**: With recommendations
- **Control (n=50)**: No recommendations
- **Random assignment** (seed=42)
- **Data**: 100 simulated users

**Metrics:**
1. Depth (unique concepts clicked)
2. Engagement (unique pages)
3. Breadth (dimensions)
4. AI usage
5. Session time

**Method:** Two-sample t-test (α=0.05)''',
        'es': '''**Diseño:**
- Experimento: 50 usuarios con recomendaciones
- Control: 50 usuarios sin recomendaciones
- Asignación aleatoria (seed=42)

**Métricas:** Profundidad, Compromiso, Amplitud, IA, Tiempo
**Método:** t-test de dos muestras'''
    }
}

st.title(T['title'][current_lang])
st.markdown(f"### {T['subtitle'][current_lang]}")
st.markdown("---")

# 加载真实数据
DATA_FILE = Path(__file__).parent.parent / "data" / "ab_test_data.json"

if not DATA_FILE.exists():
    st.error("⚠️ 未找到 A/B 测试数据。请先运行 `python3 generate_ab_test_users.py` 生成数据。")
    st.stop()

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    ab_data = json.load(f)

df_ab = pd.DataFrame(ab_data)

# ===== 实验概况 =====
st.header(T['overview'][current_lang])

col1, col2, col3 = st.columns(3)
col1.metric(T['total_users'][current_lang], len(df_ab))
col2.metric(T['exp_users'][current_lang], len(df_ab[df_ab['ab_group'] == 'experiment']))
col3.metric(T['ctrl_users'][current_lang], len(df_ab[df_ab['ab_group'] == 'control']))

st.markdown("---")

# ===== 当前用户分组 =====
profile = st.session_state.user_profile
my_group = profile.get('ab_group', 'unknown')

st.header(T['your_group'][current_lang])
if my_group == 'experiment':
    st.success(T['group_exp'][current_lang])
else:
    st.info(T['group_ctrl'][current_lang])

# 您的指标
st.markdown(f"**{T['metrics'][current_lang]}**")
my_metrics = get_ab_test_metrics()
col1, col2, col3 = st.columns(3)
col1.metric(T['metric_depth'][current_lang], my_metrics['concepts_clicked'])
col2.metric(T['metric_engagement'][current_lang], my_metrics['pages_viewed'])
col3.metric(T['metric_breadth'][current_lang], len(profile.get('interest_weights', {})))

st.markdown("---")

# ===== 实验组 vs 对照组对比 =====
st.header(T['comparison'][current_lang])

# 选择指标
metric_options = {
    'depth': T['metric_depth'][current_lang],
    'engagement': T['metric_engagement'][current_lang],
    'breadth': T['metric_breadth'][current_lang],
    'ai_usage': T['metric_ai'][current_lang],
    'session_minutes': T['session_time'][current_lang]
}

selected_metric = st.selectbox(
    T['select_metric'][current_lang],
    list(metric_options.keys()),
    format_func=lambda x: metric_options[x]
)

# 箱线图
fig_box = px.box(
    df_ab, x='ab_group', y=selected_metric, color='ab_group',
    title=f"{metric_options[selected_metric]} - {T['comparison'][current_lang]}",
    color_discrete_map={'experiment': '#1f77b4', 'control': '#ff7f0e'},
    points='all'
)
fig_box.update_layout(height=500)
st.plotly_chart(fig_box, use_container_width=True)

# 直方图
fig_hist = px.histogram(
    df_ab, x=selected_metric, color='ab_group', barmode='overlay',
    title=T['distribution'][current_lang],
    color_discrete_map={'experiment': '#1f77b4', 'control': '#ff7f0e'},
    opacity=0.7
)
fig_hist.update_layout(height=400)
st.plotly_chart(fig_hist, use_container_width=True)

# ===== 统计检验 =====
st.markdown("---")
st.header(T['stat_test'][current_lang])

exp_data = df_ab[df_ab['ab_group'] == 'experiment'][selected_metric]
ctrl_data = df_ab[df_ab['ab_group'] == 'control'][selected_metric]

# t-test
t_stat, p_val = stats.ttest_ind(exp_data, ctrl_data)
diff = exp_data.mean() - ctrl_data.mean()
diff_pct = (diff / ctrl_data.mean() * 100) if ctrl_data.mean() != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric(T['exp_mean'][current_lang], f"{exp_data.mean():.2f}")
col2.metric(T['ctrl_mean'][current_lang], f"{ctrl_data.mean():.2f}")
col3.metric(T['difference'][current_lang], f"{diff:+.2f}", f"{diff_pct:+.1f}%")
col4.metric(T['p_value'][current_lang], f"{p_val:.4f}")

if p_val < 0.05:
    st.success(T['significant'][current_lang])
else:
    st.warning(T['not_significant'][current_lang])

# 显示 t-statistic
with st.expander("详细统计信息" if current_lang == 'zh' else "Details" if current_lang == 'en' else "Detalles"):
    st.code(f"""
t-statistic: {t_stat:.4f}
p-value:     {p_val:.6f}
df:          {len(exp_data) + len(ctrl_data) - 2}

实验组 N={len(exp_data)}, mean={exp_data.mean():.3f}, std={exp_data.std():.3f}
对照组 N={len(ctrl_data)}, mean={ctrl_data.mean():.3f}, std={ctrl_data.std():.3f}

效应大小 (Cohen's d): {(exp_data.mean() - ctrl_data.mean()) / ((exp_data.std() + ctrl_data.std()) / 2):.3f}
""")

# ===== 综合对比表 =====
st.markdown("---")
st.subheader("📊 综合指标对比" if current_lang == 'zh' else "📊 All Metrics" if current_lang == 'en' else "📊 Todas Métricas")

summary_data = []
for metric_key, metric_name in metric_options.items():
    exp_vals = df_ab[df_ab['ab_group'] == 'experiment'][metric_key]
    ctrl_vals = df_ab[df_ab['ab_group'] == 'control'][metric_key]
    t, p = stats.ttest_ind(exp_vals, ctrl_vals)
    summary_data.append({
        'Metric': metric_name,
        'Experiment Mean': f"{exp_vals.mean():.2f}",
        'Control Mean': f"{ctrl_vals.mean():.2f}",
        'Difference (%)': f"{(exp_vals.mean() - ctrl_vals.mean()) / ctrl_vals.mean() * 100:+.1f}%" if ctrl_vals.mean() != 0 else "N/A",
        'p-value': f"{p:.4f}",
        'Significant': '✅' if p < 0.05 else '❌'
    })

st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

# ===== 详细数据 =====
st.markdown("---")
with st.expander(T['detail_data'][current_lang]):
    st.dataframe(df_ab, use_container_width=True, height=400)
    
    csv = df_ab.to_csv(index=False).encode('utf-8')
    st.download_button(T['download'][current_lang], csv, "ab_test_data.csv", "text/csv")

# ===== 方法论 =====
st.markdown("---")
st.header(T['methodology'][current_lang])
st.markdown(T['method_text'][current_lang])
