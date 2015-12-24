from __future__ import print_function
from __future__ import unicode_literals
import os
import pwd
import grp
from lycheesync.lycheesyncer import LycheeSyncer
import MySQLdb
import hashlib
import stat
import traceback


# Compute checksum
def __generateHash(filepath):
    checksum = None
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        sha1.update(f.read())
        checksum = sha1.hexdigest()
    return checksum


def updatedb(conf_data):
    print("updatedb")

    # read permission of the lycheepath directory to apply it to the uploade photos
    upload_dir = os.path.join(conf_data["lycheepath"], "uploads")
    stat_info = os.stat(upload_dir)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    user = pwd.getpwuid(uid)[0]
    group = grp.getgrgid(gid)[0]

    conf_data["user"] = user
    conf_data["group"] = group
    conf_data["uid"] = uid
    conf_data["gid"] = gid

    syncer = LycheeSyncer(conf_data)

    # for each file in upload fix the permissions
    for root, dirs, files in os.walk(upload_dir):
        for f in files:
            if syncer.isAPhoto(f):
                # adjust permissions
                filepath = os.path.join(root, f)
                os.chown(filepath, int(uid), int(gid))
                st = os.stat(filepath)
                os.chmod(filepath, st.st_mode | stat.S_IRWXU | stat.S_IRWXG)
                print("Changed permission for " + str(f))

    # connect to db
    try:
        db = MySQLdb.connect(host=conf_data["dbHost"],
                             user=conf_data["dbUser"],
                             passwd=conf_data["dbPassword"],
                             db=conf_data["db"])

        # get photo list
        cur = db.cursor()
        cur.execute("SELECT id, url from lychee_photos")
        rows = cur.fetchall()
        for row in rows:

            pid = row[0]
            url = row[1]

            photo_path = os.path.join(upload_dir, "big", url)
            chksum = __generateHash(photo_path)
            # for each photo in db recalculate checksum
            qry = "update lychee_photos set checksum= '" + chksum + "' where id=" + str(pid)
            try:
                cur = db.cursor()
                cur.execute(qry)
                db.commit()
                print("INFO photo checksum changed to: ", chksum)
            except Exception:
                print("checksum modification failed for photo:" + id, Exception)
                traceback.print_exc()

        print("******************************")
        print("SUCCESS")
        print("******************************")
    except Exception:
        traceback.print_exc()
    finally:
        db.close()
