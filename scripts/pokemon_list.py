# -*- coding: utf-8 -*-
"""
宝可梦基础列表数据抓取脚本
从神奇宝贝百科抓取宝可梦基础信息列表
"""
import os

from config import URLS, DATA_PATH
from network_utils import get_soup
from fixed_data import NEW_NAMES
from utils import file_exists, save_to_file, should_skip_existing_file
from logger_utils import ProgressLogger, ScriptLogger
from progress_utils import ProgressBar

# 初始化日志器
script_logger = ScriptLogger('pokemon_list')
progress_logger = ProgressLogger('pokemon_list')

def get_pokemon_list():
    """抓取宝可梦基础列表"""
    script_logger.info("开始抓取宝可梦基础列表")
    
    # 检查是否需要跳过
    list_file = os.path.join(DATA_PATH, 'pokemon_list.json')
    if should_skip_existing_file(list_file):
        script_logger.info("宝可梦列表文件较新，跳过抓取")
        return
    
    # 获取页面内容
    soup = get_soup(URLS['pokemon_list'])
    if not soup:
        script_logger.error("无法获取宝可梦列表页面")
        return
    
    # 解析宝可梦列表
    table = soup.find('table', class_='eplist')
    if not table:
        script_logger.error("未找到宝可梦列表表格")
        return
    
    tr_list = table.find_all('tr')
    pokemon_simple_list = []
    
    progress_logger.start(len(tr_list))
    progress_bar = ProgressBar(len(tr_list), "解析宝可梦列表")
    
    for i, tr in enumerate(tr_list):
        td_list = tr.find_all('td')
        if len(td_list) == 4:
            try:
                index_no = td_list[0].text.strip().replace('#', '')
                name = td_list[1].find('a').text.strip()
                name_en = td_list[3].find('a').text.strip()
                name_jp = td_list[2].find('a').text.strip()
                
                # 使用名称映射
                actual_name = NEW_NAMES.get(name, name)
                
                pokemon_simple_list.append({
                    'index': index_no,
                    'name': actual_name,
                    'name_en': name_en,
                    'name_jp': name_jp
                })
                
                progress_bar.update(1, f"解析: {actual_name}")
                
            except Exception as e:
                script_logger.warning(f"解析宝可梦信息失败: 行{i} - {e}")
        
        progress_logger.update(f"解析第 {i+1} 行")
    
    script_logger.info(f"成功解析 {len(pokemon_simple_list)} 个宝可梦")
    
    # 保存基础列表
    if save_to_file(list_file, pokemon_simple_list):
        script_logger.info(f"宝可梦基础列表保存成功: {list_file}")
    else:
        script_logger.error(f"宝可梦基础列表保存失败: {list_file}")
    
    progress_logger.finish(len(pokemon_simple_list), 0)
    return pokemon_simple_list

if __name__ == '__main__':
    try:
        progress_logger.start()
        pokemon_list = get_pokemon_list()
        
        if pokemon_list:
            script_logger.info(f"宝可梦基础列表抓取完成，共 {len(pokemon_list)} 个")
        else:
            script_logger.error("宝可梦基础列表抓取失败")
            
    except Exception as e:
        script_logger.critical(f"脚本执行异常: {e}")
    finally:
        progress_logger.finish()