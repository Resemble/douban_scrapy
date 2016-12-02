#encoding=utf-8

import json

import pymysql

db = pymysql.connect("localhost", "root", "root", "douban_movie", charset='utf8')
cursor = db.cursor()

sql = 'UPDATE mirs_movie SET imdb_rating = %s WHERE id = 1'
sql2 = 'UPDATE mirs_movie SET imdb_rating = %s WHERE douban_id = %s'
sql3 = 'SELECT * FROM mirs_movie'
data = ("2", "11")
data2 = ("2")
movie_id = 3
try:
    cursor.execute(sql, data2)
    print("**************")
    cursor.execute(sql2, data)
    # cursor.execute(sql3)
    # results = cursor.fetchall()
    # results = cursor.fetchone()
    # print(results[1])
    # i = 0
    # for row in results:
    #     id = row[1]
    #     i += 1
    #     print(i)
    #     print("id=%s" %id)
    db.commit()

except Exception as e:
    print(e)

db.close()
