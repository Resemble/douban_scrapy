import random
import base64



class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(agents = crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        print(random.choice(self.agents))
        request.headers['User-Agent'] = random.choice(self.agents)

#
# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         print("-----------------******************************************")
#         # request.meta['proxy'] = "HTTP://182.240.31.137:80"
#         request.meta['proxy'] = get_proxy()
