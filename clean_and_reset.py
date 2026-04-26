#!/usr/bin/env python3
"""
清理并重置系统

这个脚本会：
1. 删除所有用户数据
2. 重置session
3. 准备干净的环境
"""

import os
import shutil
from pathlib import Path

def clean_user_data():
    """清理用户数据"""
    
    print("🧹 开始清理系统...")
    print()
    
    # 数据目录
    data_dir = Path('data/user_data')
    
    if data_dir.exists():
        # 备份
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f'data/backup_{timestamp}')
        
        if list(data_dir.glob('*')):  # 如果有文件
            print(f"📦 备份现有数据到: {backup_dir}")
            shutil.copytree(data_dir, backup_dir)
        
        # 删除
        print(f"🗑️  删除用户数据目录: {data_dir}")
        shutil.rmtree(data_dir)
    
    # 重新创建
    print(f"📁 创建新的数据目录: {data_dir}")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建空的注册表
    import json
    registry_file = data_dir / 'user_registry.json'
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
    print(f"✅ 创建空注册表: {registry_file}")
    
    print()
    print("="*60)
    print("✅ 清理完成！系统已重置！")
    print("="*60)
    print()
    print("现在可以运行：")
    print("  streamlit run app.py")
    print()
    print("所有用户需要重新注册。")
    print()

if __name__ == '__main__':
    import sys
    
    print()
    print("⚠️  警告：此操作将删除所有用户数据！")
    print()
    
    response = input("确定要继续吗？(yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        clean_user_data()
    else:
        print("❌ 已取消")
        sys.exit(0)
