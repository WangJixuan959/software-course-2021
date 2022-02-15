# --*--coding：UTF-8 --*--
# 姓名：汪季轩
# 项目名称：
# 开发时间：2021年12月07日18:22:33

import requests

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
zhima_url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=3&pro=&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
proxy_ip = requests.get(url=zhima_url, headers=headers)
tmp = proxy_ip.text.replace('\r', '').replace('\n', '')
proxy = {'https': 'http://' + tmp}
print(proxy)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36icanhazip.com	favicon.ico	'}
try:
    response = requests.get('http://icanhazip.com', headers=headers, proxies=proxy)
    print(proxy)
except:
    pass

