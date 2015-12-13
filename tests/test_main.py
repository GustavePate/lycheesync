# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import logging
import subprocess
import os
import shutil
import time
from tests.testutils import TestUtils

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("clean")
@pytest.mark.usefixtures("initdb_and_fs")
@pytest.mark.usefixtures("confborg")
@pytest.mark.usefixtures("initloggers")
class TestClass:

    def check_grand_total(self, expected_albums, expected_photos):

        tu = TestUtils()
        assert (tu.count_db_albums() == expected_albums), "there should be {} albums in db".format(
            expected_albums)
        assert (tu.count_db_photos() == expected_photos), "there should be {} photos in db".format(
            expected_photos)
        # assert Number of photo / thumbnail on filesystem
        # assert Number of photo / thumbnail on filesystem
        assert tu.count_fs_thumb() == expected_photos
        assert tu.count_fs_photos() == expected_photos

    def test_env_maker(self):
        tu = TestUtils()
        # clean all
        tu.drop_db()
        upload_path = os.path.join(tu.conf['lycheepath'], '/uploads')
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        tu.make_fake_lychee_db()
        tu.make_fake_lychee_fs(tu.conf['lycheepath'])
        # file system exists
        assert os.path.exists('/tmp/uploads/big')
        assert os.path.exists('/tmp/uploads/medium')
        assert os.path.exists('/tmp/uploads/thumb')
        # table exists
        assert tu.table_exists('lychee_albums')
        assert tu.table_exists('lychee_photos')

    def test_subdir(self):
        try:
            tu = TestUtils()
            # copy directory to tmptest
            tu.load_photoset("album2")

            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v -d'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"
            # assert Number of album / photos in database
            expected_albums = 3
            expected_photos = 4
            assert (tu.count_db_albums() == expected_albums), "there should be {} albums in db".format(
                expected_albums)
            assert (tu.count_db_photos() == expected_photos), "there should be {} photos in db".format(
                expected_photos)
            # assert Number of photo / thumbnail on filesystem
            assert tu.count_fs_thumb() == expected_photos
            assert tu.count_fs_photos() == expected_photos

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    def test_duplicate(self):
        try:
            tu = TestUtils()
            # copy directory to tmptest
            tu.load_photoset("album2")

            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"
            # re-run
            retval = subprocess.call(cmd, shell=True)
            assert (retval == 0), "process result is ok"

            # assert Number of album / photos in database
            expected_albums = 3
            expected_photos = 4
            assert (tu.count_db_albums() == expected_albums), "there should be {} albums in db".format(
                expected_albums)
            assert (tu.count_db_photos() == expected_photos), "there should be {} photos in db".format(
                expected_photos)
            # assert Number of photo / thumbnail on filesystem
            # assert Number of photo / thumbnail on filesystem
            assert tu.count_fs_thumb() == expected_photos
            assert tu.count_fs_photos() == expected_photos
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    def test_dash_r(self):
        try:
            tu = TestUtils()
            # load album x and y
            tu.load_photoset("album1")
            tu.load_photoset("album3")

            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v -r'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"
            assert tu.album_exists_in_db("album1")
            # read album date for album1
            album1_date = tu.get_album_creation_date('album1')
            # read album date for album3
            album3_date = tu.get_album_creation_date('album3')
            # empty tmp pictures folder
            tu.delete_dir_content(src)

            # sleep 1 s to make time album signature different
            time.sleep(1)

            # load album3
            tu.load_photoset("album3")

            cmd = 'python main.py {} {} {} -v -r'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"

            album1_date_2 = tu.get_album_creation_date('album1')
            album3_date_2 = tu.get_album_creation_date('album3')
            # y date < time
            assert album1_date == album1_date_2, 'album 1 is untouched'
            assert tu.check_album_size('album1') == 1

            # x date > time
            assert album3_date < album3_date_2, 'album 3 has been modified'
            assert tu.check_album_size('album3') == 4

            expected_albums = 2
            expected_photos = 5
            self.check_grand_total(expected_albums, expected_photos)

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    def test_dash_d(self):
        try:
            # load album y
            tu = TestUtils()
            # load album x and y
            tu.load_photoset("album1")
            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v -r'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"
            assert tu.check_album_size("album1") == 1, "album 1 not correctly loaded"

            # clean input pics content
            tu.delete_dir_content(src)
            # load album x
            tu.load_photoset("album3")
            # launch lycheesync
            cmd = 'python main.py {} {} {} -v -d'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"
            assert tu.check_album_size("album3") == 4, "album 3 not correctly loaded"
            # album 1 has been deleted
            a1_check = tu.album_exists_in_db("album1")
            assert not(a1_check), "album 1  still exists"

            expected_albums = 1
            expected_photos = 4
            self.check_grand_total(expected_albums, expected_photos)

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    # without -s albums id should not be sorted by name
    def test_dash_wo_s(self):
        try:
            # -s => no album reorder
            tu = TestUtils()
            # load a bunch of album
            tu.load_photoset("aaa")
            tu.load_photoset("mini")
            tu.load_photoset("zzzz")
            tu.load_photoset("album1")
            tu.load_photoset("album3")
            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            assert (retval == 0), "process result is ok"

            # get a_id, a_names
            list = tu.get_album_ids_titles()
            logger.info(list)
            # album name sorted

            # id sorted
            ids = sorted([x['id'] for x in list])
            titles = sorted([x['title'] for x in list])

            logger.info(ids)
            logger.info(titles)

            # combine
            ordered_list = zip(ids, titles)
            logger.info(ordered_list)
            # for each sorted
            well_sorted = True
            for x in ordered_list:
                logger.info(x)

                if (tu.get_album_id(x[1]) != x[0]):
                    well_sorted = False

            assert (not well_sorted), "elements should not be sorted"

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    # with the -s switch album ids should be sorted by album title
    def test_dash_s(self):
        try:
            # -s => no album reorder
            tu = TestUtils()
            # load a bunch of album
            tu.load_photoset("aaa")
            tu.load_photoset("mini")
            tu.load_photoset("zzzz")
            tu.load_photoset("album1")
            tu.load_photoset("album3")
            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            cmd = 'python main.py {} {} {} -v -s'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            assert (retval == 0), "process result is ok"

            # get a_id, a_names
            list = tu.get_album_ids_titles()
            logger.info(list)
            # album name sorted

            # id sorted
            ids = sorted([x['id'] for x in list])
            titles = sorted([x['title'] for x in list])

            logger.info(ids)
            logger.info(titles)

            # combine
            ordered_list = zip(ids, titles)
            logger.info(ordered_list)
            # for each sorted
            well_sorted = True
            for x in ordered_list:
                assert (tu.get_album_id(x[1]) == x[0]), "element not ordered "+x[1]

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_dash_l(self):
        try:
            # load album y
            tu = TestUtils()
            # load album x and y
            tu.load_photoset("album1")
            # launch lycheesync
            src = tu.conf['testphotopath']
            lych = tu.conf['lycheepath']
            conf = tu.conf['conf']
            # -l => symbolic links instead of files
            cmd = 'python main.py {} {} {} -v -l'.format(src, lych, conf)
            logger.info(cmd)
            retval = -1
            retval = subprocess.call(cmd, shell=True)
            # process is ok
            assert (retval == 0), "process result is ok"

            # check if files are links

        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_unicode(self):
        try:
            # load unicode album name
            # there is a unicode album
            # there is a unicode photo
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_long_album(self):
        try:
            # get max_width column album name width
            # load >max_width album name
            # there is a max_width album
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_bad_taketime(self):
        try:
            # load "bad taketime"  album name
            # success
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_sha1(self):
        try:
            # load 1 album with same photo under different name
            # load 2 album with same photo under different name
            # no duplicate
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_corrupted(self):
        try:
            # load 1 album with a corrupted file
            # no import
            # no crash
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_last_import_for_manual_check(self):
        try:
            # load 1 album with a corrupted file
            # no import
            # no crash
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False

    @pytest.mark.xfail(reason="Not implemented")
    def test_album_keep_original_case(self):
        try:
            # load 1 album with a mixed case name and spaces
            # name in db is equal to directory name
            # no crash
            assert False
        except AssertionError:
            raise
        except Exception as e:
            logger.exception(e)
            assert False
