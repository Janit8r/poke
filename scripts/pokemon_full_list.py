

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
from fixed_data import NEW_NAMES
from utils import save_to_file


PATH = './../data'

def get_pokemon_full_list():
  headers = {
    'Accept-Language': 'zh-Hans'
  }
  url = 'https://wiki.52poke.com/wiki/宝可梦列表（按全国图鉴编号）'

  # 配置Chrome选项以避免沙箱问题
  chrome_options = Options()
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--disable-web-security")
  chrome_options.add_argument("--allow-running-insecure-content")
  chrome_options.add_argument("--headless")  # 无头模式运行
  
  driver = webdriver.Chrome(options=chrome_options)
  
  try:
    driver.get(url)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    pokemon_full_list = []

    table_list = soup.find_all('table', class_="eplist")

    for table in table_list:
      generation = table.find_previous('h2').text.strip().replace("宝可梦", "")
      tr_list = table.find('tbody').find_all('tr')
      for tr in tr_list:
        if tr.get("data-type") is not None:
          td_list = tr.find_all('td')
          idx = td_list[0].text.strip().replace("#", "")
          name = f'''{td_list[3].find('a').text}-{td_list[3].find('small').text}''' if td_list[3].find('small') else td_list[3].find('a').text
          name_jp = td_list[4].text.strip()
          name_en = td_list[5].text.strip()
          types = tr.get('data-type').replace('惡', '恶').replace("格鬥", "格斗").strip().split(':')
          image_class = td_list[1].find('span').get('class')[-1]

          image_style = driver.find_elements(By.CLASS_NAME, image_class)[0]
          icon_position = image_style.value_of_css_property("background-position")
          pokemon = {
            "index": idx,
            "name": NEW_NAMES.get(name, name),
            "name_jp": name_jp,
            "name_en": name_en,
            "generation": generation,
            "types": [x for x in types if x != ""],
            "meta": {
              "icon_position": icon_position
            }
          }
          pokemon_full_list.append(pokemon)

    save_to_file(f'{PATH}/pokemon_full_list.json', pokemon_full_list)
    return pokemon_full_list
    
  finally:
    # 确保总是关闭驱动程序
    driver.quit()

if __name__ == '__main__':
  get_pokemon_full_list()