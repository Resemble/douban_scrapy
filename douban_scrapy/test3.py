import random
import string

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'movie.douban.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    # "Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
}
for i in range(10):
    print(i)
    print(string.ascii_letters + string.digits)
    print(random.sample(string.ascii_letters + string.digits, 11))
    DEFAULT_REQUEST_HEADERS['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
    print(DEFAULT_REQUEST_HEADERS['Cookie'])
