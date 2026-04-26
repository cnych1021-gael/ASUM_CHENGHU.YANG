import pandas as pd
import streamlit as st
from pathlib import Path
import os
import gdown

def download_models_from_drive():
    # 设定你想保存模型的路径
    save_dir = "data/user_data"
    
    # 确保文件夹存在，如果不存在就自动创建一个
    os.makedirs(save_dir, exist_ok=True)
    
    # 我们用其中一个模型文件来做检查，避免每次刷新网页都重复下载
    check_file_path = os.path.join(save_dir, "word2vec_cold_war.model")
    
    # 如果文件不存在，说明是第一次在云端运行，开始下载
    if not os.path.exists(check_file_path):
        print("未检测到模型文件，正在从 Google Drive 自动下载...")
        # 这是你提供的文件夹链接
        folder_url = "https://drive.google.com/drive/folders/1QlERW6eTkEASYL5_qS1OHY-ve89QsL2v?usp=share_link"
        
        # 使用 gdown 下载整个文件夹的内容到指定目录
        gdown.download_folder(folder_url, output=save_dir, quiet=False, use_cookies=False)
        print("模型下载完成！")

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"

@st.cache_data
def load_60_concepts():
    """加载60个核心词汇的语义偏移数据"""
    df = pd.read_csv(DATA_DIR / "TFM_60_Concepts_Shift_Ranked.csv")
    return df

@st.cache_data
def load_global_deviation():
    """加载全球国家偏差数据"""
    df = pd.read_csv(DATA_DIR / "TFM_Global_Deviation_All_Countries_60_Concepts_WITH_BLOC.csv")
    return df

@st.cache_data
def load_voting_data():
    """加载投票数据"""
    df = pd.read_parquet(DATA_DIR / "un_voting_annual_cleaned.parquet")
    return df

@st.cache_data
def load_consistency_data():
    """加载言行一致性数据"""
    df = pd.read_csv(DATA_DIR / "TFM_Speech_Action_Consistency.csv")
    return df

@st.cache_data
def load_p5_cohesion():
    """加载P5语义凝聚力数据"""
    df = pd.read_csv(DATA_DIR / "TFM_P5_Semantic_Cohesion_60.csv")
    return df

def get_concept_definition(concept):
    """获取词汇的详细定义"""
    definitions = {
        "sovereignty": "国家在其领土范围内享有的最高排他性权力和在国际法上的独立自主地位。源自联合国宪章第2条第1款的主权平等原则。",
        "law": "国际法，约束国家、国际组织等国际法主体之间关系的原则、规则和制度的总体，其渊源包括国际条约、国际习惯及一般法律原则。",
        "multilateralism": "多个国家通过制度化的合作和协商机制来解决共同问题、制定国际规则的外交实践与原则。",
        "rule_law": "联合国定义的一种治理原则，即所有人、机构和实体都必须对公开颁布、平等执行和独立裁决的法律负责。",
        "self_determination": "各国人民享有自由决定其政治地位，并自由谋求其经济、社会和文化发展的权利。源自联合国宪章与公民权利和政治权利国际公约。",
        "jurisdiction": "主权国家或国际司法机构根据国际法或国内法，对特定人员、财产或事件行使权力和做出裁决的法定职权。",
        "decolonization": "殖民地或非自治领土摆脱宗主国控制、获得政治独立并建立主权国家的历史、政治和法律过程。",
        "treaty": "国家间或其他国际法主体间以书面形式缔结并受国际法制约的国际协议。源自1969年维也纳条约法公约。",
        "diplomacy": "主权国家等国际法主体之间通过代表进行谈判、沟通以推行国家政策、处理国际关系和和平解决争端的实践活动。",
        "governance": "跨国机构、国家和非国家行为体通过正式或非正式规则，协调冲突或不同利益、管理全球公共事务的合作机制。",
        
        "human_right": "所有人与生俱来的权利，不分国籍、性别、民族、种族、宗教、语言或任何其他身份，均不可剥夺。源自1948年世界人权宣言。",
        "democracy": "一种普世价值和政府形式，其核心是人民有权自由决定其政治、经济、社会和文化制度，并全面参与生活的各个方面。",
        "equality": "国际法上的主权均等原则，以及在社会人权层面的法律面前人人平等且享有不受任何歧视的平等保护原则。",
        "social_justice": "在社会财富、资源、机会和特权的分配方面实现公平公正，联合国将其视为国家内及国家间和平与安全共处的基础。",
        "discrimination": "基于种族、肤色、性别、语言、宗教、国籍或社会出身等任何区别、排斥、限制或偏好，其目的或效果是破坏人权的平等享受。",
        "woman_right": "妇女和女童在政治、经济、社会、文化等各个领域享有与男子平等的基本人权和自由。源自消除对妇女一切形式歧视公约。",
        "freedom_expression": "人人享有寻求、接受和传递各种消息和思想的自由，不论国界，也不论采取何种媒介。源自公民权利和政治权利国际公约。",
        "civil_right": "保护个人自由免受政府、社会组织和个人无端侵犯的权利，保障个人在不受歧视或压迫的情况下参与国家政治生活的能力。",
        "minority": "在国家人口中处于非主导地位的群体，具有区别于多数人的独特民族、宗教或语言特征，享有保留和发展其特征的权利。",
        "pluralism": "认可并容纳社会中存在多种不同利益、信仰、种族、文化和生活方式，并鼓励其和平共处的政治与社会原则。",
        
        "international_security": "保护国际体系和主权国家免受军事、外交或非传统威胁的机制与状态，现代概念已扩展至人类安全(Human Security)。",
        "terrorism": "旨在引起公众恐慌，为了政治、意识形态或宗教目的，非法且故意对平民或非战斗人员实施致命暴力的行为。",
        "peacekeeping": "联合国部署军事、警察和文职人员，帮助饱受冲突蹂躏的国家创造实现持久和平条件的特殊实操行动。",
        "disarmament": "减少、限制或彻底废除一国军事力量或特定武器的国际多边努力。",
        "arms_control": "国家间就武器的生产、开发、储备、部署或使用达成限制的国际条约或双边协议。",
        "armed_conflict": "国家武装力量之间或政府军与有组织的武装团体之间持续进行的敌对暴力行动。",
        "conflict_resolution": "通过和平手段介入危机，消除导致武装冲突的根源并达成最终和解的过程。",
        "nuclear_non_proliferation": "防止核武器及其运载工具技术的扩散，促进和平利用核能，并以最终彻底销毁核武器为目标的国际机制。源自不扩散核武器条约。",
        "sanction": "联合国安理会为应对威胁和平、破坏和平或侵略行为，采取的非武力强制性措施。",
        "ceasefire": "交战各方之间达成的暂时或永久停止敌对行动和使用武器的协议，通常是和平谈判的前提。",
        
        "economic_development": "旨在改善国家和社区的财富、政治自决和相对福祉的定量与定性过程，通常涉及产业结构优化和生产率提高。",
        "sustainable_development": "既满足当代人的需求，又不对后代人满足其需求的能力构成危害的发展模式，涵盖经济、社会和环境三大支柱。",
        "international_trade": "跨越国界和特定海关领域的资本、商品和服务的自愿交换活动。",
        "poverty_eradication": "通过经济增长、社会保障和国际合作，在全球范围内彻底消除一切形式的极端贫穷。联合国可持续发展目标SDG 1。",
        "foreign_direct_investment": "一国投资者为在另一国境内的企业获得持久利益及控制权而进行的跨国生产性投资活动。",
        "external_debt": "任何国家、企业或私人实体欠非本地居民的外币债务总和，需以外汇、商品或服务偿还，是发展中国家面临的主要经济瓶颈之一。",
        "globalization": "商品、服务、资本、技术、人员和思想在世界范围内的加速流动与一体化过程。",
        "tariff": "一国政府对进出口商品征收的税收，通常用作保护本国产业的贸易壁垒或增加政府财政收入的手段。",
        "free_trade": "国家之间对进出口商品和服务不设置关税、配额或其他政府干预等贸易壁垒的国际经济政策原则。",
        "economic_growth": "一个国家或地区在一定时期内生产的最终商品和服务的总市场价值的绝对增加。",
        
        "climate_change": "直接或间接归因于人类活动导致全球大气组成改变，并在可比时间段内观察到的气候自然变异。源自联合国气候变化框架公约。",
        "environmental_protection": "个人、组织和政府出于维护自然环境及其资源的目的，采取防止生态退化和污染的保护措施。",
        "biodiversity": "所有来源的活的生物体中的变异性，包括陆地、海洋生态系统及其构成的生态综合体，涵盖物种内、物种间和生态系统的多样性。",
        "pollution": "将可能对人类健康、生物资源、生态系统或合法物质利用造成严重危害的物质或能量引入环境的行为。",
        "water_resource": "可供人类、工业、农业和生态系统利用的淡水，是生命维持和可持续发展的核心自然资本。",
        "deforestation": "为将土地用于农业、牧业、城市建设或其他非森林用途，而大量、永久性地清除或破坏森林生态系统的行为。",
        "renewable_energy": "取自自然界且补充速度快于消耗速度的清洁能源，是应对气候变化的主要替代方案。",
        "desertification": "在干旱、半干旱和亚湿旱地区，由于各种因素造成的土地生产力退化现象。",
        "natural_disaster": "由于自然界异常极端变异对人类社会、经济系统和环境造成严重破坏的灾难性事件。",
        "greenhouse_gas_emission": "将二氧化碳、甲烷等能吸收红外辐射的吸热气体排放到大气中的行为，被认为是导致全球变暖的直接物理推手。",
        
        "technology_transfer": "科技知识、技能和制造方法从其起源地向更广泛的受众转移和普及的过程。",
        "information_technology": "利用计算机、网络、存储和通信设备来创建、处理、存储、保护和交换各类电子数据的技术的统称。",
        "artificial_intelligence": "计算机系统执行通常需要人类智能的任务的能力，涉及深远的科技伦理与战略竞争。",
        "cultural_heritage": "具有突出历史、美学、考古、科学或人类学价值的物质遗存和非物质文化表现形式的总称。",
        "education": "传播知识、技能、价值观的系统性社会过程，联合国将其视为一项基本人权及实现社会流动与消除不平等的赋权手段。",
        "innovation": "将新思想、新方法或新技术发明转化为能创造重大社会、经济或公共利益的产品、服务或过程的转化活动。",
        "cybersecurity": "保护互联网连接系统免受恶意攻击、破坏、未经授权访问或数据泄露的防御实践。",
        "digital_divide": "不同人口结构、经济阶层或地理区域在获取和使用信息与通信技术及互联网服务方面的严重差距。",
        "intellectual_property": "由人类智力创造的成果在法律上享有的专有权利，旨在保护和激励全球科技与文化创新。",
        "science_technology": "系统性地积累关于客观世界的知识体系，并将这些原理应用于解决实际问题或开发生产力工具的综合过程。",
    }
    return definitions.get(concept, f"{concept}，国际关系中的重要概念")

def get_six_dimensions():
    """返回六大维度分类"""
    return {
        "维度一: 政治法律": ["sovereignty", "law", "multilateralism", "rule_law", "self_determination", 
                           "jurisdiction", "decolonization", "treaty", "diplomacy", "governance"],
        "维度二: 人权意识": ["human_right", "democracy", "equality", "social_justice", "discrimination", 
                           "woman_right", "freedom_expression", "civil_right", "minority", "pluralism"],
        "维度三: 安全冲突": ["international_security", "terrorism", "peacekeeping", "disarmament", "arms_control", 
                           "armed_conflict", "conflict_resolution", "nuclear_non_proliferation", "sanction", "ceasefire"],
        "维度四: 经济贸易": ["economic_development", "sustainable_development", "international_trade", 
                           "poverty_eradication", "foreign_direct_investment", "external_debt", "globalization", 
                           "tariff", "free_trade", "economic_growth"],
        "维度五: 环境资源": ["climate_change", "environmental_protection", "biodiversity", "pollution", 
                           "water_resource", "deforestation", "renewable_energy", "desertification", 
                           "natural_disaster", "greenhouse_gas_emission"],
        "维度六: 科技文化": ["technology_transfer", "information_technology", "artificial_intelligence", 
                           "cultural_heritage", "education", "innovation", "cybersecurity", "digital_divide", 
                           "intellectual_property", "science_technology"]
    }

# 🚀 关键修改：在这里调用函数，确保只要导入此文件就会执行下载检查！
download_models_from_drive()
