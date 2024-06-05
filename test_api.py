import re

import requests


def get_redirect_url(short_url):
    response = requests.get(short_url, allow_redirects=False)
    xhs = response.content.decode('utf-8')
    # 第一个匹配项
    matches = re.findall('xiaohongshu.com/discovery/item/(.*?)\?', xhs)
    if len(matches) > 0:
        return matches[0]
    return None


# 使用短的分享地址
short_url = 'http://xhslink.com/tUiI5K'
redirect_url = get_redirect_url(short_url)
print(redirect_url)  # 输出：目标跳转地址
