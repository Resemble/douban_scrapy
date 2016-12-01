# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pymysql

db = pymysql.connect("localhost", "root", "ran13458555648", "ippool")

cursor = db.cursor()

with open('ip.txt', 'r') as f:
    for line in f.readlines():
        ip_list = line.split(',')
        ip_port, ip_type = ip_list[0], ip_list[1]
        amousy = ip_list[2]
        speed = ip_list[6]
        print("amousy: %s" % amousy)
        if amousy != '高匿': continue
        ip_type = 'HTTP' if ip_type == 'HTTP/HTTPS' else ip_type
        ip, port = ip_port.split(':')
        if ip_type.startswith('HTTP'):
            print(ip, port, ip_type)
            sql = "insert ignore into proxy(ip, port, type, speed) values ('%s', '%s', '%s', '%s')" % (
            ip, port, ip_type, speed)
            print(sql)
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()

    db.close()
