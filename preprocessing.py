# -*- coding: utf-8 -*-
#www.ichunqiu.com
#处理获取到的帖子内容
#过滤掉英文及特殊字符，保留中文字符
#利用jieba进行中文分词
from pymongo import MongoClient
import jieba
import re


def import_stopword_dict():
    stopwords = []
    with open('stopword.txt', 'r') as f:
        for line in f.readlines():
            line = line.decode('utf-8')
            stopwords.append(line[:-1])
    return stopwords

def get_dict_from_mongo():
    conn = MongoClient('192.168.0.50', 27017)
    db = conn.jieba
    my_set = db.test_1029
    for x in my_set.find():
        # post_id = x['_id']
        print(x['url'])
        # if int(post_id) <= 8532:
        if x.has_key('error'):
            save_mongo(x)
            continue
        dict = filter_url(x)
        dict = remain_chinese_english(dict)
        print('remain_chinese_english:')
        print(dict['post_text_chi_eng'])
        print(dict['reply_text_chi_eng'])
        dict = jieba_text(dict)
        print('stop_word:')
        print(dict['post_text_final'])
        print(dict['reply_text_final'])
        save_mongo(dict)
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

#过滤掉文本中的网址url
def filter_url(dict):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = re.findall(pattern, dict['post_text'])
    dict['post_text_no_url'] = re.sub(pattern, ' ', dict['post_text'])
    print('all urls:')
    for url in urls:
        print(url)

    for reply_dict in dict['reply_dicts']:
        reply_dict['post_text_no_url'] = re.sub(pattern, ' ', reply_dict['post_text'])
    return dict

def remain_chinese(dict):
    #处理帖子正文，保留中文字符
    post_text = dict['post_text']
    new_post_text = ''
    for uchar in post_text:
        if is_chinese(uchar):
            new_post_text = new_post_text + uchar
    dict['chinese_post_text'] = new_post_text.encode('utf-8')
    #处理帖子回复，保留中文字符
    dict['chinese_reply_text'] = ''
    for reply_dict in dict['reply_dicts']:
        reply_text = reply_dict['post_text']
        new_reply_text = ''
        for uchar in reply_text:
            if is_chinese(uchar):
                new_reply_text = new_reply_text + uchar
        reply_dict['chinese_post_text'] = new_reply_text.encode('utf-8')
        dict['chinese_reply_text'] = dict['chinese_reply_text'] + ' ' + reply_dict['chinese_post_text']
    return dict

#保留中英文字符
def remain_chinese_english(dict):
    # 处理帖子正文，保留中英文字符，其余均替换为space
    post_text = dict['post_text_no_url']
    new_post_text = ''
    for uchar in post_text:
        if is_chinese(uchar):
            new_post_text = new_post_text + uchar
        elif is_english(uchar):
            new_post_text = new_post_text + uchar.lower()
        else:
            new_post_text = new_post_text + ' '
    dict['post_text_chi_eng'] = new_post_text.encode('utf-8')
    # 处理帖子回复，保留中英文字符，其余均替换为space
    dict['reply_text_chi_eng'] = ''
    for reply_dict in dict['reply_dicts']:
        reply_text = reply_dict['post_text_no_url']
        new_reply_text = ''
        for uchar in reply_text:
            if is_chinese(uchar):
                new_reply_text = new_reply_text + uchar
            elif is_english(uchar):
                new_reply_text = new_reply_text + uchar.lower()
            else:
                new_reply_text = new_reply_text + ' '
        reply_dict['post_text_chi_eng'] = new_reply_text.encode('utf-8')
        #五个字以下的回复直接过滤掉，不进行分词
        if len(reply_dict['post_text_chi_eng']) > 5:
            dict['reply_text_chi_eng'] = dict['reply_text_chi_eng'] + ' ' + reply_dict['post_text_chi_eng']
    return dict

#判断一个unicode是否为汉字
def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

#判断一个unicode是否为英文字符
def is_english(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False


#利用jiaba进行分词
def jieba_text(dict):
    post_text = dict['post_text_chi_eng']
    reply_text = dict['reply_text_chi_eng']
    seg_post = jieba.cut(post_text)
    seg_reply = jieba.cut(reply_text)
    dict['post_text_final'] = stop_word(seg_post).encode('utf-8')
    dict['reply_text_final'] = stop_word(seg_reply).encode('utf-8')
    return dict

#去除掉无意义的停用词
def stop_word(seg_list):
    final_text = ''
    for word in seg_list:
        if word not in stopwords:
            final_text = final_text + ' ' + word
    return final_text

def save_mongo(dict):
    conn = MongoClient('192.168.0.50', 27017)
    db = conn.jieba
    my_set = db.jieba_1031_1657
    try:
        my_set.insert(dict)
        print('******************insert database success!*************************')
    except:
        print('###################insert database fail!!#######################')

if __name__ == '__main__':
    stopwords = import_stopword_dict()
    get_dict_from_mongo()
