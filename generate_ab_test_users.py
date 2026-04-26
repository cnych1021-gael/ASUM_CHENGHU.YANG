"""
用户数据生成脚本 - 用于A/B测试演示

生成合理的用户行为数据，包括：
- 用户基本信息
- 点击历史
- 探索行为
- A/B测试分组
"""

import random
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 60个概念（按你的系统定义）
CONCEPTS = [
    # 维度一：政治法律
    'sovereignty', 'law', 'multilateralism', 'rule_law', 'self_determination',
    'state', 'territorial_integrity', 'political_stability', 'governance', 'ward',
    
    # 维度二：人权意识
    'human_right', 'democracy', 'equality', 'social_justice', 'discrimination',
    'freedom', 'civil_society', 'gender_equality', 'minority_rights', 'dignity',
    
    # 维度三：安全冲突
    'armed_conflict', 'peacekeeping', 'terrorism', 'disarmament', 'nuclear_weapons',
    'conflict_resolution', 'ceasefire', 'security_council', 'intervention', 'sanctions',
    
    # 维度四：经济贸易
    'economic_development', 'trade', 'investment', 'debt', 'poverty',
    'sustainable_development', 'globalization', 'market', 'finance', 'inequality',
    
    # 维度五：环境资源
    'climate_change', 'environment', 'biodiversity', 'natural_resources', 'pollution',
    'sustainable', 'energy', 'water', 'deforestation', 'conservation',
    
    # 维度六：科技文化
    'technology', 'education', 'health', 'culture', 'information',
    'digital', 'innovation', 'science', 'heritage', 'communication'
]

DIMENSIONS = {
    '维度一: 政治法律': CONCEPTS[0:10],
    '维度二: 人权意识': CONCEPTS[10:20],
    '维度三: 安全冲突': CONCEPTS[20:30],
    '维度四: 经济贸易': CONCEPTS[30:40],
    '维度五: 环境资源': CONCEPTS[40:50],
    '维度六: 科技文化': CONCEPTS[50:60]
}

def generate_user_profile(user_id, group='control'):
    """生成单个用户档案"""
    
    # 用户基本信息
    user_type = random.choice(['novice', 'expert'])
    
    # 用户兴趣维度（随机1-3个主要兴趣维度）
    interest_dims = random.sample(list(DIMENSIONS.keys()), random.randint(1, 3))
    
    # 生成点击历史
    click_history = []
    explored_concepts = set()
    
    # 模拟探索行为
    base_clicks = random.randint(8, 25)  # 基础点击数
    
    if group == 'experiment':
        # 实验组：有推荐，探索更多样化
        num_clicks = int(base_clicks * 1.3)  # 多30%的点击
        
        # 主要兴趣维度的概念
        main_concepts = []
        for dim in interest_dims:
            main_concepts.extend(DIMENSIONS[dim])
        
        # 60%来自主要兴趣，40%来自推荐（其他维度）
        clicks_from_interest = int(num_clicks * 0.6)
        clicks_from_serendipity = num_clicks - clicks_from_interest
        
        # 主要兴趣的点击
        for _ in range(clicks_from_interest):
            concept = random.choice(main_concepts)
            explored_concepts.add(concept)
            click_history.append({
                'concept': concept,
                'dimension': get_dimension(concept),
                'timestamp': random_timestamp()
            })
        
        # 意外发现的点击（来自其他维度）
        other_concepts = [c for c in CONCEPTS if c not in main_concepts]
        for _ in range(clicks_from_serendipity):
            concept = random.choice(other_concepts)
            explored_concepts.add(concept)
            click_history.append({
                'concept': concept,
                'dimension': get_dimension(concept),
                'timestamp': random_timestamp()
            })
    else:
        # 对照组：无推荐，探索范围窄
        num_clicks = base_clicks
        
        # 主要兴趣维度的概念
        main_concepts = []
        for dim in interest_dims:
            main_concepts.extend(DIMENSIONS[dim])
        
        # 90%来自主要兴趣，10%随机
        clicks_from_interest = int(num_clicks * 0.9)
        clicks_random = num_clicks - clicks_from_interest
        
        for _ in range(clicks_from_interest):
            concept = random.choice(main_concepts)
            explored_concepts.add(concept)
            click_history.append({
                'concept': concept,
                'dimension': get_dimension(concept),
                'timestamp': random_timestamp()
            })
        
        for _ in range(clicks_random):
            concept = random.choice(CONCEPTS)
            explored_concepts.add(concept)
            click_history.append({
                'concept': concept,
                'dimension': get_dimension(concept),
                'timestamp': random_timestamp()
            })
    
    # 计算指标
    diversity_score = len(set([c['dimension'] for c in click_history])) / 6.0
    explored_dimensions = set([c['dimension'] for c in click_history])
    session_duration = random.uniform(5, 20) if group == 'experiment' else random.uniform(3, 12)
    
    return {
        'user_id': f'user_{user_id:03d}',
        'user_type': user_type,
        'ab_group': group,
        'click_history': click_history,
        'explored_concepts': list(explored_concepts),
        'diversity_score': diversity_score,
        'explored_dimensions': len(explored_dimensions),
        'session_duration': session_duration,
        'interest_dimensions': interest_dims
    }

def get_dimension(concept):
    """获取概念所属维度"""
    for dim, concepts in DIMENSIONS.items():
        if concept in concepts:
            return dim
    return '未知'

def random_timestamp():
    """生成随机时间戳（最近7天内）"""
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 24)
    minutes_ago = random.randint(0, 60)
    
    dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return dt.isoformat()

def generate_ab_test_data(num_users=30, control_ratio=0.4):
    """
    生成A/B测试数据
    
    Args:
        num_users: 总用户数
        control_ratio: 对照组比例
    """
    
    num_control = int(num_users * control_ratio)
    num_experiment = num_users - num_control
    
    users = []
    
    # 生成对照组
    for i in range(num_control):
        users.append(generate_user_profile(i, group='control'))
    
    # 生成实验组
    for i in range(num_control, num_users):
        users.append(generate_user_profile(i, group='experiment'))
    
    return users

def save_user_data(users, output_dir='data/ab_test_users'):
    """保存用户数据"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存完整数据（JSON）
    with open(output_path / 'users_full.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    # 保存汇总数据（CSV）
    summary_data = []
    for user in users:
        summary_data.append({
            'user_id': user['user_id'],
            'user_type': user['user_type'],
            'ab_group': user['ab_group'],
            'clicks': len(user['click_history']),
            'unique_concepts': len(user['explored_concepts']),
            'diversity_score': user['diversity_score'],
            'explored_dimensions': user['explored_dimensions'],
            'session_duration': user['session_duration'],
            'main_interests': ', '.join(user['interest_dimensions'])
        })
    
    df = pd.DataFrame(summary_data)
    df.to_csv(output_path / 'users_summary.csv', index=False)
    
    # 保存点击历史（用于分析）
    click_data = []
    for user in users:
        for click in user['click_history']:
            click_data.append({
                'user_id': user['user_id'],
                'ab_group': user['ab_group'],
                'concept': click['concept'],
                'dimension': click['dimension'],
                'timestamp': click['timestamp']
            })
    
    df_clicks = pd.DataFrame(click_data)
    df_clicks.to_csv(output_path / 'click_history.csv', index=False)
    
    print(f"✅ 用户数据已保存到: {output_path}")
    print(f"   - users_full.json: 完整用户档案")
    print(f"   - users_summary.csv: 用户汇总")
    print(f"   - click_history.csv: 点击历史")
    print(f"\n📊 数据统计:")
    print(f"   总用户数: {len(users)}")
    print(f"   对照组: {len([u for u in users if u['ab_group'] == 'control'])}")
    print(f"   实验组: {len([u for u in users if u['ab_group'] == 'experiment'])}")

if __name__ == '__main__':
    # 生成30个用户（12个对照组，18个实验组）
    users = generate_ab_test_data(num_users=30, control_ratio=0.4)
    
    # 保存数据
    save_user_data(users)
    
    # 显示示例
    print("\n" + "="*60)
    print("示例用户档案：")
    print("="*60)
    
    example_user = users[0]
    print(f"用户ID: {example_user['user_id']}")
    print(f"分组: {example_user['ab_group']}")
    print(f"点击数: {len(example_user['click_history'])}")
    print(f"探索概念数: {len(example_user['explored_concepts'])}")
    print(f"多样性得分: {example_user['diversity_score']:.2f}")
    print(f"兴趣维度: {', '.join(example_user['interest_dimensions'])}")
