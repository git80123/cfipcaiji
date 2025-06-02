import requests
from bs4 import BeautifulSoup
import re
import os
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# 自定义适配器，强制使用 TLS1.2
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        if hasattr(ssl, "TLSVersion"):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

# 目标URL列表
urls = [
    'https://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'https://ip.164746.xyz'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个 session 并挂载 TLS 适配器
session = requests.Session()
session.mount('https://', TLSAdapter())

# 创建一个文件来存储IP地址
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.SSLError as e:
            print(f"SSL错误，无法访问: {url}\n详细信息: {e}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {url}\n详细信息: {e}")
            continue

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 根据网站的不同结构找到包含IP地址的元素
        if url == 'https://monitor.gacjie.cn/page/cloudflare/ipv4.html':
            elements = soup.find_all('tr')
        elif url == 'https://ip.164746.xyz':
            elements = soup.find_all('tr')
        else:
            elements = soup.find_all('li')

        # 遍历所有元素,查找IP地址
        for element in elements:
            element_text = element.get_text()
            ip_matches = re.findall(ip_pattern, element_text)
            for ip in ip_matches:
                file.write(ip + '\n')

print('IP地址已保存到ip.txt文件中。')
