# -*- coding: utf-8 -*-
#www.ichunqiu.com
#获取帖子的内容

import urllib
import requests
import random
import time
import re
from lxml import etree
from pymongo import MongoClient

my_headers = [    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
                  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
                  "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
                  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
                  "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
                  'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                  'Opera/9.25 (Windows NT 5.1; U; en)',
                  'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                  'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                  'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                  "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                  "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                  'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36']
headers = {
    'user-agent': random.choice(my_headers),
    'Connection': 'keep-alive',
    'host': 'bbs.ichunqiu.com',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Enocding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'referer': 'https://bbs.ichunqiu.com/forum.php',
}


def get_post(post_id):
    url = 'https://bbs.ichunqiu.com/thread-{0}-1-1.html'.format(post_id)
    page_source = requests.get(url, headers=headers).content
    html = etree.HTML(page_source)
    page_total = html.xpath("//*[@id='ct']/div[2]/div[1]/div[2]/div/label/span/text()")
    if len(page_total) == 0:
        page_total = 1
    else:
        page_total = page_total[0].replace('/', '').replace(' ', '').replace(u'页', '')
        page_total = int(page_total)
    print(page_total)
    postlist = html.xpath("//*[@id='postlist']")
    if len(postlist) == 0:
        post_dict = {
            'url': url,
            '_id': post_id,
            'error': "can't crawl!!"
        }
        save_mongo(post_dict)
        return
    else:
        postlist = postlist[0]
    forum_type = postlist.xpath("table[1]/tr/td[3]/div/h1/a/text()")
    if len(forum_type) == 0:
        forum_type = ''
    else:
        forum_type = forum_type[0]
    title = postlist.xpath("//*[@id='thread_subject']/a/text()")[0]
    dict1 = {
        'url': url,
        '_id': post_id,
        'page_total': page_total,
        'forum_type': forum_type,
        'title': title
    }
    posts = postlist.xpath("div[starts-with(@id,'post_')]")
    first_post = posts.pop(0)
    dict2 = get_first_post(first_post)
    post_dict = dict(dict1.items() + dict2.items())
    reply_dicts = []
    print(len(posts))
    while len(posts) > 0:
        reply_dicts.append(get_first_page_reply(posts.pop(0)))
    page = 2
    while page <= page_total:
        reply_dicts.extend(get_other_page_reply(post_id, page))
        page = page + 1
    post_dict['reply_dicts'] = reply_dicts
    save_mongo(post_dict)


def get_other_page_reply(post_id, page):
    url = 'https://bbs.ichunqiu.com/thread-{0}-{1}-1.html'.format(post_id, page)
    dict_list = []
    page_source = requests.get(url, headers=headers).content
    html = etree.HTML(page_source)
    postlist = html.xpath("//*[@id='postlist']")[0]
    posts = postlist.xpath("div[starts-with(@id,'post_')]")
    print(len(posts))
    while len(posts) > 0:
        dict_list.append(get_first_page_reply(posts.pop(0)))
    return dict_list

def get_first_post(first_post):
    #作者
    author = first_post.xpath("//*[starts-with(@id,'authorposton')]/a/text()")[0]
    #作者等级
    author_level = first_post.xpath(".//div[@class='authi']/div[2]/div[1]/a/text()")
    if len(author_level) == 0:
        author_level = ''
    else:
        author_level = author_level[0]
    post_time = first_post.xpath(".//div[@class='authi']/div[2]/div[2]/span/@title")
    if len(post_time) == 0:
        post_time = first_post.xpath(".//div[@class='authi']/div[2]/div[2]/text()")
        if len(post_time) == 0:
            post_time = ''
        else:
            post_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", post_time[0]).group(0)
    else:
        post_time = post_time[0]
    #回复数目
    reply_count = first_post.xpath("//span[@class='ico_reply y']/text()")[0]
    #阅读数目
    see_count = first_post.xpath("//span[@class='ico_see y']/text()")[0]
    #帖子正文
    post = first_post.xpath(".//*[starts-with(@id,'postmessage_')]/div[@class='parsedown-markdown']")
    if len(post) == 0:
        post = first_post.xpath(".//*[starts-with(@id,'postmessage_/div[@align]')]")
    if len(post) == 0:
        post = first_post.xpath(".//*[starts-with(@id,'postmessage_')]")
    post_text = ''
    for x in post:
        for eve_text in x.itertext():
            post_text = post_text + eve_text

    dict = {
        'author': author.encode('utf-8'),
        'author-level': author_level.encode('utf-8'),
        'post_time': post_time,
        'reply_count': reply_count,
        'see_count': see_count,
        'post_text': post_text.encode('utf-8')
    }
    return dict

def get_first_page_reply(post):
    # 作者
    author = post.xpath("//*[starts-with(@id,'authorposton')]/a/text()")[0]
    # 作者等级
    author_level = post.xpath(".//div[@class='authi']/div[2]/div[1]/a/text()")
    if len(author_level) == 0:
        author_level = ''
    else:
        author_level = author_level[0]
    post_time = post.xpath(".//div[@class='authi']/div[2]/div[2]/span/@title")
    if len(post_time) == 0:
        post_time = post.xpath(".//div[@class='authi']/div[2]/div[2]/text()")
        if len(post_time) == 0:
            post_time = ''
        else:
            post_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", post_time[0]).group(0)
    else:
        post_time = post_time[0]
    # 帖子正文
    post_all_text = post.xpath(".//*[starts-with(@id,'postmessage_')]/text()")
    post_text = ''
    for eve_text in post_all_text:
        post_text = post_text + eve_text
    dict = {
        'author': author.encode('utf-8'),
        'author-level': author_level.encode('utf-8'),
        'post_time': post_time,
        'post_text': post_text.encode('utf-8')
    }
    return dict

def save_mongo(dict):
    conn = MongoClient('192.168.0.50', 27017)
    db = conn.ichunqiu
    # my_set = db.test
    my_set = db.test_1029
    try:
        my_set.insert(dict)
        print('******************insert database success!*************************')
    except:
        print('###################insert database fail!!#######################')

def get_id_from_mongo():
    conn = MongoClient('192.168.0.50', 27017)
    db = conn.ichunqiu
    my_set = db.test_1024
    for x in my_set.find():
        post_id = x['_id']
        print(x['post_url'])
        # if int(post_id) <= 8532:
        get_post(post_id)
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

if __name__ == '__main__':
    get_id_from_mongo()
    # get_post(9999)
