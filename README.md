# Lycheesync

[![Build Status](https://travis-ci.org/GustavePate/lycheesync.svg)](https://travis-ci.org/GustavePate/lycheesync) [![Coverage Status](https://img.shields.io/coveralls/GustavePate/lycheesync/master.svg)](https://coveralls.io/github/GustavePate/lycheesync?branch=master)

Lycheesync is a command line tool to synchronise a directory containing photos with Lychee.
* Lycheesync is meant to be used on the same server that run Lychee. If your photo source directory is on another computer, use synchronize tools like rsync or owncloud.
* Lycheesync is often meant to be run regulary and automatically, use cron for this (or monitor [filesystem events](https://github.com/seb-m/pyinotify) if you want your photos really fast online)

## WARNING: Breaking changes

Sorry for the inconvenience but Lycheesync has change a lot in the last weeks.
I added a few dependencies and remove others.
As an exemple the mysql driver has changed, so...
Check the install Chapter !

PS: I strongly recommand to use python3.4 with a virtualenv even if python2.7 will still be supported in the following months.

# Issue / logs

If you have read the documentation below and it still doesn't work as expected for you, feel free to submit a github issue.

Complete logs for the last run can be found in `logs/lycheesync.log`, if it's relevant, please attach them to your issue.

## Context

This project was created to synchronize an [owncloud](http://owncloud.org/) photo repositories and [Lychee](http://lychee.electerious.com/).
It turns out it can, totally or partially, enslave Lychee with any given directory structure.

The program is simple it scans a directory for files and subdirectories:
- subdirectories are converted to Lychee albums
- files are imported in Lychee as photos

You can choose between 3 behaviours:
- **Lychee as a slave**: Lychee db is drop before each run `-d option`
- **Lychee as a slave only for album in the source directories**: albums existing in
  Lychee but not in the source directory will be kept `-r option`
- **Keep existing Lychee albums and photos** The program will try to know if a photo in the
  source directory has already been imported in Lychee and does nothing in this case, this is the default behaviour


## What's new

See [changelog](./doc/changelog.md)

## Install

### Retrieve the project

`git clone https://github.com/GustavePate/lycheesync`

### Install dependencies

Then you have to install the following dependencies:

- python 2.7, 3.4 or 3.5 (python 3 prefered !)
- pillow
- dateutils
- [pymysql](https://github.com/PyMySQL/PyMySQL)
- [click](http://click.pocoo.org/)


#### Using a virtual env (the GOOD way)

On debian based Linux

    sudo apt-get install python3-dev python3.4-venv libjpeg-dev zlib1g-dev
    cd /path/to/lycheesync
    pyvenv-3.4 ./venv3.4
    . ./venv3.4/bin/activate
    which pip # should give you a path in your newly created ./venv3.4 dir
    # if not execute: curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python
    pip install -r requirements.txt

And wait for compilation to finish ;)

#### Using the distro package manager (the BAD way)

On debian based Linux

    sudo apt-get install python3-dev python3 python3-pymysql python3-click python3-pil python3-dateutil libjpeg-dev

PS: Depending on your distro version, you may need to activate universe repository for you distribution first.

### Adjust configuration

Finally, adjust the `ressources/conf.json` file to you use case.
Explanations in next chapter.

## Basic usage

### Configuration

The configuration file is straight-forward.
Simply enter your Lychee DB configuration.
publicAlbum should be set to 1 if you want to make public all your photos.


```json
{
    "db":"lychee",
    "dbUser":"lychee",
    "dbPassword":"cheely",
    "dbHost":"localhost",
    "thumbQuality":80,
    "publicAlbum": 0
}
```

### Command line parameters

The basic usage is `python -m lycheesync.sync srcdir lycheepath conf`

Where:
- `srcdir` is the directory containing photos you want to add to Lychee
- `lycheepath` is the path were you installed Lychee (usually `/var/www/lychee`)
- `conf` is the full path to your configuration file (usually `./ressources/conf.json`)

### Explanation

The default mod is a **merge** mode.

Given the following source tree:

```text
_srcdir
    |_album1
        |_a1p1.jpg
        |_a1p2.jpg
    |_album2
        |_album21
            |_a21p1.jpg
            |_a21p2.jpg
        |_album22
            |_a22p1.jpg
```

And this lychee prexisting structure:

```text
|_album1
    |_a1p1.jpg
    |_a1p3.jpg
|_album3
    |_a3p1.jpg
```

Lychee doesn't support yet sub-albums so any sub-directory in your source directory will be flat-out
The resulting lychee structure will be:


```text
|_album1
    |_a1p1.jpg (won't be re-imported by default)
    |_a1p2.jpg
    |_a1p3.jpg
|_album2_album21 (notice directory / subdirectory concatenation)
    |_a21p1.jpg
    |_a21p2.jpg
|_album2_album22
    |_a22p1.jpg
|_album3
    |_a3p1.jpg
```


### Counters

At the end of the script a few counters will be displayed in order to keep you informed of what have been done.

```text
Directory scanned: /var/www/lychee/Lychee/dirsync/test/
Created albums:  4
10 photos imported on 10 discovered
```

##  Advanced usage

### Command line switches

You can choose between the following options to adjust the program behaviour:

- `-v` **verbose mode**. A little more output
- `-r` **replace album mode**. If a pre-existing album is found in Lychee that match a soon to be imported album. The pre-existing album is removed before hand. Usefull if you want to have lychee in slave mode only for a few albums
- `-d` **drop all mode**. Everything in Lychee is dropped before import. Usefull to make lychee a slave of another repository
- `-l` **link mode**. Don't copy files from source folder to lychee directory structure, just create symbolic links (thumbnails will however be created in lychee's directory structure)
- `-s` **sort mode**. Sort album by name in lychee. Could be usefull if your album names start with the date (YYYYMMDD).
- `-c` `--sanitycheck` **sanity check mode**. Will remove empty album, orphan files, broken links...


### Choose your album cover

Add `_star` at the end of one filename in a directory and this photo will be stared, making it your album cover. Ex: `P1000274_star.JPG`

### Using crontab to automate synchronization

Add this line in your crontab (`crontab -e`) to synchronize a photo directory to your lychee installation every day at 2 am.

    0 2 * * * cd /path/to/lycheesync && . ./venv3.4/bin/activate && python -m lycheesync.sync /path/to/photo_directory/ /var/www/path/to/lychee/ ./ressources/conf.json -d > /tmp/lycheesync.out.log 2>&1


## Technical doc

This code is pep8 compliant and well documented, if you want to contribute, thanks to
keep it this way.

This project files are:
* lycheesync/sync.py: argument parsing and conf reading, defer work to lycheesyncer
* lycheesync/lycheesyncer: logic and filesystem operations
* lycheesync/lycheedao: database operations
* lycheesync/lycheemodel: a lychee photo representation, manage exif tag parsing too
* ressources/conf.json: the configuration file


# Licence

[MIT License](./doc/LICENSE)
