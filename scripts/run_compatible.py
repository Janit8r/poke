# -*- coding: utf-8 -*-
"""
兼容性包装脚本
为确保现有脚本能正常运行而提供的包装
"""
import sys
import os
import importlib.util
from datetime import datetime

# 添加脚本目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_script(script_name):
    """运行指定的脚本"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    print(f"🚀 开始执行: {script_name}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        # 动态导入并执行脚本
        spec = importlib.util.spec_from_file_location("temp_module", script_path)
        module = importlib.util.module_from_spec(spec)
        
        # 设置模块的__name__为'__main__'以触发if __name__ == '__main__'块
        module.__name__ = '__main__'
        
        spec.loader.exec_module(module)
        
        print("-" * 60)
        print(f"✅ {script_name} 执行成功")
        return True
        
    except Exception as e:
        print("-" * 60)
        print(f"❌ {script_name} 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 脚本执行顺序
    scripts = [
        "pokemon_list.py",
        "ability_list.py", 
        "move_list.py",
        "pokemon.py",
        "ability.py",
        "move.py",
        "pokemon_full_list.py",
        "download_dream_image.py"
    ]
    
    print("=" * 80)
    print("宝可梦数据抓取脚本执行器")
    print("=" * 80)
    
    total_start_time = datetime.now()
    results = []
    
    for i, script in enumerate(scripts):
        print(f"\n[{i+1}/{len(scripts)}] 执行脚本: {script}")
        
        # 对于图片下载脚本，询问用户是否跳过
        if script == "download_dream_image.py":
            response = input("是否下载图片？这可能需要很长时间。(y/N): ")
            if response.lower() != 'y':
                print("⏭️ 跳过图片下载")
                results.append(True)
                continue
        
        success = run_script(script)
        results.append(success)
        
        if not success:
            response = input("脚本执行失败，是否继续？(Y/n): ")
            if response.lower() == 'n':
                break
    
    # 显示总结
    total_end_time = datetime.now()
    total_duration = total_end_time - total_start_time
    
    success_count = sum(results)
    total_count = len(results)
    
    print("\n" + "=" * 80)
    print("执行总结")
    print("=" * 80)
    print(f"总脚本数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    print(f"总耗时: {total_duration}")
    print("=" * 80)

if __name__ == "__main__":
    main()

