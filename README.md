# Changelog

## trunk

- don't lower case album name

## v3.0.1
- change versioning to match lychee's


## v2.7.1
- change versioning to match lychee's
- don't import duplicated files
- handle corrupted files correctly
- unicode directory name supported

## v2.6
- change versioning to match lychee's
- lychee 2.6 support
- fixed some permission problem: give the photo files the same group and owner than lychee uploads directory + rwx permission for group and user
- added an *update mode* to fix problem experienced by those who used lycheesync with a lychee 2.6 before this version. To update your lychee db an photo repository, just add the -u switch to your usual call (you can run it anyway, it won't break anything:)

`python main.py srcdir lycheepath conf -u`

## v1.3
- lychee 2.5 support


## v1.2
- added exif orientation support which was not totally fixed in luchee 2.0 ;)
- a photo containing 'star' or 'cover' in its filename will be automatically starred, thus making it the album cover
- photo titles now equals original filenames

## v1.1
- added suport for lychee 2.1
- removed exif orientation support (fixed in lychee 2.0)
- added takedate and taketime in photo description in order to be able to use the sort by description functionality of lychee 2.0
- albums display order is "sorted by name"
- album date is now the max takedate/taketime of its photos if exif data exists (if no, import date is used)

## v1.0
- initial version

# Context

This project was created to syncronize an [owncloud](http://owncloud.org/) photo repositories and [Lychee](http://lychee.electerious.com/).
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

# Install

First you have to install the following dependencies:
- python 2.7
- mysql bindings for python
- PIL
- dateutils
- git

On debian based Linux:

`sudo apt-get install imagemagick python python-mysqldb python-imaging python-dateutil git`


Then retrieve the project:

`git clone https://github.com/GustavePate/lycheesync`

Finally, adjust the `conf.json` file to you use case.

# Basic usage

## Configuration

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

## Command line parameters


The basic usage is `python main.py srcdir lycheepath conf`

Where:
- `srcdir` is the directory containing photos you want to add to leeche
- `lycheepath` is the path were you installed Lychee (usually /var/ww/lychee)
- `conf` is the full path to your configuration file

## Explanation

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


## Counters

At the end of the script a few counters will be displayed in order to keep you informed of what have been done.

```text
Directory scanned: /var/www/lychee/Lychee/dirsync/test/
Created albums:  4
10 photos imported on 10 discovered
```

#  Advanced usage

You can choose between the following options to adjust the program behaviour:

- `-v` **verbose mode**. A little more output
- `-r` **replace album mode**. If a pre-existing album is found in Lychee that match a soon to
  be imported album. The pre-existing album is removed before hand. Usefull if you want to have lychee in slave mode only for a few albums
- `-d` **drop all mode**. Everything in Lychee is dropped before import. Usefull to make lychee a slave of another repository
- `-l` **link mode**. Don't copy files from source folder to lychee directory structure, just create symbolic links (thumbnails will however be created in lychee's directory structure)
- `-s` **sort mode**. Sort album by name in lychee. Could be usefull if your album names start with the date (YYYYMMDD).




# Technical doc

This code is pep8 compliant and well documented, if you want to contribute, thanks to
keep it this way.

This project files are:
* main.py: argument parsing and conf reading, defer work to lycheesyncer
* lycheesyncer: logic and filesystem operations
* lycheedao: database operations
* lycheemodel: a lychee photo representation, manage exif tag parsing too
* conf.json: the configuration file


# Licence

[MIT License](./LICENSE)
