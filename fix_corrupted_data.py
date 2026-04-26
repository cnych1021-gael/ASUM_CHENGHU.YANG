#!/usr/bin/env python3
"""
一键修复损坏的用户数据文件

这个脚本会：
1. 备份损坏的文件
2. 创建新的空文件
3. 清理临时数据
"""

from pathlib import Path
import json
import shutil
from datetime import datetime

def fix_corrupted_data():
    """修复损坏的数据文件"""
    
    print("🔧 开始修复数据文件...")
    print()
    
    # 数据目录
    data_dir = Path('data/user_data')
    
    if not data_dir.exists():
        print("✅ 数据目录不存在，创建新目录...")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"   创建目录: {data_dir}")
    
    # 处理user_registry.json
    registry_file = data_dir / 'user_registry.json'
    
    if registry_file.exists():
        print(f"📁 发现注册表文件: {registry_file}")
        
        # 尝试加载
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("✅ 文件正常，无需修复")
        except json.JSONDecodeError as e:
            print(f"❌ 文件损坏: {e}")
            
            # 备份损坏的文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = data_dir / f'user_registry_corrupted_{timestamp}.json'
            shutil.copy(registry_file, backup_file)
            print(f"💾 已备份到: {backup_file}")
            
            # 创建新文件
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"✅ 已创建新文件: {registry_file}")
    else:
        print("📝 注册表文件不存在，创建新文件...")
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建: {registry_file}")
    
    # 处理interactions文件
    interactions_file = data_dir / 'user_interactions.csv'
    
    if interactions_file.exists():
        print(f"📁 发现交互记录: {interactions_file}")
        print("✅ CSV文件保持不变")
    else:
        print("📝 交互记录不存在，将在首次使用时创建")
    
    print()
    print("="*60)
    print("✅ 修复完成！")
    print("="*60)
    print()
    print("现在可以运行：")
    print("  streamlit run app.py")
    print()

if __name__ == '__main__':
    fix_corrupted_data()
