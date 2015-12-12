#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pformat


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class ConfBorg(Borg):

    isinitialized = False

    def __init__(self, confdic=None):
        Borg.__init__(self)
        if not (self.isinitialized):
            if confdic:
                self.confdic = confdic
                self.isinitialized = True
            else:
                raise Exception('ConfBorg not initialized')

    def __str__(self):
        return str(self.val)

    @property
    def pretty(self):
        return pformat(self.confdic)

    @property
    def conf(self):
        return self.confdic
