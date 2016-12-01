# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["imdb.com"]
    start_urls = [
        "https://movie.douban.com/subject/26683290/comments?start=0&limit=20&sort=new_score",
    ]

    # allowed_domains = ["movie.douban.com/"]
    # start_urls = [
    # 	"https://movie.douban.com/",
    # ]



    def parse(self, response):
        print("----------------")
        bs_obj_comment = BeautifulSoup(response.body, "lxml")
        # movie_content = []
        # movie_short_comments_mod = movie_content.find('div', class_="article").find('div', id="comments-section").find(
        #     'div', class_="mod-hd")
        # # movie_short_comments_link = movie_short_comments_mod.h2.span.a.get('href')
        # movie_short_comments_mod = movie_short_comments_mod.find_next_sibling("div")
        # movie_short_comments_items = movie_short_comments_mod.find('div', class_="tab-bd")
        # if movie_short_comments_items is None:
        #     movie_short_pop_comments = []
        # else:



        movie_short_comments_items = bs_obj_comment.find('div', class_="article").find('div', id='comments').find_all('div',
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




        # movie_imdb_rating = bs_obj_rating.find(
        #     "#title-overview-widget > div.vital > div.title_block > div > div.ratings_wrapper > div.imdbRating > div.ratingValue > strong > span")
        # if movie_imdb_rating != None:
        #     movie_imdb_rating = movie_imdb_rating.get_text()
        #     print(movie_imdb_rating)
        #     print('something')
        # else:
        #     movie_imdb_rating = ""
        #     print("nothing")
