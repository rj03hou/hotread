#核心目标

解决信息过载。
#功能简介
链接分享网站，形式和reddit、hacknews类似。

1. 支持tag、赞、评论基本功能。
1. 通过api获得weibo上该链接的转发、评论、赞次数，用于对链接进行自动打分，会影响到该链接的排序。
1. 数据来源包含两种：a.用户主动分享 b.rss源自动导入（按照主题维护公共的RSS源列表，比如database、linux、php、java、big data等），会根据2得到的分数对rss源中产生的数据进行过滤。跟RSS阅读器的区别：支持对链接进行打分，可以进行过滤；在时间有限的情况尽可能的去阅读一些高品质的文章，然后更多的时间去系统性的阅读书籍，进而提高阅读质量和效率。

#用户场景
1. 订阅了很多的RSS源但是时间有限，有大量的未读文章，因为没法进行过滤，因此会处于一种要么一个都不看，要么因为害怕受到伤害而拒绝一切的状态。
1. 公司内部技术交流处于不活跃状态，各自处于各自喜欢的社区中，而彼此不认识，比如A对tokudb非常感兴趣，并且阅读了一些文章，但是A活跃在微博；B也对tokudb感兴趣，但是B活跃在twitter；两个人虽然在同一个公司，但是没法直接进行交流。 
1. A是技术大牛，通过多年的积累了很多高质量的RSS源，B刚来公司，不知道从哪些地方来获取高质量的信息。
1. A部门研究了某项技术并且投入到实际使用中，在内部进行了分享并且wiki上有一些文档；B部门也需要该技术，但是B部门不知道A部门该技术已经投入使用，因此需要重新调研。 

#环境

###线上环境

ip:xxx

user:root

password:xx

###MySQL

host:xxx

database:gogoreader

user:gogoreader

password:gogoreader
###SQL
	CREATE TABLE `links_link` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(100) NOT NULL,
	`submitter_id` int(11) NOT NULL,
	`published_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`rank_score` double NOT NULL,
	`url` varchar(250) NOT NULL,
	`description` longtext NOT NULL,
	`short_url` varchar(20) DEFAULT '',
	`source` varchar(255) DEFAULT '',
	`weibo_sharecount` int(10) unsigned NOT NULL DEFAULT '0',
	`weibo_commentcount` int(10) unsigned NOT NULL DEFAULT '0',
	`tag_id` int(11) NOT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `uniq_url` (`url`),
	KEY `links_link_5f7282ee` (`submitter_id`),
	CONSTRAINT `submitter_id_refs_id_ac29084f` FOREIGN KEY (`submitter_id`) REFERENCES `auth_user` (`id`)
	) ENGINE=InnoDB

	CREATE TABLE `links_tag` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) NOT NULL,
	`submitter_id` int(11) NOT NULL,
	`published_time` datetime NOT NULL,
	PRIMARY KEY (`id`),
	KEY `links_tag_5f7282ee` (`submitter_id`),
	CONSTRAINT `submitter_id_refs_id_9bd4c3d9` FOREIGN KEY (`submitter_id`) REFERENCES `auth_user` (`id`)
	)

	CREATE TABLE `links_rsssource` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(255) NOT NULL,
	`published_time` datetime NOT NULL,
	`description` longtext NOT NULL,
	`tag_id` int(11) NOT NULL,
	`url` varchar(250) NOT NULL,
	PRIMARY KEY (`id`),
	KEY `links_rsssource_5659cca2` (`tag_id`),
	CONSTRAINT `tag_id_refs_id_76b63e16` FOREIGN KEY (`tag_id`) REFERENCES `links_tag` (`id`)
	)
###依赖

[django version:1.5.2](https://www.djangoproject.com/)

[django-registration:1.0](https://pypi.python.org/packages/source/d/django-registration/django-registration-1.0.tar.gz)

[feedparser](https://code.google.com/p/feedparser/) pip install feedparser

[OPML解析类](http://blog.donews.com/limodou/archive/2005/12/25/670385.aspx)

[steel-rumors](https://github.com/arocks/steel-rumors)

mysql-connector-python pip install mysql-connector-python

sinaweibopy pip install sinaweibopy

#未实现功能清单
* rss源的录入页面
* 根据tag进行分类（不同类型的link）
* 导入微博评论
* 用户收藏

#已经实现功能清单
* 用户注册、登陆
* 赞
* rss源的预输入
* url录入
* 评论
* 功能

#实现原理

排名算法

hacknews排名算法，Score = (P-1) / (T+2)^G其中，P = 文章获得的票数( -1 是去掉文章提交人的票)，T = 从文章提交至今的时间(小时)，G = 比重，news.arc里缺省值是1.8；随着时间的流逝，得分骤然下降。算法简单明了，顶，可以在每篇文章发生变化的时候更新一下分数。

#参照

1. [feweekly](http://www.feweekly.com/)
1. [hacknews](https://news.ycombinator.com/)
1. [steel-rumors](https://github.com/arocks/steel-rumors) 
1. [reddit](http://zh.reddit.com/) 
