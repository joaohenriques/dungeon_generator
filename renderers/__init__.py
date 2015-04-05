__author__ = 'jpsh'

from abc import ABCMeta, abstractmethod


class MapRenderer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, cave):
        pass