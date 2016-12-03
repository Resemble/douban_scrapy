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


class DoubanMovieSpider(scrapy.Spider):
    name = "douban_movie"
    allowed_domains = ["movie.douban.com", "imdb.com"]
    try:
        connector = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db='douban_movie',
            charset='UTF8'
        )
        cursor = connector.cursor()
    except Exception as err:
        print(err)
        sys.exit('Filed to connect database.2')

    # movie_id = 0

    def __init__(self, *a, **kwargs):
        super().__init__(*a, **kwargs)
        DEFAULT_REQUEST_HEADERS['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        self.headers = DEFAULT_REQUEST_HEADERS
        # self.headers = self.settings.get('DEFAULT_REQUEST_HEADERS')
        self.movie_id = 0
        self.cur_stills_requests = 0
        self.cur_poster_requests = 0
        self.cur_comment_requests = 0
        self.cur_review_requests = 0

        self.stills_lock = threading.Lock()
        self.poster_lock = threading.Lock()
        self.comment_lock = threading.Lock()
        self.review_lock = threading.Lock()

    def start_requests(self):
        self.logger.info('start...')
        sql = "SELECT * FROM movie"
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                self.movie_id = row[1]
                movie_url = 'https://movie.douban.com/subject/' + str(self.movie_id)
                yield scrapy.Request(url=movie_url)
        except Exception as err:
            print(err)

    def parse(self, response):
        # print(response.url)
        global movie_directors, movie_screenwriters, movie_actors, movie_types, movie_official_website, movie_IMDb_link
        global movie_origin_place, movie_release_dates, movie_languages, movie_runtime, movie_another_names
        global movie_award
        movie_id = str(response.url.split('/')[4])
        print(movie_id)
        bs_obj = BeautifulSoup(response.body, "lxml")
        movie_content = bs_obj.find('div', id='content')
        movie_name = movie_content.h1.span.get_text()
        movie_year = movie_content.find('span', class_='year').get_text()
        movie_year = re.sub(r"[()]", "", movie_year)
        movie_year = re.match(r'\d{4}', movie_year).group(0)
        movie_info = movie_content.find('div', id='info')
        movie_info_items = movie_info.get_text().split('\n')
        movie_directors = ""
        movie_screenwriters = ""
        movie_actors = ""
        movie_types = ""
        movie_official_website = ""
        movie_origin_place = ""
        movie_release_dates = ""
        movie_languages = ""
        movie_runtime = ""
        movie_another_names = ""
        movie_IMDb_link = ""
        movie_award = ""
        for item in movie_info_items:
            # print(item.split(':')[0])
            if item.split(':')[0] == "导演":
                movie_directors = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "编剧":
                movie_screenwriters = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "主演":
                movie_actors = item.split(':')[1].replace(' ', '').replace('更多...', '').split('/')
            if item.split(':')[0] == "类型":
                movie_types = item.split(':')[1].replace(' ', '').split('/')
            # if item.split(':')[0] == "官方网站":
            #     movie_official_website = item.split(':')[1].replace(' ', '')
            if re.match('官方网站', item):
                movie_official_website = item.replace("官方网站:", "")
            if item.split(':')[0] == "制片国家/地区":
                movie_origin_place = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "语言":
                movie_languages = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "上映日期":
                movie_release_dates = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "片长":
                movie_runtime = item.split(':')[1].strip().replace('分钟', '')
                runtime = re.match("(\d{1,3})", movie_runtime)
                movie_runtime = runtime.group(1)
            if item.split(':')[0] == "又名":
                movie_another_names = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "IMDb链接":
                movie_IMDb_link = item.split(':')[1].replace(' ', '')
                movie_IMDb_link = "http://www.imdb.com/title/" + str(movie_IMDb_link)
                # print(movie_IMDb_link)
                imdb_rating_item = ImdbRatingItem(
                    movie_id=None,
                    movie_imdb_rating=None,
                )
                imdb_rating_item['movie_id'] = movie_id
                try:
                    # imd 评分
                    yield scrapy.Request(
                        url=movie_IMDb_link,
                        meta={'item': imdb_rating_item},
                        callback=self.parse_imdb
                    )
                except Exception as err:
                    print(err)
            if item.split(':')[0] == "首播":
                movie_premiere = item.split(':')[1].replace(' ', '').split('/')
            if item.split(':')[0] == "集数":
                movie_numbers = item.split(':')[1].replace(' ', '').split('/')
        # 简介
        movie_synopsis = movie_content.find('div', id="link-report")
        if movie_synopsis is not None:
            movie_synopsis = movie_synopsis.span.get_text().replace('\n', '').replace(
                '\u3000\u3000',
                '').strip()
        else:
            movie_synopsis = ""
        # 获奖 电视剧的需要改
        movie_awards_mod = movie_content.find('div', class_="article").find('div', class_="mod")
        if movie_awards_mod is None:
            movie_awards = []
        else:
            # movie_all_awards_link = movie_awards_mod.find('div', class_="hd").h2.span.a.get('href')
            movie_awards_uls = movie_awards_mod.find_all('ul', class_="award")
            movie_awards = []
            for ul in movie_awards_uls:
                awards = {}
                movie_award = ul.get_text()
                movie_award = movie_award.split("\n")
                award_name = movie_award[2]
                award_name_specific = movie_award[4]
                award_owner = movie_award[5]
                awards["award_name"] = award_name
                awards["award_name_specific"] = award_name_specific
                awards["award_owner"] = award_owner
                movie_awards.append(awards)
            temp_award = []
            for i in movie_award:
                if i != '':
                    # print(i)
                    temp_award.append(i)
            movie_award = temp_award
        # 喜欢这部电影也喜欢的电影
        if movie_content.find('div', class_="article").find('div', id="recommendations"):

            movie_recommendation_bd_dls = movie_content.find('div', class_="article").find('div',
                                                                                           id="recommendations").find(
                'div', class_="recommendations-bd").find_all('dl')
            # movie_also_like_movies 第一个是喜欢这部电影并喜欢的电影的页面链接，第二个是一张图片链接，第三个是电影名字
            movie_also_like_movies = []
            for dl in movie_recommendation_bd_dls:
                dl_a = dl.dt.a
                movie_href = dl_a.get('href')
                movie_href = movie_href.split("/")
                movie_like_id = movie_href[4]
                movie_also_like_movies.append(movie_like_id)
        else:
            movie_also_like_movies = []

        # 豆瓣评分
        movie_douban_rating = movie_content.find('div', class_="article").find('div', id="interest_sectl").find('div',
                                                                                                                class_="rating_wrap clearbox").find(
            'div', class_="rating_self clearfix").find('strong', class_="ll rating_num").get_text()
        # print(movie_douban_rating)
        movie_cover_link = movie_content.find("div", class_="grid-16-8 clearfix").find("div", class_="article").find(
            "div", class_="indent clearfix").find("div", class_="subjectwrap clearfix").find("div",
                                                                                             class_="subject clearfix").find(
            "div", id="mainpic").a.img.get('src')

        # 爬照片
        # 剧照
        self.headers['Referer'] = 'https://movie.douban.com/subject/' + movie_id + '/all_photos'
        still_url = "https://movie.douban.com/subject/" + str(
            movie_id) + "/photos?type=S"
        stills_link_item = StillsLinksItem(
            movie_id=None,
            movie_stills_photos_links=None,
        )
        stills_link_item['movie_id'] = movie_id
        stills_link_item['movie_stills_photos_links'] = []
        self.headers['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        yield scrapy.Request(
            url=still_url,
            meta={'item': stills_link_item},
            callback=self.parse_stills,
            headers=self.headers
        )
        # 海报
        self.headers['Referer'] = 'https://movie.douban.com/subject/' + movie_id + '/all_photos'
        poster_url = "https://movie.douban.com/subject/" + str(
            movie_id) + "/photos?type=R"
        self.headers['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        poster_link_item = PosterLinksItem(
            movie_id=None,
            movie_poster_photos_links=None,
        )
        poster_link_item['movie_id'] = movie_id
        poster_link_item['movie_poster_photos_links'] = []
        self.headers['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        yield scrapy.Request(
            url=poster_url,
            meta={'item': poster_link_item},
            callback=self.parse_poster,
            headers=self.headers
        )

        # 短评
        self.headers['Referer'] = 'https://movie.douban.com/subject/' + movie_id
        comment_url = "https://movie.douban.com/subject/" + str(movie_id) + "/comments"
        short_comment_item = ShortCommentsItem(
            movie_id=None,
            comment_list=None
        )
        short_comment_item['movie_id'] = movie_id
        short_comment_item['comment_list'] = []
        self.headers['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        yield scrapy.Request(
            url=comment_url,
            meta={'item': short_comment_item},
            callback=self.parse_comment,
            headers=self.headers
        )
        # 影评
        self.headers['Referer'] = 'https://movie.douban.com/subject/' + movie_id
        review_url = "https://movie.douban.com/subject/" + str(movie_id) + "/reviews"
        review_item = ReviewsItem(
            movie_id=None,
            review_list=None
        )
        review_item['movie_id'] = movie_id
        review_item['review_list'] = []
        self.headers['Cookie'] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))
        yield scrapy.Request(
            url=review_url,
            meta={'item': review_item},
            callback=self.parse_review,
            headers=self.headers
        )
        item = DoubanMovieItem()
        item['movie_id'] = movie_id
        item['movie_name'] = str(movie_name)
        item['movie_douban_rating'] = str(movie_douban_rating)
        item['movie_year'] = str(movie_year)
        item['movie_directors'] = str(movie_directors)
        item['movie_screenwriters'] = str(movie_screenwriters)
        item['movie_actors'] = str(movie_actors)
        item['movie_types'] = str(movie_types)
        item['movie_official_website'] = str(movie_official_website)
        item['movie_origin_place'] = str(movie_origin_place)
        item['movie_release_dates'] = str(movie_release_dates)
        item['movie_languages'] = str(movie_languages)
        item['movie_runtime'] = str(movie_runtime)
        item['movie_another_names'] = str(movie_another_names)
        item['movie_IMDb_link'] = str(movie_IMDb_link)
        item['movie_cover_link'] = str(movie_cover_link)
        item['movie_synopsis'] = str(movie_synopsis)
        item['movie_awards'] = str(movie_award)
        item['movie_also_like_movies'] = str(movie_also_like_movies)
        # print(item)
        yield item

    def parse_imdb(self, response):
        # print('response IMDB_link %s' % response.url)
        imdb_rating_item = response.meta['item']
        if response.xpath(
                '//div[@id="title-overview-widget"]/div[@class="vital"]/div[@class="title_block"]/div/div[@class="ratings_wrapper"]/div[@class="imdbRating"]/div[@class="ratingValue"]/strong/span'):
            movie_imdb_rating = response.xpath(
                '//div[@id="title-overview-widget"]/div[@class="vital"]/div[@class="title_block"]/div/div[@class="ratings_wrapper"]/div[@class="imdbRating"]/div[@class="ratingValue"]/strong/span/text()').extract_first()
        else:
            movie_imdb_rating = ""
        imdb_rating_item['movie_imdb_rating'] = movie_imdb_rating
        yield imdb_rating_item

    def parse_stills(self, response):
        # print('response Still_link %s' % response.url)
        stills_link_item = response.meta['item']
        bs_obj = BeautifulSoup(response.body, "lxml")
        movie_ul = bs_obj.find('div', id='content').find('div', class_='article').find('ul',
                                                                                       class_='poster-col4 clearfix')
        movie_lis = movie_ul.find_all('li')
        for movie_li in movie_lis:
            li = has_attr_dataid(movie_li)
            if li:
                link_id = movie_li.get('data-id')
                link = "https://img1.doubanio.com/view/photo/thumb/public/p" + link_id + ".jpg"
                stills_link_item['movie_stills_photos_links'].append(link)

        if response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a'):
            next_url = response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a/@href').extract_first()
            self.headers['Referer'] = response.url
            request = scrapy.Request(
                url=next_url,
                meta={'item': stills_link_item},
                callback=self.parse_stills,
                headers=self.headers
            )
            if not self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
                yield request
            elif self.cur_stills_requests > self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
                stills_link_item['movie_stills_photos_links'] = json.dumps(
                    stills_link_item['movie_stills_photos_links'])
                yield stills_link_item
            else:
                self.stills_lock.acquire()
                if self.cur_stills_requests <= self.settings.get('MAX_STILLS_PAGES_PER_MOVIE'):
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

    def parse_poster(self, response):
        # print('response Poter_link %s' % response.url)
        poster_link_item = response.meta['item']
        bs_obj = BeautifulSoup(response.body, "lxml")
        movie_ul = bs_obj.find('div', id='content').find('div', class_='article').find('ul',
                                                                                       class_='poster-col4 clearfix')
        movie_lis = movie_ul.find_all('li')
        for movie_li in movie_lis:
            li = has_attr_dataid(movie_li)
            if li:
                link_id = movie_li.get('data-id')
                link = "https://img1.doubanio.com/view/photo/thumb/public/p" + link_id + ".jpg"
                poster_link_item['movie_poster_photos_links'].append(link)

        if response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a'):
            next_url = response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a/@href').extract_first()
            self.headers['Referer'] = response.url
            request = scrapy.Request(
                url=next_url,
                meta={'item': poster_link_item},
                callback=self.parse_poster,
                headers=self.headers
            )
            if not self.settings.get('MAX_POSTER_PAGES_PER_MOVIE'):
                yield request
            elif self.cur_poster_requests > self.settings.get('MAX_POSTER_PAGES_PER_MOVIE'):
                poster_link_item['movie_poster_photos_links'] = json.dumps(
                    poster_link_item['movie_poster_photos_links'])
                yield poster_link_item
            else:
                self.poster_lock.acquire()
                if self.cur_poster_requests <= self.settings.get('MAX_POSTER_PAGES_PER_MOVIE'):
                    self.cur_poster_requests += 1
                    self.poster_lock.release()
                    yield request
                else:
                    self.poster_lock.release()
                    poster_link_item['movie_poster_photos_links'] = json.dumps(
                        poster_link_item['movie_poster_photos_links'])
                    yield poster_link_item
        # 否则，返回这一个页面的所有链接
        else:
            poster_link_item['movie_poster_photos_links'] = json.dumps(
                poster_link_item['movie_poster_photos_links'])
            yield poster_link_item

    def parse_comment(self, response):
        # print('response Comment_link %s' % response.url)
        short_comment_item = response.meta['item']
        bs_obj_comment = BeautifulSoup(response.body, "lxml")
        movie_short_comments_items = bs_obj_comment.find('div', class_="article").find('div', id='comments').find_all(
            'div', class_="comment-item")

        for item in movie_short_comments_items:
            movie_short_comment_comment = item.find('div', class_="comment")
            if movie_short_comment_comment is not None:
                movie_short_comment_author_date = movie_short_comment_comment.h3.find('span',
                                                                                      class_="comment-info").get_text()
                movie_short_comment_author_date = movie_short_comment_author_date.replace(" ", "").replace("\n\n",
                                                                                                           "").split(
                    "\n")
                # print(movie_short_comment_author_date)
                author_date_len = len(movie_short_comment_author_date)
                if author_date_len == 2:
                    date = re.search(r'\d{4}-\d{2}-\d{2}', movie_short_comment_author_date[1])
                    movie_short_comment_date = date.group(0)
                    movie_short_comment_author = movie_short_comment_author_date[1].replace(date.group(0), "")
                else:
                    movie_short_comment_author = movie_short_comment_author_date[1]
                    movie_short_comment_date = movie_short_comment_author_date[-1]
                movie_short_comment_text = movie_short_comment_comment.p.get_text()
                movie_short_comment_text = movie_short_comment_text.replace(" ", "").replace("\n", "")

                short_comment_item['comment_list'].append({
                    'comment_author': movie_short_comment_author,
                    'comment_text': movie_short_comment_text,
                    'comment_date': movie_short_comment_date
                })

        if response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@id="comments"]/div[@id="paginator"]/a[@class="next"]'):
            next_url = response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@id="comments"]/div[@id="paginator"]/a[@class="next"]/@href').extract_first()
            next_url = "https://movie.douban.com/subject/" + short_comment_item['movie_id'] + "/comments" + next_url
            # print(next_url)
            self.headers['Referer'] = response.url
            request = scrapy.Request(
                url=next_url,
                meta={'item': short_comment_item},
                callback=self.parse_comment,
                headers=self.headers
            )
            if not self.settings.get('MAX_COMMENT_PAGES_PER_MOVIE'):
                yield request
            elif self.cur_comment_requests > self.settings.get('MAX_COMMENT_PAGES_PER_MOVIE'):
                yield short_comment_item
            else:
                self.comment_lock.acquire()
                if self.cur_comment_requests <= self.settings.get('MAX_COMMENT_PAGES_PER_MOVIE'):
                    self.cur_comment_requests += 1
                    self.comment_lock.release()
                    yield request
                else:
                    self.comment_lock.release()
                    yield short_comment_item
        # 否则，返回这一个页面的所有链接
        else:
            yield short_comment_item

    def parse_review(self, response):
        # print('response review_link %s' % response.url)
        review_item = response.meta['item']

        if response.xpath(
                '///div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="review-list"]/div[@typeof="v:Review"]'):
            movie_reviews_items = response.xpath(
                '///div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="review-list"]')

            for item in movie_reviews_items.xpath('div[@typeof="v:Review"]'):
                review_content = item.xpath('div[@class="main review-item"]/div[@class="middle"]')
                movie_review_title = review_content.xpath(
                    'header[@class="main-hd"]/h3[@class="title"]/a/text()').extract_first()
                movie_review_header_more = review_content.xpath('header[@class="main-hd"]/div[@class="header-more"]')
                movie_review_author = movie_review_header_more.xpath('a[@class="author"]/span/text()').extract_first()
                movie_review_date = movie_review_header_more.xpath('span[@class="main-meta"]/text()').extract_first()
                movie_review_rating = movie_review_header_more.xpath(
                    'span[@property="v:rating"]/@title').extract_first()
                movie_review_text = review_content.xpath(
                    'div[@class="main-bd"]/div[@class="review-short"]/div[@class="short-content"]/text()').extract_first()

                movie_review_text = movie_review_text.replace(" ", "").replace("\n", "")

                review_item['review_list'].append({
                    'review_title': movie_review_title,
                    'review_author': movie_review_author,
                    'review_date': movie_review_date,
                    'review_rating': movie_review_rating,
                    'review_text': movie_review_text,
                })
                # print(review_item)

        if response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a'):
            next_url = response.xpath(
                '//div[@id="wrapper"]/div[@id="content"]/div[@class="grid-16-8 clearfix"]/div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a/@href').extract_first()
            next_url = "https://movie.douban.com/subject/" + review_item['movie_id'] + "/reviews" + next_url
            # print(next_url)
            self.headers['Referer'] = response.url
            request = scrapy.Request(
                url=next_url,
                meta={'item': review_item},
                callback=self.parse_review,
                headers=self.headers
            )
            if not self.settings.get('MAX_REVIEW_PAGES_PER_MOVIE'):
                yield request
            elif self.cur_review_requests > self.settings.get('MAX_REVIEW_PAGES_PER_MOVIE'):
                yield review_item
            else:
                self.review_lock.acquire()
                if self.cur_review_requests <= self.settings.get('MAX_REVIEW_PAGES_PER_MOVIE'):
                    self.cur_review_requests += 1
                    self.review_lock.release()
                    yield request
                else:
                    self.review_lock.release()
                    yield review_item
        # 否则，返回这一个页面的所有链接
        else:
            yield review_item


# 获取有属性是data-id的tag
def has_attr_dataid(tag):
    return tag.has_attr('data-id')
