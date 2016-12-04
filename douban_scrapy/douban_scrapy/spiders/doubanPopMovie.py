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
import copy


class DoubanMovieSpider(scrapy.Spider):
    name = "doubanPopMovie"
    allowed_domains = ["movie.douban.com", "imdb.com"]
    start_urls = [
        "https://movie.douban.com/subject/10430287/",
        "https://movie.douban.com/subject/10438140/",
        "https://movie.douban.com/subject/3025375/?from=showing",
    ]

    # try:
    #     connector = pymysql.connect(
    #         host='localhost',
    #         port=3306,
    #         user='root',
    #         passwd='root',
    #         db='douban_movie',
    #         charset='UTF8'
    #     )
    #     cursor = connector.cursor()
    # except Exception as err:
    #     print(err)
    #     sys.exit('Filed to connect database.2')

    # movie_id = 0

    def __init__(self, *a, **kwargs):
        super().__init__(*a, **kwargs)
        DEFAULT_REQUEST_HEADERS['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        self.headers = DEFAULT_REQUEST_HEADERS
        # self.headers = self.settings.get('DEFAULT_REQUEST_HEADERS')

    def parse(self, response):
        movie_id = str(response.url.split('/')[4])
        print(movie_id)
        bs_obj = BeautifulSoup(response.body, "lxml")
        content = bs_obj.find("div", id="content")
        movie_synopsis = content.find('div', id="link-report")
        if movie_synopsis is not None:
            if movie_synopsis.find("span", attrs={"class": "all hidden"}) is not None:
                print("*****************222222222222222222222")

                movie_synopsis = movie_synopsis.find("span", attrs={"class": "all hidden"}).get_text()
                # replace('\u3000\u3000', '') 去除br
                movie_synopsis = " ".join(movie_synopsis.split()).replace('\u3000\u3000', '')
            # sopu.findAll("div", attrs={"aria-lable": "xxx"});
            else:
                if movie_synopsis.find("span", attrs={"property": "v:summary"}) is not None:
                    movie_synopsis = movie_synopsis.find("span", attrs={"property": "v:summary"}).get_text()
                    movie_synopsis = " ".join(movie_synopsis.split()).replace('\u3000\u3000', '')
                else:
                    movie_synopsis = ""
        else:
            movie_synopsis = ""
        print(movie_synopsis)
