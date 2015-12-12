# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import os
import glob
import shutil
import subprocess
import pymysql
from lycheesync.utils.configuration import ConfBorg
# from datetime import datetime
import pymysql.cursors

logger = logging.getLogger(__name__)


class TestUtils:

    def __init__(self):
        self.db = None
        self.cb = ConfBorg()

    @property
    def conf(self):
        return self.cb.conf

    def _connect_db(self):
        self.db = pymysql.connect(host=self.cb.conf['dbHost'],
                                  user=self.cb.conf['dbUser'],
                                  passwd=self.cb.conf['dbPassword'],
                                  db=self.cb.conf['db'],
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)

    def _exec_sql(self, sql):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql)

            self.db.commit()

        except Exception as e:
            raise e

    def make_fake_lychee_fs(self, path):

        if not(os.path.isdir(os.path.join(path, 'uploads', 'big'))):
            uploads = os.path.join(path, 'uploads')
            path = []
            path.append(uploads)
            path.append(os.path.join(uploads, 'big'))
            path.append(os.path.join(uploads, 'thumb'))
            path.append(os.path.join(uploads, 'medium'))
            for p in path:
                if not(os.path.isdir(p)):
                    os.mkdir(p)

    def drop_db(self):
        # connect to db
        self.db = pymysql.connect(host=self.cb.conf['dbHost'],
                                  user=self.cb.conf['dbUser'],
                                  passwd=self.cb.conf['dbPassword'],
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)
        # check if db exists
        try:
            sql = "DROP DATABASE " + self.cb.conf['db']
            with self.db.cursor() as cursor:
                cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            logger.exception(e)
        finally:
            self.db.close()

    def table_exists(self, table_name):
        res = False
        self._connect_db()
        try:
            sql = "show tables where Tables_in_lychee='lychee_albums';"
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                res = (len(cursor.fetchall()) == 1)
        except Exception as e:
            raise e
        finally:
            self.db.close()
            return res

    def make_fake_lychee_db(self):

        # connect to db
        self.db = pymysql.connect(host=self.cb.conf['dbHost'],
                                  user=self.cb.conf['dbUser'],
                                  passwd=self.cb.conf['dbPassword'],
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)
        # check if db exists
        try:
            sql = "CREATE DATABASE IF NOT EXISTS " + self.cb.conf['db']
            with self.db.cursor() as cursor:
                cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            logger.exception(e)
        finally:
            self.db.close()

        self._connect_db()

        try:
            # check if table exists
            sql = "show tables where Tables_in_lychee='lychee_albums';"
            with self.db.cursor() as cursor:
                cursor.execute(sql)

                if (len(cursor.fetchall()) == 0):
                    cmd = 'mysql -h {} -u {} -p{} {} < ./ressources/lychee.sql'.format(
                        self.cb.conf['dbHost'],
                        self.cb.conf['dbUser'],
                        self.cb.conf['dbPassword'],
                        self.cb.conf['db'])
                    logger.info(cmd)
                    retval = -1
                    retval = subprocess.call(cmd, shell=True)
                    assert retval == 0

            # create tables
        except Exception as e:
            logger.exception(e)
        finally:
            self.db.close()

    def load_photoset(self, setname):
        testlibpath = self.cb.conf['testlib']
        testalbum = os.path.join(testlibpath, setname)
        dest = os.path.join(self.cb.conf['testphotopath'], setname)
        shutil.copytree(testalbum, dest, copy_function=shutil.copy)

    def clean_db(self):
        logger.info("Clean Database")
        # connect to db
        self._connect_db()
        try:
            self._exec_sql("TRUNCATE TABLE lychee_albums;")
            self._exec_sql("TRUNCATE TABLE lychee_photos;")
        except Exception as e:
            logger.exception(e)
        finally:
            self.db.close()

    def _empty_or_create_dir(self, path):
        try:
            if os.path.isdir(path):
                path = os.path.join(path, '*')
                for f in glob.glob(path):

                    if os.path.exists(f):

                        if os.path.isfile(f):
                            if not f.endswith("html"):
                                os.remove(f)
                        elif os.path.isdir(f):
                            shutil.rmtree(f)

            else:
                logger.info(path + ' not a dir, create it')
                os.mkdir(path)
        except Exception as e:
            logger.exception(e)

    def clean_fs(self):

        logger.info("Clean Filesystem")
        lycheepath = self.cb.conf['lycheepath']
        # empty tmp directory
        tmpdir = self.cb.conf['testphotopath']
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)

        os.mkdir(tmpdir)

        # empty images
        big = os.path.join(lycheepath, "uploads", "big")
        med = os.path.join(lycheepath, "uploads", "medium")
        thumb = os.path.join(lycheepath, "uploads", "thumb")

        # empty images
        self._empty_or_create_dir(big)
        self._empty_or_create_dir(med)
        self._empty_or_create_dir(thumb)

    def delete_dir_content(self, dir):
        self._empty_or_create_dir(dir)

    def count_db_photos(self):
        res = -1
        self._connect_db()
        try:
            sql = "select count(1) as total from lychee_photos"
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                count = cursor.fetchone()
                res = count['total']
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            self.db.close()
            return res

    def count_db_albums(self):
        res = -1
        self._connect_db()
        try:
            sql = "select count(1) as total from lychee_albums"
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                count = cursor.fetchone()
                res = count['total']
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            self.db.close()
            return res

    def get_album_creation_date(self, a_name):
        res = -1
        self._connect_db()
        try:
            sql = "select sysstamp from lychee_albums where title='{}'".format(a_name)
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchone()
                sysstamp = data['sysstamp']
                # res = datetime.fromtimestamp(sysstamp)
                res = sysstamp
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            self.db.close()
            return res

    def _count_files_in_dir(self, path):
        res = -1
        try:
            res = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
            # don't count index.html
            path = os.path.join(path, 'index.html')
            if os.path.isfile(path):
                res = res - 1
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            return res

    def count_fs_photos(self):
        path = os.path.join(self.cb.conf['lycheepath'], 'uploads', 'big')
        res = self._count_files_in_dir(path)
        return res

    def count_fs_thumb(self):
        path = os.path.join(self.cb.conf['lycheepath'], 'uploads', 'thumb')
        res = self._count_files_in_dir(path)
        # 2 thumbs per image
        return (res / 2)

    def album_exists_in_db(self, a_name):
        return self.get_album_id(a_name)

    def get_album_id(self, a_name):
        res = None
        self._connect_db()
        try:
            # check if exists in db
            sql = "select id from lychee_albums where title='{}'".format(a_name)
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchmany(size=2)
                if (len(rows) == 1 and rows[0]):
                    res = rows[0]['id']
        except Exception as e:
            logger.exception(e)
            res = None
        finally:
            self.db.close()
            return res

    def get_album_photos(self, a_id):
        res = None
        self._connect_db()
        try:
            # check if exists in db
            sql = "select url from lychee_photos where album='{}'".format(a_id)
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                res = []
                for r in rows:
                    res.append(r['url'])
        except Exception as e:
            logger.exception(e)
            res = None
        finally:
            self.db.close()
            return res

    def photo_exists_in_fs(self, photo):
        res = False
        try:

            # check if exists 1x in big
            big_path = os.path.join(self.cb.conf['lycheepath'], 'uploads', 'big', photo)
            assert os.path.exists(big_path), "Does not exists {}".format(big_path)
            # check if exists 2x in thumbnail
            thumb_path = os.path.join(self.cb.conf['lycheepath'], 'uploads', 'thumb', photo)
            assert os.path.exists(thumb_path), "Does not exists {}".format(thumb_path)
            file, ext = photo.split('.')
            thumb_path = os.path.join(
                self.cb.conf['lycheepath'], 'uploads', 'thumb', ''.join([file, '@2x.', ext]))
            assert os.path.exists(thumb_path), "Does not exists {}".format(thumb_path)
            res = True
        except Exception as e:
            logger.exception(e)
        finally:
            return res

    def get_album_ids_titles(self):
        res = None
        self._connect_db()
        try:
            # check if exists in db
            sql = "select id, title from lychee_albums"
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
            res = rows
        except Exception as e:
            #logger.exception(e)
            res = None
            raise e
        finally:
            self.db.close()
            return res

    def check_album_size(self, a_name):
        res = None
        try:
            a_id = self.get_album_id(a_name)
            assert a_id, "Album does not exist in db"
            # check no of photo in db
            photos = self.get_album_photos(a_id)
            nb_photos_in_db = len(photos)
            # check if files exists on fs
            for p in photos:
                assert self.photo_exists_in_fs(p), "All photos for {} are not on fs".format(photos)
            #  every thing is ok
            res = nb_photos_in_db
        except Exception as e:
            logger.exception(e)
        finally:
            return res
