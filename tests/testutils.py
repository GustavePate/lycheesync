# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import os
import glob
import shutil
import re
import subprocess
import pymysql
import base64
from tests.configuration import TestBorg
from lycheesync.utils.configuration import ConfBorg
# from datetime import datetime
import pymysql.cursors

logger = logging.getLogger(__name__)


class TestUtils:

    def __init__(self):
        self.db = None
        self.cb = TestBorg()
        self._lychee_sync_conf_borg = ConfBorg(force_init=True)

    @property
    def conf(self):
        return self.cb.conf

    def _connect_db(self):
        db = pymysql.connect(host=self.cb.conf['dbHost'],
                             user=self.cb.conf['dbUser'],
                             passwd=self.cb.conf['dbPassword'],
                             db=self.cb.conf['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        return db

    def _exec_sql(self, db, sql):
        try:
            with db.cursor() as cursor:
                cursor.execute(sql)

            db.commit()

        except Exception as e:
            raise e

    def make_fake_lychee_fs(self, path):

        logger.info("make fake lychee fs")
        if not(os.path.isdir(os.path.join(path, 'uploads', 'big'))):
            uploads = os.path.join(path, 'uploads')
            os.mkdir(path)
            os.mkdir(uploads)
            paths = []
            paths.append(os.path.join(uploads, 'big'))
            paths.append(os.path.join(uploads, 'thumb'))
            paths.append(os.path.join(uploads, 'medium'))
            for p in paths:
                if not(os.path.isdir(p)):
                    logger.info('mkdir ' + p)
                    os.mkdir(p)

    def is_env_clean(self, path):
        check = []
        logger.info("is env clean")
        try:
            folders = {}
            folders['big'] = os.path.join(path, 'uploads', 'big')
            folders['medium'] = os.path.join(path, 'uploads', 'medium')
            folders['thumb'] = os.path.join(path, 'uploads', 'thumb')
            # is dir
            check.append(os.path.isdir(folders['big']))
            check.append(os.path.isdir(folders['medium']))
            check.append(os.path.isdir(folders['thumb']))
            # is empty
            path = folders['big']
            check.append(0 == len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]))

            subprocess.call("ls /tmp/lychee/uploads/big/ -la", shell=True)
            assert len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]) == 0, "big is not empty"
            path = folders['medium']
            check.append(0 == len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]))
            path = folders['thumb']
            check.append(0 == len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]))
            # count album == 0
            albums = self.get_album_ids_titles()
            check.append(len(albums) == 0)

            # count photos == 0
            check.append(len(self.get_photos()) == 0)

        except Exception as e:
            logger.exception(e)
            check.append(False)
        finally:
            res = True
            for c in check:
                if not(c):
                    res = False
            return res

    def drop_db(self):
        # connect to db
        if self.db_exists():
            try:
                self.db = pymysql.connect(host=self.cb.conf['dbHost'],
                                          user=self.cb.conf['dbUser'],
                                          passwd=self.cb.conf['dbPassword'],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
            # check if db exists
                sql = "DROP DATABASE " + self.cb.conf['db']
                with self.db.cursor() as cursor:
                    cursor.execute(sql)
                self.db.commit()
                logger.info('drop database: ok')
            except Exception as e:
                logger.warn('drop database: ko', e)
            finally:
                self.db.close()

    def table_exists(self, table_name):
        res = False
        db = self._connect_db()
        try:
            sql = "show tables where Tables_in_{}='lychee_albums';".format(self.cb.conf['db'])
            with db.cursor() as cursor:
                cursor.execute(sql)
                res = (len(cursor.fetchall()) == 1)
        except Exception as e:
            raise e
        finally:
            db.close()
            return res

    def db_exists(self):
        res = True
        try:
            db = self._connect_db()
        except Exception as e:
            logger.warn("db does not exist yet... %s", e)
            res = False
        finally:
            try:
                db.close()
            finally:
                return res

    def make_fake_lychee_db(self):

        logger.info("make fake lychee db")
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
            logger.info('db created')
        except Exception as e:
            logger.exception('db already exists', e)
        finally:
            self.db.close()

        db = self._connect_db()

        try:
            # check if table exists
            sql = "show tables where Tables_in_{}='lychee_albums';".format(self.cb.conf['db'])
            with db.cursor() as cursor:
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
                    self.init_db_settings()
        except Exception as e:
            logger.exception(e)
        finally:
            db.close()

    def init_db_settings(self):
        db = self._connect_db()
        try:
            username = "foo"
            password = "bar"
            usernameb = bytearray()
            passwordb = bytearray()
            usernameb.extend(username.encode())
            usernameb.extend(username.encode())
            b64_username = base64.b64encode(usernameb)
            b64_password = base64.b64encode(passwordb)
            qry = "insert into lychee_settings (`key`, `value`) values ('username', %s)"
            with db.cursor() as cursor:
                try:
                    cursor.execute(qry, (b64_username))
                except Exception as e:
                    logger.warn(e)
                    logger.warn(cursor)
            qry = "insert into lychee_settings (`key`, `value`) values ('password', %s)"
            with db.cursor() as cursor:
                cursor.execute(qry, (b64_password))
            db.commit()
        except Exception as e:
            logger.exception(e)
        finally:
            db.close()

    def load_photoset(self, set_name, dest_name=None):
        testlibpath = self.cb.conf['testlib']
        testalbum = os.path.join(testlibpath, set_name)

        if dest_name is None:
            dest_name = set_name

        dest = os.path.join(self.cb.conf['testphotopath'], dest_name)
        shutil.copytree(testalbum, dest)  # , copy_function=shutil.copy)

    def clean_db(self):
        logger.info("Clean Database")
        # connect to db
        db = self._connect_db()
        try:
            if self.table_exists('lychee_albums'):
                self._exec_sql(db, "TRUNCATE TABLE lychee_albums;")
            if self.table_exists('lychee_photos'):
                self._exec_sql(db, "TRUNCATE TABLE lychee_photos;")
        except Exception as e:
            logger.exception(e)
        finally:
            try:
                db.close()
            finally:
                pass

    def _empty_or_create_dir(self, path):
        try:
            if os.path.isdir(path):
                path = os.path.join(path, '*')
                for f in glob.glob(path):
                    if os.path.lexists(f):
                        if os.path.isfile(f):
                            if not f.endswith("html"):
                                os.remove(f)
                        elif os.path.isdir(f):
                            shutil.rmtree(f)
                        elif os.path.islink(f):
                            os.unlink(f)
                        else:
                            logger.warn("will not remove: %s", f)
                    else:
                        logger.warn("will not remove not exists: %s", f)

            else:
                logger.info(path + ' not a dir, create it')
                os.makedirs(path, mode=0o777, exist_ok=True)

        except Exception as e:
            logger.exception(e)

    def clean_fs(self):

        logger.info("***************Clean Filesystem")
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
        db = self._connect_db()
        try:
            sql = "select count(1) as total from lychee_photos"
            with db.cursor() as cursor:
                cursor.execute(sql)
                count = cursor.fetchone()
                res = count['total']
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            db.close()
            return res

    def dump_table(self, table_name):
        db = self._connect_db()
        try:
            sql = "select * from " + table_name
            with db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    logger.info(row)

        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            db.close()

    def count_db_albums(self):
        res = -1
        db = self._connect_db()
        try:
            sql = "select count(1) as total from lychee_albums"
            with db.cursor() as cursor:
                cursor.execute(sql)
                count = cursor.fetchone()
                res = count['total']
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            db.close()
            return res

    def get_album_creation_date(self, a_name):
        res = -1
        db = self._connect_db()
        try:
            sql = "select sysstamp from lychee_albums where title='{}'".format(a_name)
            with db.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchone()
                sysstamp = data['sysstamp']
                # res = datetime.fromtimestamp(sysstamp)
                res = sysstamp
        except Exception as e:
            logger.exception(e)
            assert False
        finally:
            db.close()
            return res

    def _count_files_in_dir(self, path):
        res = -1
        try:
            res = len([name for name in os.listdir(path) if os.path.isfile(
                os.path.join(path, name)) or os.path.islink(os.path.join(path, name))])
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
        return (self.get_album_id(a_name) is not None)

    def get_album_id(self, a_name):
        res = None
        db = self._connect_db()
        try:
            # check if exists in db
            sql = "select id from lychee_albums where title='{}'".format(a_name)
            with db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchmany(size=2)
                if (len(rows) == 1 and rows[0]):
                    res = rows[0]['id']
        except Exception as e:
            logger.exception(e)
            res = None
        finally:
            db.close()
            return res

    def get_photos(self, a_id=None, p_id=None):
        """ get photos as a list of dictionnary. optionnal: a_id to get photos of one album """
        res = None
        db = self._connect_db()
        try:
            # check if exists in db
            if a_id:
                sql = "select id, title, url, iso, aperture, shutter, focal  from lychee_photos where album='{}'".format(a_id)
            elif p_id:
                sql = "select id, title, url, iso, aperture, shutter, focal  from lychee_photos where id='{}'".format(p_id)
            else:
                sql = "select id, title, url, iso, aperture, shutter, focal  from lychee_photos"

            with db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                res = []
                for r in rows:
                    photo = {}
                    photo['url'] = r['url']
                    photo['id'] = r['id']
                    photo['iso'] = r['iso']
                    photo['aperture'] = r['aperture']
                    photo['shutter'] = r['shutter']
                    photo['focal'] = r['focal']
                    photo['title'] = r['title']
                    res.append(photo)
        except Exception as e:
            logger.exception(e)
            res = None
        finally:
            db.close()
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

    def photo_exists_in_db(self, photo_id):
        res = False
        try:
            if (self.get_photos(p_id=photo_id)):
                res = True

        except Exception as e:
            logger.exception(e)
        finally:
            return res

    def get_album_ids_titles(self):
        res = None
        db = self._connect_db()
        try:
            # check if exists in db
            sql = "select id, title from lychee_albums"
            with db.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
            res = rows
        except Exception as e:
            # logger.exception(e)
            res = None
            raise e
        finally:
            db.close()
            return res

    def check_album_size(self, a_name):
        res = None
        try:
            a_id = self.get_album_id(a_name)
            assert a_id, "Album does not exist in db"
            # check no of photo in db
            photos = self.get_photos(a_id)
            nb_photos_in_db = len(photos)
            # check if files exists on fs
            for p in photos:
                assert self.photo_exists_in_fs(p['url']), "All photos for {} are not on fs".format(photos)
            #  every thing is ok
            res = nb_photos_in_db
        except Exception as e:
            logger.exception(e)
        finally:
            return res

    def get_column_width(self, table, column):
        res = 50  # default value
        query = "show columns from " + table + " where Field='" + column + "'"
        logger.info(query)
        db = self._connect_db()
        cur = db.cursor()
        try:
            cur.execute(query)
            row = cur.fetchone()
            logger.info(row)
            type = row['Type']
            # is type ok
            p = re.compile('varchar\(\d+\)', re.IGNORECASE)
            if p.match(type):
                # remove varchar(and)
                p = re.compile('\d+', re.IGNORECASE)
                ints = p.findall(type)
                if len(ints) > 0:
                    res = int(ints[0])
            else:
                logger.ERROR(
                    "unable to find column width for " +
                    table +
                    "." +
                    column +
                    " fallback to default")
        except Exception as e:
            logger.exception(e)
            logger.error("Impossible to find column width for " + table + "." + column)
        finally:
            db.close()
            return res

    def change_column_width(self, table, column, width):

        if width:

            try:
                query = "alter " + table + " modify " + column + " varchar(" + str(width) + ")"
                db = self._connect_db()
                self._exec_sql(db, query)
            except Exception as e:
                logger.exception(e)
                logger.error(
                    "Impossible to modify column width for " +
                    table +
                    "." +
                    column +
                    " to " +
                    str(width))
                raise
            finally:
                db.close()
