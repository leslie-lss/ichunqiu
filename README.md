# 概述
爬取春秋论坛白帽子技术版块的所有帖子内容，进行分词预处理，并且存入mongodb中

# 网址分析

## 版块网址分析

论坛首页：https://bbs.ichunqiu.com/portal.php

版块列表：https://bbs.ichunqiu.com/portal.php

白帽子技术/思路版块：https://bbs.ichunqiu.com/forum-59-1.html

或：https://bbs.ichunqiu.com/forum.php?mod=forumdisplay&fid=59&page=1

其中59为版块代号，不同代号代表不同的版块，1为页码代号

## 帖子列表网址分析

例如以下几篇帖子的网址：

https://bbs.ichunqiu.com/thread-46970-1-1.html

https://bbs.ichunqiu.com/thread-30119-1-1.html

https://bbs.ichunqiu.com/thread-46687-1-1.html

https://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=46687&extra=page%3D1&page=1

其中thread-a-b-c的意义为:

a对应为每一个帖子的代码，是唯一的；

b对应为该帖子的第几页；

C均为1。

白帽子技术版块按照发帖时间排序：	

https://bbs.ichunqiu.com/forum.php?mod=forumdisplay&fid=59&orderby=dateline&orderby=dateline&filter=author&page=1

# 网页页面元素分析

## 帖子列表页面元素分析

在白帽子技术版块，可以看到整个版块的帖子列表，可以获取到每个帖子的url：

Xpath：//*[starts-with(@id,'normalthread_')]/tr/th/a[1]/@href

## 帖子页面元素分析

帖子每一页的主要内容均处于id=”postlist”的div标签中，如下图所示：

>![帖子页面结构](https://github.com/leslie-lss/ichunqiu/blob/master/image.png)

其中：

帖子的主题类型及帖子标题位于第一个table标签中；

接下来的多个id=”post_*”的div标签为帖子每一楼的内容，对于帖子的第一页来说，第一个div标签即为首楼的内容。

# 爬网程序实现

## 爬虫流程

1、按照发帖时间获取到白帽子版块所有帖子的url

2、针对每个帖子，爬取页面元素，并存入MongoDB中

3、对爬取到的帖子内容进行分词、过滤停用词等预处理

## 关键程序流程分析

### 帖子内容爬取

1、反爬

  >添加headers进行伪装，同时不停切换user-agent来反反爬，春秋论坛并没有针对IP的访问频次进行反爬，不需要切换IP。

2、页面元素的提取

  >利用lxml包中的etree来解析DOM树，通过XPath来定位页面元素并提取。

  >主要的页面元素有：

  >帖子页数、帖子类型、标题、帖子的阅读数目、回帖数目、每一楼的用户、用户等级、内容、时间

  >每个元素的具体定位不再详细说明，具体实现可查看程序。

### 文本预处理

1、利用正则表达式，过滤掉文本中的网址url

2、过滤掉无用字符，保留中英文文本，同时统一英文的大小写

3、利用jieba实现分词

4、利用现有的停用词表对分词结果进行分词停用，过滤掉无意义的分词

# 数据存储结构

在MongoDB中，每个帖子以一条信息的方式存储，每条信息的具体字段意义如下表所示：

key | 意义
-------- | --------
_id	| 帖子的ID号，唯一，且可以凭借ID确定帖子的url
url	| 帖子的地址
error	| （大多没有）获取不到帖子内容时，一般是没有查看帖子权限时，显示为"can't crawl!!"
page_total	| 帖子页数
forum_type	| 帖子类型
title	| 帖子标题
author	| 发帖人用户名
author_level	| 发帖用户等级
post_time	| 发帖时间
reply_count	| 回复数目
see_count	| 查看数目
post_text	| 帖子正文
reply_dicts	| 列表，列表元素为字典。包含所有的回复信息，每一条回复以字典的形式存储，每个字典中存储回复人的用户名、等级、回复时间、回复内容、以及过滤掉url的内容和保留中英文文本之后的内容
post_text_no_url	| 过滤掉网址url的帖子文本
post_text_chi_eng	| 保留中英文字符之后的帖子文本
reply_text_chi_eng	| 保留中英文字符之后的所有回复的文本，其中不包含字符数小于等于5的回复
post_text_final	 | 分词并且过滤掉停用词之后的帖子分词
reply_text_final	| 分词并且过滤掉停用词之后的回帖分词

