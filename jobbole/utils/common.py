# -*- coding: utf-8 -*-
# Author  :  Sxt
# Date    :  2018/6/10 16:37
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    #  从字符串里提取数字
    match_re = re.match('.*?(\d+).*?', text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

if __name__ == '__main__':
    print(get_md5("http://jobbloe.com".encode("utf-8")))