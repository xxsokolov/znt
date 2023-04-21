# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import pytest


@pytest.mark.tryfirst
def pytest_itemcollected(item):
    # par = item.parent.obj
    node = item.obj
    # pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if suf:
        item._nodeid = suf