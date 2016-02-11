#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def get_kanjis(string):
    """Returns all kanjis from $string as a list"""
    return re.findall(ur'[\u4e00-\u9fbf]', string)


def highlight_match(string, match, pre='<span style="color:red">', after='</span>'):
    """Looks for all occurences of the character $match in $string and returns
    the string with $pre$match$after inserted for every $match. """
    if not len(match) == 1:
        # just to make sure....
        raise (ValueError, "Argument $match must be single character letter!")
    out = ""
    for letter in string:
        if letter != match:
            out += letter
        else:
            out += pre+letter+after
    return out


def clean(string, unwanted, replace):
    """ Replaces all the elements from list $unwanted in $string by $replace.
    (case insensitive!)"""
    for uw in unwanted:
        regex = re.compile(re.escape(uw), re.IGNORECASE)
        string = regex.sub(replace, string)
    return string