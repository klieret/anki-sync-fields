#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def get_kanjis(string):
    """Returns all kanjis from $string as a list.
    :type string: str
    """
    return re.findall(ur'[\u4e00-\u9fbf]', string)


def ci_list_replace(string, replace_me, replace):
    """ Replaces all case insensitive matches of strings from the list $replace_me
    in the string $string with the string $replace.
    Example: ci_list_replace_at("aabcdefg", ["a", "d", "f", "g"], "x") will return "xxbcxexx".
             Input:  aabcdefg
             Output: xxbcxexx
    :param string: Input string
    :param replace_me: A list of substrings to be replaced.
    :param replace: String with which to be replaced substrings will be replaced.
    :return:
    """
    # build regular expression [<replace_me string 1><replace_me string 2>....], matching
    # any of the characters (but only one at a time).
    regex_string = '[%s]' % ''.join([re.escape(uw) for uw in replace_me])
    regex = re.compile(regex_string, re.IGNORECASE)
    return regex.sub(replace, string)


def ci_list_replace_trailing(string, replace_me, replace):
    """ Replaces an arbitrary combination of strings from the list $replace_me at the end
    of the string $string with the string $replace.
    Example: ci_list_replace_at("abcdefgg", ["a", "d", "f", "g"], "x") will return "abcdex".
             Input:  abcdefgg
             Output: abcdex
    Important note: The string $replace is inserted only once! ("acdex" not "acdexxx")
    :param string: Input string
    :param replace_me: A list of substrings to be replaced.
    :param replace: String with which to be replaced substrings will be replaced.
    :return:
    """
    # Note: Be careful with using re's '$' to match the end of the string, because it will also
    #       match right before a linebreak '\n'. Solution: Use '$(?!\n)' instead (match end of line
    #       except there's still a '\n' following.
    # Build a regular expression hat matches any combination of the strings from replace_me at the
    # (real) end of the string:
    regex_string = '[%s]*$(?!\n)' % ''.join([re.escape(uw) for uw in replace_me])
    regex = re.compile(regex_string, re.IGNORECASE)
    return regex.sub(replace, string)
