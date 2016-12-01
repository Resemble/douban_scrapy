# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanMovieItem(scrapy.Item):
    #    movie_screenwriter 编剧
    #    movie_origin_place 制片国家/地区
    #    movie_runtime	片长
    #    movie_another_name 又名
    #    movie_synopsis 	剧情简介
    #    movie_offical_website 官方网站
    #    movie_IMD_link     IMD链接
    #    movie_awards 获奖
    #    movie_all_awards_link 全部获奖页面
    #    movie_also_like_movies 喜欢这部电影同样喜欢的电影
    #    movie_questions 关于这部电影的问题
    #    movie_all_questions_link    关于这部电影所有问题的页面链接
    #    movie_reviews_link  所有影评页面链接
    #    movie_reviews   几个影评
    #    movie_short_comments_link   所有短评页面链接
    #    movie_short_pop_comments    几个热门短评

    movie_id = scrapy.Field()
    movie_name = scrapy.Field()
    movie_year = scrapy.Field()
    movie_directors = scrapy.Field()
    movie_screenwriters = scrapy.Field()
    movie_actors = scrapy.Field()
    movie_types = scrapy.Field()
    movie_official_website = scrapy.Field()
    movie_origin_place = scrapy.Field()
    movie_languages = scrapy.Field()
    movie_release_dates = scrapy.Field()
    movie_runtime = scrapy.Field()
    movie_another_names = scrapy.Field()
    movie_IMDb_link = scrapy.Field()
    movie_cover_link = scrapy.Field()
    movie_synopsis = scrapy.Field()
    movie_awards = scrapy.Field()
    movie_all_awards_link = scrapy.Field()
    movie_also_like_movies = scrapy.Field()
    movie_reviews = scrapy.Field()
    movie_reviews_link = scrapy.Field()
    movie_short_pop_comments = scrapy.Field()
    movie_short_comments_link = scrapy.Field()
    movie_douban_rating = scrapy.Field()
    movie_imdb_rating = scrapy.Field()
    movie_stills_photos_links = scrapy.Field()
    movie_poster_photos_links = scrapy.Field()
    movie_wallpaper_photos_links = scrapy.Field()
    movie_premiere = scrapy.Field()
    movie_numbers = scrapy.Field()


class ImdbRatingItem(scrapy.Item):
    movie_id = scrapy.Field()
    movie_imdb_rating = scrapy.Field()
    movie_imdb_link = scrapy.Field()


class StillsLinksItem(scrapy.Item):
    movie_id = scrapy.Field()
    movie_stills_photos_links = scrapy.Field()

class PosterLinksItem(scrapy.Item):
    movie_id = scrapy.Field()
    movie_poster_photos_links = scrapy.Field()

class ShortCommentsItem(scrapy.Item):
    movie_id = scrapy.Field()
    comment_list = scrapy.Field()

class ReviewsItem(scrapy.Item):
    movie_id = scrapy.Field()
    review_list = scrapy.Field()



# 依次是剧照、海报、壁纸 第一个是页面的链接 第二个是照片的集合
class DoubanMoviePhotoItem(scrapy.Item):
    movie_id = scrapy.Field()
    movie_stills_link = scrapy.Field()
    movie_stills_photos_links = scrapy.Field()
    movie_poster_link = scrapy.Field()
    movie_poster_photos_links = scrapy.Field()
    movie_wallpaper_link = scrapy.Field()
    movie_wallpaper_photos_links = scrapy.Field()
