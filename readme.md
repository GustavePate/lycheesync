# Context

This project was created to syncronize an [owncloud](http://owncloud.org/) photo repositories and [Lychee](http://lychee.electerious.com/).
It turns out it can, totally or partially, enslave Lychee with a given directory structure.

The program is simple it scans a directory for files and sub-directories:
- subdirectories are converted to Lychee albums
- files are imported in Lychee as photos

You can choose between 3 behaviours:
- *Lychee as a slave*: Lychee db is drop before each run `-d option`
- *Lychee as a slave only for album in the source directories*: others albums existing in
  Lychee but not in the source directory will be kept `-r option`
- *Keep existing Lychee albums and photos* The program will try to know if a photo in the
  source directory has already been imported in Lychee and does nothing in this case, this is the default behaviour

# Install

First you have to install the following dependencies:
- python 2.7
- mysql bindings for python
- PIL
- git

On debian based Linux:
`sudo apt-get install python python-mysql python-imaging git`

Then retrieve the project:

`git clone xxx`

Finally, adjust the `conf.json` file to you use case.

# Basic usage

## Configuration

The configuration file is straight-forward.
Simply enter your Lychee DB configuration.
publicAlbum and starPhoto should be set to 1 if you wan't to make public or star all your photos.

{
    "db":"lychee",
    "dbUser":"lychee",
    "dbPassword":"cheely",
    "dbHost":"localhost",
    "thumbQuality":80,
    "publicAlbum": 0,
    "starPhoto": 0
}

## Run example

Given the following  source tree

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


And this lychee prexisting structure

|_album1
 |_a1p1.jpg
 |_a1p3.jpg
|_album3
 |_a3p1.jpg

The resulting lychee structure will be


|_album1
 |_a1p1.jpg (won't be re-imported by default)
 |_a1p2.jpg
 |_a1p3.jpg
|_album2_album21
  |_a21p1.jpg
  |_a21p2.jpg
|_album2_album22
  |_a22p1.jpg
|_album3
 |_a3p1.jpg


* counters

#  Usage

## Basic

The basic usage is `python main.py srcdir lycheepath conf`

Where:
- `srcdir` is the directory containing photos you wan't to add to leeche
- `lycheepath` is the path were you installed Lychee (usually /var/ww/lychee)
- `conf` is the full path to your configuration file

## Advanced

You can choose between the following options to adjust the program behaviour:

- `-v`: verbose mode, a little more output
- `-r`: replace album mode, if an pre-existing album is found in Lychee that match a soon to
  be imported album. The pre-existing album is removed before hand. Usefull if you wan't to have lychee in slave mode only for a few albums
- `-d`: drop all mode. Everything in Lychee is dropped before import. Usefull to make lychee
  a slave of another repositorie


# Technical doc

This code is pep8 compliant and well documeented, if you wan't to contribute, thanks to
keep it this way.

This project files are:
* main.py: argument parsing and conf reading, defer work to lycheesyncer
* lycheesyncer: logic and filesystem operations
* lycheedao: database operations
* lycheemodel: a lychee photo representation, manage exif tag parsing too
* conf.json: the configuration file
