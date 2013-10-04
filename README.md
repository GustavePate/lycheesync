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
- git

On debian based Linux:

`sudo apt-get install imagemagick python python-mysql python-imaging git`


Then retrieve the project:

`git clone https://github.com/GustavePate/lycheesync`

Finally, adjust the `conf.json` file to you use case.

# Basic usage

## Configuration

The configuration file is straight-forward.
Simply enter your Lychee DB configuration.
publicAlbum and starPhoto should be set to 1 if you wan't to make public or star all your photos.


```json
{
    "db":"lychee",
    "dbUser":"lychee",
    "dbPassword":"cheely",
    "dbHost":"localhost",
    "thumbQuality":80,
    "publicAlbum": 0,
    "starPhoto": 0
}
```

## Command line parameters



The basic usage is `python main.py srcdir lycheepath conf`

Where:
- `srcdir` is the directory containing photos you wan't to add to leeche
- `lycheepath` is the path were you installed Lychee (usually /var/ww/lychee)
- `conf` is the full path to your configuration file

## Explanation


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

At the end of the scipt a few counters will be displayed in order to keep you informed of what have been done.

```text
Directory scanned: /var/www/lychee/Lychee/dirsync/test/
Created albums:  4
10 photos imported on 10 discovered
```

#  Advanced usage

You can choose between the following options to adjust the program behaviour:

- `-v` **verbose mode**. A little more output
- `-r` **replace album mode**. If a pre-existing album is found in Lychee that match a soon to
  be imported album. The pre-existing album is removed before hand. Usefull if you wan't to have lychee in slave mode only for a few albums
- `-d` **drop all mode**. Everything in Lychee is dropped before import. Usefull to make lychee
  a slave of another repository


# Technical doc

This code is pep8 compliant and well documented, if you wan't to contribute, thanks to
keep it this way.

This project files are:
* main.py: argument parsing and conf reading, defer work to lycheesyncer
* lycheesyncer: logic and filesystem operations
* lycheedao: database operations
* lycheemodel: a lychee photo representation, manage exif tag parsing too
* conf.json: the configuration file

# Known limitation

When a photo has an [exif orientation](http://sylvana.net/jpegcrop/exif_orientation.html) equals 6, which is produce by some cameras, the photo is rotated to display correctly on lychee.
Thanks to PIL, all exif data is lost in the process :(


# Licence

[MIT License](./LICENSE)
