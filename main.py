#!/usr/bin/python
# -*- coding: utf-8 -*-

from lycheesync.sync import main

if __name__ == '__main__':
        import sys
        print(sys.argv[1:])
        main(sys.argv[1:])
