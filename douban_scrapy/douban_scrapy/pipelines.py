# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import sys
import logging
from .items import DoubanMovieItem, ImdbRatingItem, StillsLinksItem, ShortCommentsItem, PosterLinksItem, ReviewsItem
import json
import threading


class DoubanScrapyPipeline(object):
    def process_item(self, item, spider):
        # print("*******************************")
        # print(item)
        return item


class MySQLStorePipeline(object):
    def __init__(self, settings):
        self.username = settings.get('MYSQL_USERNAME')
        self.password = settings.get('MYSQL_PASSWORD')
        self.database = settings.get('MYSQL_DATABASE')
        self.host = settings.get('MYSQL_HOST')
        self.charset = settings.get('MYSQL_CHARSET')
        self.table_name_dict = settings.get('TABLE_NAME_DICT')

        self.still_link_item_count = 1
        self.short_comment_item_count = 1
        self.poster_link_item_count = 1
        self.review_item_count = 1

        self.douban_lock = threading.Lock()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings
        )

    def open_spider(self, spider):
        # 连接数据库
        try:
            self.connector = pymysql.connect(
                host=self.host,
                port=3306,
                user=self.username,
                passwd=self.password,
                db=self.database,
                charset=self.charset
            )
            self.cursor = self.connector.cursor()
            self.logger.info('Connecting to database successfully!')
        except Exception as err:
            print(err)
            sys.exit('Filed to connect database.')

        # 如果表不存在，则首先建表
        try:
            self.cursor.execute(
                """CREATE TABLE mirs_movie(
                      `id` INT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
                      `douban_id` VARCHAR(12) NOT NULL UNIQUE COMMENT '豆瓣电影ID',
                      `name` VARCHAR(600) COMMENT '电影名',
                      `douban_rating` CHAR(3) COMMENT '豆瓣评分',
                      `imdb_rating` CHAR(3) COMMENT 'IMDb评分',
                      `release_year` CHAR(4) COMMENT '电影发行年份',
                      `directors` VARCHAR(600) COMMENT '电影导演',
                      `screenwriters` VARCHAR(600) COMMENT '编剧',
                      `actors` VARCHAR(500) COMMENT '相关演员',
                      `types` VARCHAR(100) COMMENT '电影类型',
                      `official_website` VARCHAR(100) COMMENT '官网',
                      `origin_place` VARCHAR(30) COMMENT '国家',
                      `release_date` VARCHAR(600) COMMENT '上映时间',
                      `languages` VARCHAR(500) COMMENT '语言',
                      `runtime` VARCHAR(100) COMMENT '时长',
                      `another_names` VARCHAR(100) COMMENT '又名',
                      `imdb_link` VARCHAR(50) COMMENT 'IMDb的电影链接',
                      `cover_link` VARCHAR(150) COMMENT '电影封面链接',
                      `synopsis` TEXT COMMENT '剧情概要',
                      `stills_photos_links` JSON COMMENT '剧照照片集合页面链接',
                      `poster_photos_links` JSON COMMENT '海报照片集合页面链接',
                      `wallpaper_photos_links` JSON COMMENT '壁纸照片集合页面链接',
                      `awards` TEXT COMMENT '获奖',
                      `also_like_movies` VARCHAR(200) COMMENT '喜欢这部电影的人同样喜欢的电影',
                      `reviews` TEXT COMMENT '几个影评',
                      `short_pop_comments` TEXT COMMENT '几个热门短评',
                      PRIMARY KEY (id),
                      INDEX idx_id(id),
                      INDEX idx_douban_id(douban_id),
                      INDEX idx_name(name),
                      INDEX idx_douban_rating(douban_rating),
                      INDEX idx_imdb_rating(imdb_rating),
                      INDEX idx_year(release_year),
                      INDEX idx_directors(directors),
                      INDEX idx_screenwriters(screenwriters),
                      INDEX idx_actors(actors),
                      INDEX idx_types(types),
                      INDEX idx_origin_place(origin_place),
                      INDEX idx_languages(languages),
                      INDEX idx_runtime(runtime),
                      INDEX idx_another_names(another_names)
                    )ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '电影基本信息表';""".format(
                    self.table_name_dict['mirs_movie']
                )
            )
        except Exception as err:
            print(err)




    def close_spider(self, spider):
        self.cursor.close()
        self.connector.close()

    def process_item(self, item, spider):
        if isinstance(item, DoubanMovieItem):
            try:
                self.douban_lock.acquire()
                sql = 'INSERT IGNORE INTO mirs_movie(douban_id, name,douban_rating,release_year,directors,screenwriters,' \
                      'actors,types,official_website,origin_place,release_date,languages,runtime,another_names,' \
                      'imdb_link,cover_link,synopsis,awards,also_like_movies) VALUES (%s, %s, %s, %s, %s,%s, %s, %s,' \
                      ' %s, %s,%s, %s, %s,' \
                      '%s,%s, %s, %s, %s, %s)'
                data = (item['movie_id'], item['movie_name'], item['movie_douban_rating'], item['movie_year'],
                        item['movie_directors'], item['movie_screenwriters'], item['movie_actors'], item['movie_types'],
                        item['movie_official_website'], item['movie_origin_place'], item['movie_release_dates'],
                        item['movie_languages'],
                        item['movie_runtime'], item['movie_another_names'], item['movie_IMDb_link'],
                        item['movie_cover_link'], item['movie_synopsis'],
                        item['movie_awards'], item['movie_also_like_movies'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.douban_lock.release()
                self.logger.info(
                    'Write a DoubanMovieItem (movie_id: {0:s}) and (movie_name: {1:s})'.format(
                        item['movie_id'],
                        item['movie_name']
                    )
                )
                # print("DoubanMovieItem success")
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['mirs_movie_test']
                    )
                )
                print(err)
                self.connector.rollback()
        elif isinstance(item, ImdbRatingItem):
            try:
                # sql = 'INSERT INTO imdb_rating(douban_id, imdb_rating) VALUES (%s, %s)'
                sql = 'UPDATE mirs_movie SET imdb_rating = %s WHERE douban_id = %s'
                data = (item['movie_imdb_rating'], item['movie_id'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.logger.info(
                    'Write a ImdbRatingItem (movie_id: {0:s}) and (movie_imdb_rating: {1:s})'.format(
                        item['movie_id'],
                        item['movie_imdb_rating']
                    )
                )
                # print("imdb_rating success")
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['imdb_rating']
                    )
                )
                print(err)
                self.connector.rollback()
        elif isinstance(item, StillsLinksItem):
            try:
                # sql = 'INSERT INTO stills_links(douban_id, stills_photos_links) VALUES (%s, %s)'
                sql = 'UPDATE mirs_movie SET stills_photos_links = %s WHERE douban_id = %s'
                data = (item['movie_stills_photos_links'], item['movie_id'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.logger.info(
                    'Write a StillsLinksItem (movie_id: {0:s}) and movie_stills_photos_links)sep:{1:d}'.format(
                        item['movie_id'],
                        self.still_link_item_count
                    )
                )
                # print("stills_links success")
                self.still_link_item_count += 1
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['stills_links']
                    )
                )
                print(err)
                self.connector.rollback()
        elif isinstance(item, PosterLinksItem):
            try:
                # sql = 'INSERT INTO poster_links(douban_id, poster_photos_links) VALUES (%s, %s)'
                sql = 'UPDATE mirs_movie SET poster_photos_links = %s WHERE douban_id = %s'
                # data = (item['movie_id'], item['movie_poster_photos_links'])
                data = (item['movie_poster_photos_links'], item['movie_id'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.logger.info(
                    'Write a PosterLinksItem (movie_id: {0:s}) and movie_poster_photos_links)sep:{1:d}'.format(
                        item['movie_id'],
                        self.poster_link_item_count
                    )
                )
                # print("stills_links success")
                self.poster_link_item_count += 1
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['poster_links']
                    )
                )
                print(err)
                self.connector.rollback()
        elif isinstance(item, ShortCommentsItem):
            try:
                # sql = """INSERT INTO short_comments(douban_id, comment_list) VALUES (%s, %s)"""
                sql = """UPDATE mirs_movie SET short_pop_comments = %s WHERE douban_id = %s"""
                comment_list = str(item['comment_list']).replace("'", '"')
                # data = (item['movie_id'], comment_list)
                data = (comment_list, item['movie_id'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.logger.info(
                    'Write a ShortCommentsItem (movie_id: {0:s}) and comment_list)sep:{1:d}'.format(
                        item['movie_id'],
                        self.short_comment_item_count
                    )
                )
                self.short_comment_item_count += 1
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['short_comments']
                    )
                )
                print(err)
                self.connector.rollback()
        elif isinstance(item, ReviewsItem):
            try:
                # sql = """INSERT INTO reviews(douban_id, review_list) VALUES (%s, %s)"""
                sql = """UPDATE mirs_movie SET reviews = %s WHERE douban_id = %s"""
                review_list = str(item['review_list']).replace("'", '"')
                # data = (item['movie_id'], review_list)
                data = (review_list, item['movie_id'])
                self.cursor.execute(sql, data)
                self.connector.commit()
                self.logger.info(
                    'Write a ReviewsItem (movie_id: {0:s}) and review_list)sep:{1:d}'.format(
                        item['movie_id'],
                        self.review_item_count
                    )
                )
                self.review_item_count += 1
            except Exception as err:
                self.logger.error(
                    'Failed to insert data into table {0:s}'.format(
                        self.table_name_dict['reviews']
                    )
                )
                print(err)
                self.connector.rollback()
        return item
