# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import time
from bs4 import BeautifulSoup
from scrapy import signals
from pydispatch import dispatcher
from selenium import webdriver
import re
import requests
from douban_scrapy.items import DoubanMovieItem
from ..items import DoubanMovieItem, ImdbRatingItem, StillsLinksItem
import json
import threading
from ..settings import *

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'bid="8gWdRndOu8A"; ll="118318"; gr_user_id=0e15fd61-b612-4585-848f-67efbd8cbfda; viewed="26767354_26613463_3288908_11614538_3711653_25786138_3794471_25980975_25755874_4922689"; ct=y; push_noty_num=0; push_doumail_num=0; _vwo_uuid_v2=3F90AEC7B02CF82F9075F0897A97B3DA|9b8c1dcb472d2b7a35df79d6f82a6148; ap=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1476097337%2C%22https%3A%2F%2Fwww.google.com.hk%2F%22%5D; _pk_id.100001.4cf6=6b9240f7030f2333.1470222117.20.1476099215.1476091776.; _pk_ses.100001.4cf6=*; __utma=30149280.735639331.1460979507.1476090095.1476097338.55; __utmb=30149280.0.10.1476097338; __utmc=30149280; __utmz=30149280.1475659687.53.45.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmv=30149280.15077; __utma=223695111.1630462862.1470222118.1476090095.1476097338.20; __utmb=223695111.0.10.1476097338; __utmc=223695111; __utmz=223695111.1475659687.18.15.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    'Host': 'movie.douban.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}


class DoubanpopmovieSpider(scrapy.Spider):
    name = "doubanPopMovie"
    allowed_domains = ["movie.douban.com"]
    count = 0
    start_urls = (
        # 'https://movie.douban.com/explore#!type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start=0',
        # 'http://www.imdb.com/title/tt2981768/',
        'https://movie.douban.com/subject/25921812/comments'
    )

    def __init__(self, *a, **kwargs):
        super().__init__(*a, **kwargs)

        self.headers = DEFAULT_REQUEST_HEADERS
        # self.headers = self.settings.get('DEFAULT_REQUEST_HEADERS')
        self.movie_id = 0
        self.cur_stills_requests = 1

        self.stills_lock = threading.Lock()

    def parse(self, response):
        print(response.url)
        bs_obj_comment = BeautifulSoup(response.body, "lxml")
        movie_short_comments_items = bs_obj_comment.find('div', class_="article").find('div', id='comments').find_all(
            'div',
            class_="comment-item")
        movie_short_pop_comments = []

        for item in movie_short_comments_items:
            pop_comments = {}
            movie_short_comment_comment = item.find('div', class_="comment")
            movie_short_comment_author_date = movie_short_comment_comment.h3.find('span',
                                                                                  class_="comment-info").get_text()
            movie_short_comment_author_date = movie_short_comment_author_date.replace(" ", "").replace("\n\n",
                                                                                                       "").split(
                "\n")
            movie_short_comment_author = movie_short_comment_author_date[1]
            movie_short_comment_date = movie_short_comment_author_date[-1]
            movie_short_comment_text = movie_short_comment_comment.p.get_text()
            movie_short_comment_text = movie_short_comment_text.replace(" ", "").replace("\n", "")
            pop_comments["author"] = movie_short_comment_author
            pop_comments["date"] = movie_short_comment_date
            pop_comments["text"] = movie_short_comment_text
            movie_short_pop_comments.append(pop_comments)

        print(movie_short_pop_comments)

        # still_url = "https://movie.douban.com/subject/10001432/photos?type=S"
        # movie_id = "10001432"
        # stills_link_item = StillsLinksItem(
        #     movie_id=None,
        #     movie_stills_photos_links=None,
        # )
        # stills_link_item['movie_id'] = movie_id
        # stills_link_item['movie_stills_photos_links'] = []
        # yield scrapy.Request(
        #     url=still_url,
        #     meta={'item': stills_link_item},
        #     callback=self.parse_stills,
        #     headers=self.headers
        # )

    def parse_stills(self, response):
        print('response Still_link %s' % response.url)
        stills_link_item = response.meta['item']
        if response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a'):
            next_url = response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a/@href').extract_first()
            print(next_url)
            self.headers['Referer'] = response.url
            try:
                request = scrapy.Request(
                    url=next_url,
                    meta={'item': stills_link_item},
                    callback=self.parse_stills,
                    headers=self.headers
                )
            except Exception as err:
                print(err)
            if not self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
                self.cur_stills_requests += 1
                yield request
            elif self.cur_stills_requests >= self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
                stills_link_item['movie_stills_photos_links'] = json.dumps(
                    stills_link_item['movie_stills_photos_links'])
                yield stills_link_item
            else:
                self.stills_lock.acquire()
                if self.cur_stills_requests < self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
                    self.cur_stills_requests += 1
                    self.stills_lock.release()
                    yield request
                else:
                    self.stills_lock.release()
                    stills_link_item['movie_stills_photos_links'] = json.dumps(
                        stills_link_item['movie_stills_photos_links'])
                    yield stills_link_item
                    # 否则，返回这一个页面的所有链接
        else:
            stills_link_item['movie_stills_photos_links'] = json.dumps(
                stills_link_item['movie_stills_photos_links'])
            yield stills_link_item


            # print("imdb_link %s" % response.url)
            # if response.xpath(
            #         '//div[@id="title-overview-widget"]/div[@class="vital"]/div[@class="title_block"]/div/div[@class="ratings_wrapper"]/div[@class="imdbRating"]/div[@class="ratingValue"]/strong/span'):
            #     movie_imdb_rating = response.xpath(
            #         '//div[@id="title-overview-widget"]/div[@class="vital"]/div[@class="title_block"]/div/div[@class="ratings_wrapper"]/div[@class="imdbRating"]/div[@class="ratingValue"]/strong/span/text()').extract_first()
            #     print("success")
            # else:
            #     movie_imdb_rating = ""
            #     print("nothing")
            # print(movie_imdb_rating)
            #     pass
            # print("----------------")
            # bs_obj_rating = BeautifulSoup(response.body, "lxml")
            # # print(bs_obj_rating)
            # print(bs_obj_rating.find('div', id='main_top').find('div', id='title-overview-widget'))
            # print(bs_obj_rating.find("#main_top"))
            # print(bs_obj_rating.find("#title-overview-widget"))
            # print(bs_obj_rating.find("#title-overview-widget > div.vital > div.title_block"))
            # movie_imdb_rating = bs_obj_rating.find(
            #     "#title-overview-widget > div.vital > div.title_block > div > div.ratings_wrapper > div.imdbRating > div.ratingValue > strong > span")
            # print(movie_imdb_rating)
            # if movie_imdb_rating != None:
            #     movie_imdb_rating = movie_imdb_rating.get_text()
            #     print(movie_imdb_rating)
            #     print('something')
            # else:
            #     movie_imdb_rating = ""
            #     print("nothing")

            # web_data =movie_IMs.get(response.url, headers=headers)
            # bs_obj = BeautifulSoup(web_data.text, "lxml")
            # movie_content = bs_obj.find('div', id='content')
            # movie_name = movie_content.h1.span.get_text()
            # movie_year = movie_content.find('span', class_='year').get_text()
            # movie_year = re.sub(r"[()]", "", movie_year)
            # movie_info = movie_content.find('div', id='info')
            # # self.driver.find_element_by_xpath(
            # #     '//div[@id="info"]/span[@class="actor"]/span[@class="attrs"]/a[@class="more-actor"]').click()
            # # time.sleep(1)
            # movie_info_items = movie_info.get_text().split('\n')
            # print(movie_info)
            # print(movie_info_items)
            # movie_directors = []
            # movie_screenwriters = []
            # movie_actors = []
            # movie_types = []
            # movie_languages = []
            # movie_release_dates = []
            # movie_runtime = []
            # movie_another_names = []
            # movie_IMDb_link = []
            # movie_imdb_rating = []
            # movie_premiere = []
            # movie_movie_numbers = []
            # # movie_screenwriters = []
            # # movie_screenwriters = []
            # # movie_screenwriters = []
            # # movie_screenwriters = []
            # # movie_screenwriters = []
            # for item in movie_info_items:
            #     print(item.split(':')[0])
            #     # print(item.split(':')[0])
            #     if item.split(':')[0] == "导演":
            #         movie_directors = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "编剧":
            #         movie_screenwriters = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "主演":
            #         movie_actors = item.split(':')[1].replace(' ', '').replace('更多...', '').split('/')
            #     if item.split(':')[0] == "类型":
            #         movie_types = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "官方网站":
            #         movie_official_website = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "制片国家/地区":
            #         movie_origin_place = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "语言":
            #         movie_languages = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "上映日期":
            #         movie_release_dates = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "片长":
            #         movie_runtime = item.split(':')[1].strip().replace('分钟', '')
            #         runtime = re.match("(\d{1,3})", movie_runtime)
            #         movie_runtime = runtime.group(1)
            #     if item.split(':')[0] == "又名":
            #         movie_another_names = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "IMDb链接":
            #         movie_IMDb_link = item.split(':')[1].replace(' ', '')
            #
            #     if item.split(':')[0] == "首播":
            #         movie_premiere = item.split(':')[1].replace(' ', '').split('/')
            #     # if item.split(':')[0] == "季数":
            #     #     movie_directors = item.split(':')[1].replace(' ', '').split('/')
            #     if item.split(':')[0] == "集数":
            #         movie_numbers = item.split(':')[1].replace(' ', '').split('/')
            # print(movie_directors)
            # print(movie_screenwriters)



            # print("------------------------------------------")
            # # items = []
            # item = DoubanMovieItem()
            # # item['movie_id'] = self.movie_id
            # item['movie_name'] = movie_name
            # item['movie_year'] = movie_year
            # item['movie_directors'] = movie_directors
            # item['movie_screenwriters'] = movie_screenwriters
            # item['movie_actors'] = movie_actors
            # item['movie_types'] = movie_types
            # item['movie_official_website'] = movie_official_website
            # item['movie_origin_place'] = movie_origin_place
            # item['movie_languages'] = movie_languages
            # item['movie_release_dates'] = movie_release_dates
            # item['movie_runtime'] = movie_runtime
            # item['movie_another_names'] = movie_another_names
            # item['movie_IMDb_link'] = movie_IMDb_link
            # # item['movie_douban_rating'] = movie_douban_rating
            # item['movie_imdb_rating'] = movie_imdb_rating
            # # items.append(item)
            # # print(items)
            # print(item)

    def parse_page1(self, response):
        item = DoubanPopMovieItem()
        item['pop_movie_url'] = response.url
        request = scrapy.Request("https://movie.douban.com/subject/1292722/photos?type=S",
                                 callback=self.parse_page2)
        request.meta['item'] = item
        print(item)
        print(request)
        return request

    def parse_page2(self, response):
        item = response.meta['item']
        item['pop_movie_other_url'] = response.url
        print(item)
        return item
