#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql


def main():

    db = pymysql.connect(host='127.0.0.1',
                         user='lycheetest',
                         passwd='lycheetest',
                         db='lycheetest',
                         charset='utf8mb4',
                         unix_socket='/var/run/mysqld/mysqld.sock',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("set names utf8;")

if __name__ == '__main__':
    main()
