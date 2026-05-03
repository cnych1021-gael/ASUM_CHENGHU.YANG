"""
A/B 测试模拟用户生成器
生成100个模拟用户进行A/B测试

实验组（experiment）：使用推荐系统
对照组（control）：无推荐系统

预期效果：实验组的探索深度、参与度、广度都应优于对照组
"""

import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

# 配置
N_USERS = 100  # 总用户数
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 60个概念（按维度）
DIMENSIONS = {
    "政治法律": ["sovereignty", "democracy", "human_right", "self_determination", "rule_of_law", "freedom", "justice", "pluralism", "election", "constitution"],
    "安全冲突": ["war", "peace", "terrorism", "security", "conflict", "weapon", "nuclear", "military", "violence", "threat"],
    "经济发展": ["economy", "development", "trade", "poverty", "globalization", "investment", "growth", "inequality", "industry", "market"],
    "国际秩序": ["multilateralism", "cooperation", "diplomacy", "alliance", "treaty", "negotiation", "agreement", "partnership", "dialogue", "consensus"],
    "人文社会": ["education", "culture", "religion", "gender", "youth", "minority", "migration", "refugee", "identity", "diversity"],
    "环境科技": ["climate", "environment", "energy", "sustainability", "technology", "innovation", "biodiversity", "pollution", "resource", "ocean"]
}

ALL_CONCEPTS = [c for cs in DIMENSIONS.values() for c in cs]
ALL_DIMS = list(DIMENSIONS.keys())

# 6 个页面
PAGES = ["Global Overview", "Bloc Analysis", "Consistency Check", "Expert Lab", "User Dashboard", "AB Test"]

# 模拟姓名
FIRST_NAMES = ["Wang", "Li", "Zhang", "Chen", "Liu", "Yang", "Zhao", "Huang", "Zhou", "Wu",
               "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore",
               "García", "Martínez", "López", "Hernández", "González"]
INSTITUTIONS = ["Universidad Complutense", "Tsinghua University", "Harvard University", 
                "Oxford University", "MIT", "UC Berkeley", "北京大学", "清华大学",
                "Independent Researcher", "Think Tank", "Government Analyst"]


def generate_user_id(idx):
    """生成用户ID"""
    return f"user_{idx:04d}"


def generate_random_name():
    """生成随机姓名"""
    return random.choice(FIRST_NAMES) + " " + ''.join(random.choices(string.ascii_uppercase, k=2))


def simulate_user_behavior(group):
    """
    模拟用户行为
    
    实验组：探索深度 8-25，参与度 4-8，广度 3-6
    对照组：探索深度 2-12，参与度 2-5，广度 1-3
    """
    
    if group == 'experiment':
        # 实验组：受推荐系统影响，探索更多
        n_concepts = random.randint(8, 25)
        n_pages_visits = random.randint(15, 40)
        n_dimensions = random.randint(3, 6)
        session_minutes = random.randint(10, 45)
        ai_requests = random.randint(2, 10)  # 实验组更频繁使用AI
    else:
        # 对照组：仅探索基础内容
        n_concepts = random.randint(2, 12)
        n_pages_visits = random.randint(5, 20)
        n_dimensions = random.randint(1, 3)
        session_minutes = random.randint(3, 20)
        ai_requests = random.randint(0, 4)
    
    # 选择探索的维度
    selected_dims = random.sample(ALL_DIMS, n_dimensions)
    
    # 从这些维度中选择概念
    available_concepts = []
    for dim in selected_dims:
        available_concepts.extend(DIMENSIONS[dim])
    
    # 实际点击的概念
    n_concepts = min(n_concepts, len(available_concepts))
    clicked_concepts = random.sample(available_concepts, n_concepts)
    
    # 每个概念点击次数（1-5次）
    click_counts = {c: random.randint(1, 5) for c in clicked_concepts}
    
    # 兴趣权重
    interest_weights = {dim: random.randint(1, 10) for dim in selected_dims}
    
    # 访问页面
    visited_pages = []
    for _ in range(n_pages_visits):
        page = random.choice(PAGES)
        visited_pages.append({
            'page': page,
            'time': (datetime.now() - timedelta(minutes=random.randint(0, session_minutes))).isoformat()
        })
    
    # AI 请求记录
    ai_request_records = []
    if clicked_concepts:
        sample_concepts_for_ai = random.sample(clicked_concepts, min(ai_requests, len(clicked_concepts)))
        for c in sample_concepts_for_ai:
            ai_request_records.append({
                'concept': c,
                'time': (datetime.now() - timedelta(minutes=random.randint(0, session_minutes))).isoformat()
            })
    
    return {
        'clicked_concepts': click_counts,
        'interest_weights': interest_weights,
        'viewed_pages': visited_pages,
        'ai_requests': ai_request_records,
        'session_duration_minutes': session_minutes,
        'metrics': {
            'depth': len(clicked_concepts),  # 探索深度
            'engagement': len(set(p['page'] for p in visited_pages)),  # 参与度（不同页面数）
            'breadth': len(selected_dims),  # 探索广度（维度数）
            'ai_usage': len(ai_request_records)  # AI使用频率
        }
    }


def generate_users():
    """生成所有用户"""
    users = {}
    ab_test_data = []
    
    print(f"🚀 开始生成 {N_USERS} 个模拟用户...")
    print(f"   实验组：{N_USERS // 2} 人")
    print(f"   对照组：{N_USERS // 2} 人")
    print()
    
    for i in range(N_USERS):
        user_id = generate_user_id(i)
        
        # 一半实验组，一半对照组
        group = 'experiment' if i < N_USERS // 2 else 'control'
        
        # 角色：70% novice, 30% expert
        role = 'novice' if random.random() < 0.7 else 'expert'
        
        # 模拟行为
        behavior = simulate_user_behavior(group)
        
        # 用户基本信息（用于 users.json）
        users[user_id] = {
            'password': 'demo123',  # 演示用密码
            'name': generate_random_name(),
            'institution': random.choice(INSTITUTIONS),
            'role': role,
            'ab_group': group,
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        
        # A/B 测试数据
        ab_test_data.append({
            'user_id': user_id,
            'name': users[user_id]['name'],
            'role': role,
            'ab_group': group,
            'institution': users[user_id]['institution'],
            **behavior['metrics'],
            'session_minutes': behavior['session_duration_minutes'],
            'clicked_concepts': behavior['clicked_concepts'],
            'interest_weights': behavior['interest_weights'],
            'n_ai_requests': len(behavior['ai_requests'])
        })
        
        # 进度显示
        if (i + 1) % 20 == 0:
            print(f"   已生成 {i+1}/{N_USERS} 个用户...")
    
    # 保存 users.json（用于登录系统）
    users_file = DATA_DIR / "users.json"
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 用户登录数据已保存到: {users_file}")
    
    # 保存 ab_test_data.json（用于A/B测试分析）
    ab_file = DATA_DIR / "ab_test_data.json"
    with open(ab_file, 'w', encoding='utf-8') as f:
        json.dump(ab_test_data, f, ensure_ascii=False, indent=2)
    print(f"✅ A/B 测试数据已保存到: {ab_file}")
    
    # 统计摘要
    print()
    print("=" * 60)
    print("📊 数据摘要")
    print("=" * 60)
    
    exp_users = [u for u in ab_test_data if u['ab_group'] == 'experiment']
    ctrl_users = [u for u in ab_test_data if u['ab_group'] == 'control']
    
    print(f"\n🧪 实验组 ({len(exp_users)} 人)：")
    print(f"   平均探索深度: {sum(u['depth'] for u in exp_users) / len(exp_users):.1f}")
    print(f"   平均参与度:   {sum(u['engagement'] for u in exp_users) / len(exp_users):.1f}")
    print(f"   平均广度:     {sum(u['breadth'] for u in exp_users) / len(exp_users):.1f}")
    print(f"   平均AI使用:   {sum(u['ai_usage'] for u in exp_users) / len(exp_users):.1f}")
    
    print(f"\n📊 对照组 ({len(ctrl_users)} 人)：")
    print(f"   平均探索深度: {sum(u['depth'] for u in ctrl_users) / len(ctrl_users):.1f}")
    print(f"   平均参与度:   {sum(u['engagement'] for u in ctrl_users) / len(ctrl_users):.1f}")
    print(f"   平均广度:     {sum(u['breadth'] for u in ctrl_users) / len(ctrl_users):.1f}")
    print(f"   平均AI使用:   {sum(u['ai_usage'] for u in ctrl_users) / len(ctrl_users):.1f}")
    
    # 简单t-test
    try:
        from scipy import stats
        exp_depth = [u['depth'] for u in exp_users]
        ctrl_depth = [u['depth'] for u in ctrl_users]
        t_stat, p_val = stats.ttest_ind(exp_depth, ctrl_depth)
        print(f"\n📈 探索深度 t-test:")
        print(f"   t = {t_stat:.3f}, p = {p_val:.4f}")
        print(f"   {'✅ 显著差异（p < 0.05）' if p_val < 0.05 else '❌ 无显著差异'}")
    except ImportError:
        print("\n⚠️ scipy 未安装，跳过 t-test")
    
    print()
    print("🎉 生成完成！")
    print()
    print("💡 提示：")
    print("   - 这些用户的密码都是: demo123")
    print("   - 用户名格式: user_0000 到 user_0099")
    print("   - A/B 测试页面会自动读取这些数据")


if __name__ == '__main__':
    random.seed(42)  # 可重现的结果
    generate_users()
