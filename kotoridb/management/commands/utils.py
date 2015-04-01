# -*- coding: utf-8 -*-
import re

def check_ascii(ch):
    return ord(ch)<128

def deal_str(s, rm_brackets=True):
    tr = '　 '
    s = s.strip(tr)
    if rm_brackets:
        # remove ()
        s = re.sub(r'([^()]+)\([^()]+\)', r'\1', s).strip(tr)
        s = re.sub(r'([^（）]+)（[^（）]+）', r'\1', s).strip(tr)
    # deal with space
    res = ''
    for i, c in enumerate(s):
        if c == ' ':
            if check_ascii(s[i-1]) or check_ascii(s[i+1]):
                res += c
        else:
            res += c
    return res

def split_str(s, delimiter, escape=[]):
    res = []
    # first get all escapes
    for es in escape:
        regex = '^%s(?=$|[%s])' % (es, delimiter)
        s, n = re.subn(regex, '', s)
        for i in range(n):
            res.append(es)
        regex = '(?<=[%s])%s(?=$|[%s])' % (delimiter, es, delimiter)
        s, n = re.subn(regex, '', s)
        for i in range(n):
            res.append(es)

    res.extend([ss.strip() for ss in re.split('|'.join(delimiter), s) if ss.strip()])
    return res

#if __name__=='__main__':
#    print(split_str('bw#z/ar/bw#z/zwc', '/#', ['bw#z']))

