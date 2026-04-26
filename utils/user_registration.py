"""
用户注册和A/B测试管理系统

功能：
1. 用户注册（姓名、机构、角色）
2. 自动A/B分组
3. 记录用户行为数据
4. 数据持久化存储
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import hashlib
import random

# 数据存储路径
USER_DATA_DIR = Path('data/user_data')
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_REGISTRY_FILE = USER_DATA_DIR / 'user_registry.json'
USER_INTERACTIONS_FILE = USER_DATA_DIR / 'user_interactions.csv'

def initialize_user_registry():
    """初始化用户注册表"""
    if not USER_REGISTRY_FILE.exists():
        with open(USER_REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    else:
        # 验证现有文件是否有效
        try:
            with open(USER_REGISTRY_FILE, 'r', encoding='utf-8') as f:
                json.load(f)
        except (json.JSONDecodeError, ValueError):
            # 文件损坏，备份并重新创建
            import shutil
            backup_file = USER_REGISTRY_FILE.with_suffix('.json.corrupted')
            shutil.copy(USER_REGISTRY_FILE, backup_file)
            with open(USER_REGISTRY_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

def load_user_registry():
    """加载用户注册表"""
    initialize_user_registry()
    try:
        with open(USER_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # JSON文件损坏，备份并创建新的
        if USER_REGISTRY_FILE.exists():
            import shutil
            backup_file = USER_REGISTRY_FILE.with_suffix('.json.backup')
            shutil.copy(USER_REGISTRY_FILE, backup_file)
            print(f"⚠️ JSON文件损坏，已备份到: {backup_file}")
        
        # 创建新的空注册表
        with open(USER_REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}

def save_user_registry(registry):
    """保存用户注册表"""
    with open(USER_REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def generate_user_id(name, institution):
    """生成用户唯一ID"""
    # 使用姓名+机构+时间戳生成唯一ID
    raw = f"{name}_{institution}_{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def assign_ab_group():
    """随机分配A/B测试组"""
    # 50%概率分配到实验组
    return 'experiment' if random.random() > 0.5 else 'control'

def register_user(name, institution, role, language='zh'):
    """
    注册新用户
    
    Args:
        name: 用户姓名
        institution: 机构名称
        role: 用户角色 (novice/expert)
        language: 界面语言
    
    Returns:
        user_id: 用户唯一ID
    """
    registry = load_user_registry()
    
    # 生成用户ID
    user_id = generate_user_id(name, institution)
    
    # 分配A/B测试组
    ab_group = assign_ab_group()
    
    # 创建用户档案
    user_profile = {
        'user_id': user_id,
        'name': name,
        'institution': institution,
        'role': role,
        'language': language,
        'ab_group': ab_group,
        'registered_at': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat(),
        'total_sessions': 0,
        'total_clicks': 0,
        'explored_concepts': [],
        'explored_dimensions': []  # 改为list，不用set
    }
    
    # 保存到注册表
    registry[user_id] = user_profile
    save_user_registry(registry)
    
    return user_id, ab_group

def load_user_profile(user_id):
    """加载用户档案"""
    registry = load_user_registry()
    return registry.get(user_id)

def update_user_activity(user_id):
    """更新用户活跃时间"""
    registry = load_user_registry()
    if user_id in registry:
        registry[user_id]['last_active'] = datetime.now().isoformat()
        registry[user_id]['total_sessions'] += 1
        save_user_registry(registry)

def record_user_interaction(user_id, action, concept=None, dimension=None, page=None):
    """
    记录用户交互行为
    
    Args:
        user_id: 用户ID
        action: 行为类型 (view_concept, click, explore, etc.)
        concept: 点击的概念
        dimension: 所属维度
        page: 所在页面
    """
    # 加载或创建交互记录
    if USER_INTERACTIONS_FILE.exists():
        df = pd.read_csv(USER_INTERACTIONS_FILE)
    else:
        df = pd.DataFrame(columns=[
            'timestamp', 'user_id', 'action', 'concept', 
            'dimension', 'page', 'ab_group'
        ])
    
    # 获取用户AB组
    user_profile = load_user_profile(user_id)
    ab_group = user_profile['ab_group'] if user_profile else 'unknown'
    
    # 添加新记录
    new_record = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'action': action,
        'concept': concept,
        'dimension': dimension,
        'page': page,
        'ab_group': ab_group
    }
    
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_csv(USER_INTERACTIONS_FILE, index=False)
    
    # 更新用户档案统计
    if concept:
        registry = load_user_registry()
        if user_id in registry:
            registry[user_id]['total_clicks'] += 1
            if concept not in registry[user_id]['explored_concepts']:
                registry[user_id]['explored_concepts'].append(concept)
            if dimension and isinstance(registry[user_id]['explored_dimensions'], list):
                if dimension not in registry[user_id]['explored_dimensions']:
                    registry[user_id]['explored_dimensions'].append(dimension)
            save_user_registry(registry)

def get_ab_test_statistics():
    """获取A/B测试统计数据"""
    registry = load_user_registry()
    
    if not registry:
        return None
    
    # 统计两组用户
    control_users = [u for u in registry.values() if u['ab_group'] == 'control']
    experiment_users = [u for u in registry.values() if u['ab_group'] == 'experiment']
    
    # 计算指标
    stats = {
        'total_users': len(registry),
        'control_count': len(control_users),
        'experiment_count': len(experiment_users),
        'control_avg_clicks': sum(u['total_clicks'] for u in control_users) / len(control_users) if control_users else 0,
        'experiment_avg_clicks': sum(u['total_clicks'] for u in experiment_users) / len(experiment_users) if experiment_users else 0,
        'control_avg_concepts': sum(len(u['explored_concepts']) for u in control_users) / len(control_users) if control_users else 0,
        'experiment_avg_concepts': sum(len(u['explored_concepts']) for u in experiment_users) / len(experiment_users) if experiment_users else 0
    }
    
    return stats

def show_user_login_page(language='zh'):
    """
    显示用户登录/注册页面
    
    Returns:
        bool: 是否完成登录
    """
    
    # 多语言文本
    texts = {
        'zh': {
            'welcome': '欢迎！请先告诉我们关于您的信息',
            'identity': '您的身份是？',
            'name': '您的姓名：',
            'institution': '您的机构（学校/企业）：',
            'name_help': '请输入您的真实姓名',
            'institution_help': '例如：马德里康普顿斯大学',
            'novice': '🎓 学生 / 记者（新手模式）',
            'expert': '👔 研究员 / 外交官（专家模式）',
            'start': '开始探索',
            'novice_desc': '**✨ 新手模式包含：**\n- 简化的图表和解释\n- 完整的概念定义\n- 词云可视化\n- 推荐系统',
            'expert_desc': '**🔬 专家模式包含：**\n- 完整的数据分析工具\n- 7个高级页面（含A/B测试）\n- 可下载原始数据\n- 统计显著性检验',
            'required': '⚠️ 请填写所有必填项',
            'welcome_back': '欢迎回来',
            'assigned_group': '您已被分配到',
            'control_group': '对照组（无推荐）',
            'experiment_group': '实验组（有推荐）'
        },
        'en': {
            'welcome': 'Welcome! Please tell us about yourself',
            'identity': 'Your profile:',
            'name': 'Your name:',
            'institution': 'Your institution (University/Company):',
            'name_help': 'Please enter your real name',
            'institution_help': 'e.g., Complutense University of Madrid',
            'novice': '🎓 Student / Journalist (Novice Mode)',
            'expert': '👔 Researcher / Diplomat (Expert Mode)',
            'start': 'Start Exploring',
            'novice_desc': '**✨ Novice Mode includes:**\n- Simplified charts\n- Complete definitions\n- Word clouds\n- Recommendation system',
            'expert_desc': '**🔬 Expert Mode includes:**\n- Full analysis tools\n- 7 advanced pages\n- Downloadable data\n- Statistical testing',
            'required': '⚠️ Please fill in all required fields',
            'welcome_back': 'Welcome back',
            'assigned_group': 'You have been assigned to',
            'control_group': 'Control Group (no recommendations)',
            'experiment_group': 'Experiment Group (with recommendations)'
        },
        'es': {
            'welcome': '¡Bienvenido! Por favor, cuéntanos sobre ti',
            'identity': 'Tu perfil:',
            'name': 'Tu nombre:',
            'institution': 'Tu institución (Universidad/Empresa):',
            'name_help': 'Por favor ingresa tu nombre real',
            'institution_help': 'ej: Universidad Complutense de Madrid',
            'novice': '🎓 Estudiante / Periodista (Modo Principiante)',
            'expert': '👔 Investigador / Diplomático (Modo Experto)',
            'start': 'Comenzar a Explorar',
            'novice_desc': '**✨ Modo Principiante incluye:**\n- Gráficos simplificados\n- Definiciones completas\n- Nubes de palabras\n- Sistema de recomendación',
            'expert_desc': '**🔬 Modo Experto incluye:**\n- Herramientas completas\n- 7 páginas avanzadas\n- Datos descargables\n- Pruebas estadísticas',
            'required': '⚠️ Por favor completa todos los campos requeridos',
            'welcome_back': 'Bienvenido de nuevo',
            'assigned_group': 'Has sido asignado al',
            'control_group': 'Grupo de Control (sin recomendaciones)',
            'experiment_group': 'Grupo Experimental (con recomendaciones)'
        }
    }
    
    t = texts.get(language, texts['zh'])
    
    st.markdown("---")
    st.header(f"👤 {t['welcome']}")
    
    st.subheader(t['identity'])
    
    # 角色选择
    role_options = [t['novice'], t['expert']]
    identity = st.radio(
        "",
        role_options,
        key="identity_choice_login"
    )
    
    # 显示模式说明
    if t['novice'] in identity:
        st.info(t['novice_desc'])
        selected_role = 'novice'
    else:
        st.info(t['expert_desc'])
        selected_role = 'expert'
    
    st.markdown("---")
    
    # 用户信息输入
    col1, col2 = st.columns(2)
    
    with col1:
        user_name = st.text_input(
            t['name'],
            placeholder="e.g., 张三 / John Smith / María García",
            help=t['name_help'],
            key="user_name_input"
        )
    
    with col2:
        user_institution = st.text_input(
            t['institution'],
            placeholder="e.g., UCM / Harvard / UNAM",
            help=t['institution_help'],
            key="user_institution_input"
        )
    
    st.markdown("---")
    
    # 开始按钮
    if st.button(t['start'], type="primary", use_container_width=True):
        # 验证输入
        if not user_name or not user_institution:
            st.error(t['required'])
            return False
        
        # 注册用户
        user_id, ab_group = register_user(
            name=user_name,
            institution=user_institution,
            role=selected_role,
            language=language
        )
        
        # 保存到session_state
        st.session_state.user_profile = {
            'user_id': user_id,
            'name': user_name,
            'institution': user_institution,
            'role': selected_role,
            'language': language,
            'ab_group': ab_group,
            'expertise_level': 'beginner' if selected_role == 'novice' else 'professional'
        }
        
        # 显示分组信息
        st.success(f"✅ {t['welcome_back']}, {user_name}!")
        
        group_text = t['experiment_group'] if ab_group == 'experiment' else t['control_group']
        st.info(f"🎯 {t['assigned_group']}: **{group_text}**")
        
        st.balloons()
        
        return True
    
    return False

# 导出函数供其他模块使用
__all__ = [
    'show_user_login_page',
    'record_user_interaction',
    'load_user_profile',
    'update_user_activity',
    'get_ab_test_statistics'
]
