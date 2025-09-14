# -*- coding: utf-8 -*-
"""
宝可梦数据抓取项目配置文件
"""
import os

# 基础路径配置
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, 'data')
IMAGES_PATH = os.path.join(DATA_PATH, 'images')

# 数据文件路径
POKEMON_DATA_PATH = os.path.join(DATA_PATH, 'pokemon')
ABILITY_DATA_PATH = os.path.join(DATA_PATH, 'ability')
MOVE_DATA_PATH = os.path.join(DATA_PATH, 'move')
DREAM_IMAGES_PATH = os.path.join(IMAGES_PATH, 'dream')

# 确保目录存在
for path in [POKEMON_DATA_PATH, ABILITY_DATA_PATH, MOVE_DATA_PATH, DREAM_IMAGES_PATH]:
    os.makedirs(path, exist_ok=True)

# 网络配置
NETWORK_CONFIG = {
    'base_url': 'https://wiki.52poke.com/wiki/',
    'headers': {
        'Accept-Language': 'zh-Hans',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    },
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 2,
    'request_delay': 1,  # 请求间隔秒数
    'retry_status_codes': [429, 500, 502, 503, 504]
}

# URL配置
URLS = {
    'pokemon_list': 'https://wiki.52poke.com/wiki/宝可梦列表（按全国图鉴编号）/简单版',
    'pokemon_full_list': 'https://wiki.52poke.com/wiki/宝可梦列表（按全国图鉴编号）',
    'ability_list': 'https://wiki.52poke.com/wiki/特性列表',
    'move_list': 'https://wiki.52poke.com/wiki/招式列表',
    'dream_images': 'https://wiki.52poke.com/index.php?title=Category:宝可梦版权绘',
    'pokemon_detail': lambda name: f'https://wiki.52poke.com/wiki/{name}',
    'ability_detail': lambda name: f'https://wiki.52poke.com/wiki/{name}（特性）',
    'move_detail': lambda name: f'https://wiki.52poke.com/wiki/{name}（招式）' if name in SPECIAL_MOVES else f'https://wiki.52poke.com/wiki/{name}'
}

# 特殊招式列表（需要特殊URL处理）
SPECIAL_MOVES = ['灼热暴冲', '黑暗暴冲', '剧毒暴冲', '格斗暴冲', '魔法暴冲']

# 脚本执行顺序配置
SCRIPT_EXECUTION_ORDER = [
    {
        'name': 'pokemon_list.py',
        'description': '抓取宝可梦基础列表',
        'required': True,
        'estimated_time': 30
    },
    {
        'name': 'ability_list.py', 
        'description': '抓取特性列表',
        'required': True,
        'estimated_time': 20
    },
    {
        'name': 'move_list.py',
        'description': '抓取招式列表', 
        'required': True,
        'estimated_time': 25
    },
    {
        'name': 'pokemon.py',
        'description': '抓取宝可梦详细信息',
        'required': True,
        'estimated_time': 1800  # 30分钟，最耗时的步骤
    },
    {
        'name': 'ability.py',
        'description': '抓取特性详细信息',
        'required': True,
        'estimated_time': 600  # 10分钟
    },
    {
        'name': 'move.py',
        'description': '抓取招式详细信息',
        'required': True,
        'estimated_time': 900  # 15分钟
    },
    {
        'name': 'pokemon_full_list.py',
        'description': '生成完整宝可梦列表',
        'required': True,
        'estimated_time': 120  # 2分钟
    },
    {
        'name': 'download_dream_image.py',
        'description': '下载宝可梦图片',
        'required': False,  # 可选
        'estimated_time': 900  # 15分钟
    }
]

# 日志配置
LOG_CONFIG = {
    'log_file': os.path.join(BASE_PATH, 'pokemon_data_scraper.log'),
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 3
}

# 进度显示配置
PROGRESS_CONFIG = {
    'show_percentage': True,
    'show_eta': True,
    'show_speed': True,
    'bar_length': 50,
    'update_interval': 0.1
}

