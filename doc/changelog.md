# Changelog

## v3.0.8

*Warning* this is a breaking release new python packages must be installed (see the Install section in ReadMe)

- automated testing
- travis ci
- compatibility with python 3
- don't lower case album name
- photos ordered by name in an album
- make use of the DateTimeOriginal exif tag
- dependency change: switch to a pure python mysql driver
- dependency change: use click to parse arguments

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

