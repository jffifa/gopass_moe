# -*- coding: utf-8 -*-
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
