"""
真实用户A/B测试数据分析工具

功能：
1. 查看所有注册用户
2. 分析A/B测试结果
3. 导出数据用于展示
4. 生成统计报告
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import streamlit as st

def load_all_users():
    """加载所有用户数据"""
    user_file = Path('data/user_data/user_registry.json')
    
    if not user_file.exists():
        return pd.DataFrame()
    
    with open(user_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    if not registry:
        return pd.DataFrame()
    
    # 转换为DataFrame
    users = []
    for user_id, profile in registry.items():
        # 处理explored_dimensions可能是set的情况
        explored_dims = profile.get('explored_dimensions', [])
        if isinstance(explored_dims, set):
            explored_dims = list(explored_dims)
        
        users.append({
            'user_id': user_id,
            'name': profile.get('name', ''),
            'institution': profile.get('institution', ''),
            'role': profile.get('role', ''),
            'ab_group': profile.get('ab_group', ''),
            'registered_at': profile.get('registered_at', ''),
            'total_clicks': profile.get('total_clicks', 0),
            'explored_concepts_count': len(profile.get('explored_concepts', [])),
            'explored_dimensions_count': len(explored_dims),
            'total_sessions': profile.get('total_sessions', 0)
        })
    
    return pd.DataFrame(users)

def load_interactions():
    """加载所有交互数据"""
    interactions_file = Path('data/user_data/user_interactions.csv')
    
    if not interactions_file.exists():
        return pd.DataFrame()
    
    return pd.read_csv(interactions_file)

def calculate_ab_metrics(users_df):
    """计算A/B测试关键指标"""
    if users_df.empty:
        return None
    
    # 分组
    control = users_df[users_df['ab_group'] == 'control']
    experiment = users_df[users_df['ab_group'] == 'experiment']
    
    metrics = {
        'total_users': len(users_df),
        'control_users': len(control),
        'experiment_users': len(experiment),
        
        # 平均点击数
        'control_avg_clicks': control['total_clicks'].mean() if len(control) > 0 else 0,
        'experiment_avg_clicks': experiment['total_clicks'].mean() if len(experiment) > 0 else 0,
        
        # 平均探索概念数
        'control_avg_concepts': control['explored_concepts_count'].mean() if len(control) > 0 else 0,
        'experiment_avg_concepts': experiment['explored_concepts_count'].mean() if len(experiment) > 0 else 0,
        
        # 平均探索维度数
        'control_avg_dimensions': control['explored_dimensions_count'].mean() if len(control) > 0 else 0,
        'experiment_avg_dimensions': experiment['explored_dimensions_count'].mean() if len(experiment) > 0 else 0,
        
        # 多样性得分（维度数/6）
        'control_diversity': (control['explored_dimensions_count'].mean() / 6.0) if len(control) > 0 else 0,
        'experiment_diversity': (experiment['explored_dimensions_count'].mean() / 6.0) if len(experiment) > 0 else 0
    }
    
    # 计算提升百分比
    if metrics['control_diversity'] > 0:
        metrics['diversity_lift'] = (
            (metrics['experiment_diversity'] - metrics['control_diversity']) / 
            metrics['control_diversity'] * 100
        )
    else:
        metrics['diversity_lift'] = 0
    
    return metrics

def export_for_presentation(output_dir='data/presentation_export'):
    """导出数据用于课程展示"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    users_df = load_all_users()
    interactions_df = load_interactions()
    
    if users_df.empty:
        return None
    
    # 导出用户汇总
    users_df.to_csv(output_path / 'users_summary.csv', index=False)
    
    # 导出交互记录
    if not interactions_df.empty:
        interactions_df.to_csv(output_path / 'user_interactions.csv', index=False)
    
    # 导出A/B测试统计
    metrics = calculate_ab_metrics(users_df)
    with open(output_path / 'ab_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    # 生成报告
    report_lines = [
        "# A/B测试结果报告",
        f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## 用户统计",
        f"- 总用户数: {metrics['total_users']}",
        f"- 对照组: {metrics['control_users']}人",
        f"- 实验组: {metrics['experiment_users']}人",
        "\n## 关键指标对比",
        "\n### 探索多样性（探索维度数/6）",
        f"- 对照组平均: {metrics['control_diversity']:.3f}",
        f"- 实验组平均: {metrics['experiment_diversity']:.3f}",
        f"- **提升: {metrics['diversity_lift']:.1f}%**",
        "\n### 探索深度",
        f"- 对照组平均点击数: {metrics['control_avg_clicks']:.1f}",
        f"- 实验组平均点击数: {metrics['experiment_avg_clicks']:.1f}",
        f"- 对照组平均探索概念数: {metrics['control_avg_concepts']:.1f}",
        f"- 实验组平均探索概念数: {metrics['experiment_avg_concepts']:.1f}",
        "\n### 探索广度",
        f"- 对照组平均探索维度数: {metrics['control_avg_dimensions']:.1f}",
        f"- 实验组平均探索维度数: {metrics['experiment_avg_dimensions']:.1f}",
        "\n## 结论",
        "\n推荐系统对用户探索行为的影响：",
    ]
    
    if metrics['diversity_lift'] > 5:
        report_lines.append(f"✅ 显著提升了探索多样性（+{metrics['diversity_lift']:.1f}%）")
    elif metrics['diversity_lift'] > 0:
        report_lines.append(f"📈 轻微提升了探索多样性（+{metrics['diversity_lift']:.1f}%）")
    else:
        report_lines.append("📊 未观察到显著提升")
    
    report = '\n'.join(report_lines)
    
    with open(output_path / 'AB_TEST_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path

# Streamlit界面（可以作为独立页面使用）
def show_ab_analysis_page():
    """显示A/B测试分析页面"""
    st.header("📊 真实用户A/B测试分析")
    
    # 加载数据
    users_df = load_all_users()
    interactions_df = load_interactions()
    
    if users_df.empty:
        st.warning("⚠️ 暂无用户数据")
        st.info("""
        **如何收集真实用户数据：**
        
        1. 邀请同学使用系统（建议3-5人）
        2. 让他们正常探索10-15分钟
        3. 系统会自动记录所有行为
        4. 回到这个页面查看结果
        """)
        return
    
    # 显示统计
    metrics = calculate_ab_metrics(users_df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总用户数", metrics['total_users'])
    
    with col2:
        st.metric("对照组", metrics['control_users'])
    
    with col3:
        st.metric("实验组", metrics['experiment_users'])
    
    st.markdown("---")
    
    # 关键指标对比
    st.subheader("🎯 关键指标对比")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "探索多样性",
            f"{metrics['experiment_diversity']:.2f}",
            f"+{metrics['diversity_lift']:.1f}%" if metrics['diversity_lift'] > 0 else f"{metrics['diversity_lift']:.1f}%",
            help="实验组的平均探索维度数/6"
        )
    
    with col2:
        lift_concepts = (
            (metrics['experiment_avg_concepts'] - metrics['control_avg_concepts']) / 
            metrics['control_avg_concepts'] * 100
        ) if metrics['control_avg_concepts'] > 0 else 0
        
        st.metric(
            "探索概念数",
            f"{metrics['experiment_avg_concepts']:.1f}",
            f"+{lift_concepts:.1f}%",
            help="实验组的平均探索概念数"
        )
    
    with col3:
        lift_clicks = (
            (metrics['experiment_avg_clicks'] - metrics['control_avg_clicks']) / 
            metrics['control_avg_clicks'] * 100
        ) if metrics['control_avg_clicks'] > 0 else 0
        
        st.metric(
            "总点击数",
            f"{metrics['experiment_avg_clicks']:.1f}",
            f"+{lift_clicks:.1f}%",
            help="实验组的平均点击数"
        )
    
    st.markdown("---")
    
    # 用户列表
    st.subheader("👥 用户列表")
    
    # 添加筛选
    filter_group = st.selectbox(
        "筛选分组：",
        ['全部', '对照组', '实验组']
    )
    
    display_df = users_df.copy()
    if filter_group == '对照组':
        display_df = display_df[display_df['ab_group'] == 'control']
    elif filter_group == '实验组':
        display_df = display_df[display_df['ab_group'] == 'experiment']
    
    st.dataframe(display_df, use_container_width=True)
    
    # 导出数据
    st.markdown("---")
    st.subheader("📥 导出数据")
    
    if st.button("导出完整数据用于展示"):
        output_path = export_for_presentation()
        if output_path:
            st.success(f"✅ 数据已导出到: {output_path}")
            st.info("""
            **导出的文件：**
            - `users_summary.csv` - 用户汇总表
            - `user_interactions.csv` - 交互记录
            - `ab_metrics.json` - A/B测试指标
            - `AB_TEST_REPORT.md` - 分析报告
            """)

if __name__ == '__main__':
    show_ab_analysis_page()
