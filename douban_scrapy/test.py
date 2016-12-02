#encoding=utf-8

import json

import pymysql

db = pymysql.connect("localhost", "root", "root", "douban_movie", charset='utf8')
cursor = db.cursor()

sql = 'INSERT INTO test(json) VALUES (%s)'
sql2 = 'SELECT * FROM movie'

try:
    # cursor.execute(sql)
    cursor.execute(sql2)
    results = cursor.fetchall()
    # results = cursor.fetchone()
    # print(results[1])
    i = 0
    for row in results:
        id = row[1]
        i += 1
        print(i)
        print("id=%s" %id)

except Exception as e:
    print(e)

db.close()
