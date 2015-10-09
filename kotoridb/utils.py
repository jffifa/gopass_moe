# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import
def guess_tv_name(url):
    TV_LIST = {
        'iqiyi':'爱奇艺',
        'sohu':'搜狐视频',
        'bilibili':'bilibili',
        'pptv':'pptv',
        'youku':'优酷',
        'tudou':'土豆',
        'qq':'腾讯视频',
        'letv':'乐视',
    }
    for pattern, name in TV_LIST.items():
        if (pattern+'.') in url:
            return name

    return 'link'

def resize_img(f, max_width, max_height):
    pass
