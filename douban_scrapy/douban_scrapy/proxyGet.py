import pymysql

db = pymysql.connect("localhost", "root", "root", "ippool")

cursor = db.cursor()


def get_proxy():
    sql = "SELECT IP,PORT,TYPE FROM proxy WHERE ID >= (((SELECT  MAX(ID) FROM proxy) - (SELECT  MIN(ID) FROM proxy)) * rand() + (SELECT  MIN(ID) FROM proxy)) LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)
    return result[0][2] + "://" + result[0][0] + ":" + result[0][1]
