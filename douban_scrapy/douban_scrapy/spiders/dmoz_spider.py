# -*- coding: utf-8 -*-
import scrapy
from ..items import DoubanMovieItem, ImdbRatingItem, StillsLinksItem, ShortCommentsItem, PosterLinksItem, ReviewsItem
from bs4 import BeautifulSoup
import re
import pymysql
import json
import sys
import threading
from ..settings import *
import random
import string

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["movie.douban.com"]
    start_urls = [
        "https://movie.douban.com/subject/10430287/",
    ]

    def __init__(self, *a, **kwargs):
        super().__init__(*a, **kwargs)
        DEFAULT_REQUEST_HEADERS['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        self.headers = DEFAULT_REQUEST_HEADERS

    def start_requests(self):
        print("start")

    def parse(self, response):
        print("----------------")
        bs_obj = BeautifulSoup(response.body, "lxml")
        content = bs_obj.find("div", id="content")
        movie_synopsis = content.find('div', id="link-report")
        if movie_synopsis is not None:
            # sopu.findAll("div", attrs={"aria-lable": "xxx"});
            if movie_synopsis.find("span", attrs={"property": "v:summary"}) is not None:
                movie_synopsis = movie_synopsis.find("span", attrs={"property": "v:summary"}).get_text().replace(' ',
                                                                                                                 '').replace(
                    '\n', ' ').replace('\u3000\u3000', '')
            else:
                movie_synopsis = ""
        else:
            movie_synopsis = ""
        print(movie_synopsis)




