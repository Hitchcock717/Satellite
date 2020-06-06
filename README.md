![banner](https://raw.githubusercontent.com/Hitchcock717/Satellite/master/docs/logos.png)

<p align="center">
	<a href="https://github.com/Hitchcock717/Satellite/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite/network/members" target="_blank"><img src="https://img.shields.io/github/forks/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite/issues" target="_blank"><img src="https://img.shields.io/github/issues/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite/issues?q=is%3Aissue+is%3Aclosed" target="_blank"><img src="https://img.shields.io/github/issues-closed/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite/pulls" target="_blank"><img src="https://img.shields.io/github/issues-pr/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite/pulls?q=is%3Apr+is%3Aclosed" target="_blank"><img src="https://img.shields.io/github/issues-pr-closed/Hitchcock717/Satellite.svg"></a>
	<a href="https://github.com/Hitchcock717/Satellite" target="_blank"><img src="https://img.shields.io/github/last-commit/Hitchcock717/Satellite.svg"></a>
</p>

[Satellite](https://github.com/Hitchcock717/Satellite) 是一个简易型的**科研雷达**平台，该平台致力于模拟检索、分析并推荐精细化领域下的中文论文数据。前端框架基于[D2Admin](https://github.com/d2-projects/d2-admin)集成方案，后端采用[Django](https://github.com/django/django)框架，搭载[Elasticsearch](https://github.com/elastic/elasticsearch)开源搜索引擎，通过实时爬取诸如[知网](http://search.cnki.com.cn/Search/Result?searchType=MultiyTermsSearch&Content=%E6%B0%A8%E5%9F%BA%E9%85%B8&Order=1)等文献数据平台，完成平台功能展示。

## 致谢
Satellite 的界面完全依赖于D2Admin框架。D2Admin使用最新的前端技术栈，小于 60kb 的本地首屏 js 加载，已经做好大部分项目前期准备工作，从而省去了许多从零起步的时间。另外界面组件遵循了许多ElementUI的设计风格，很好地融合了D2Admin框架。
在使用本平台前或打算二次开发，推荐先阅读[D2Admin官方文档](https://d2.pub/zh/)和[Element桌面端组件库](https://element.eleme.cn/#/zh-CN)，将会节省您的时间。
``` html
<a href="https://github.com/d2-projects/d2-admin" target="_blank"><img src="https://raw.githubusercontent.com/FairyEver/d2-admin/master/docs/image/d2-admin@2x.png" width="200"></a>
```

## 预览
Satellite 暂未提供服务器部署的访问地址，或将选择在后续的版本中提供链接。如需快速了解本平台，请点击下方GIF图片：
![Satellite演示](https://github.com/Hitchcock717/Satellite/blob/master/docs/introduction.gif)

## 模块
Satellite 按功能属性主要分为：
* 检索平台
* 分析平台
* 推荐平台
* 项目仓库
* 收藏夹
* 个人中心

## 个人信息 / Profile
Satellite 要求首次登录用户需完善个人信息，填写入口可在**个人中心**或**检索平台欢迎页**找到。
由于个人信息可作为推荐依据的重要一环，所以请务必准确输入各项信息。
保存个人信息后，再次进入**个人中心**页面时信息将会保留至上次填写状态，方便用户随时修改。

## 项目 / Project
用户自建项目是使用 Satellite 检索平台的第一步，也是用户每次检索历史的记录。整个 Satellite 项目仓库将按项目进度分为：
* 待办项目
* 已完成项目
待办项目指在平台内数据库无任何搜索结果或只含少量结果，将启动平台爬虫引擎爬取的检索项目。当爬取结束，并且新数据存入Elasticsearch引擎时，平台将会自动为用户发送邮件提醒。用户可按照邮件内容的指引，确定待办项目名称和检索词汇，重新登录平台后在**项目仓库 --- 待办项目**处点击详情一键开启检索进程。

## 爬虫 / Spider
Satellite 内嵌了小型检索平台，平台数据来自文献平台爬虫。需说明的是：平台内定制的爬虫引擎，目前只作为演示使用，爬取规模与速度尚不能满足实际项目需要。
| 数据来源 | 地址 | 爬虫名称 |
| --- | --- | --- |
| 知网 | [知网空间](http://search.cnki.com.cn/Search/Result?searchType=MultiyTermsSearch&Content=%E6%B0%A8%E5%9F%BA%E9%85%B8&Order=1) | CNKIspider |
| 维普 | [维普中文期刊](http://qikan.cqvip.com/Qikan/Search/Index?from=Qikan_Search_Index) | CQVIPspider |
| 万方 | [万方智搜](http://www.wanfangdata.com.cn/index.html) | WFspider |
若存在大规模地爬取任务，平台内的爬虫引擎可另外使用[阿布云](https://www.abuyun.com/)提供的付费IP隧道，一键启动爬取。(Satellite 不作任何付费平台推介，如有付费需要，请务必自行考虑后选择。）

## 检索平台 / Retrieve
Satellite 检索平台按检索方式分为：
* 论文信息检索
* 上传词表检索
论文信息检索包括论文关键词和论文标题两部分。若使用标题作为检索条件，Satellite 会启用关键词提取功能，供用户选择意向词汇。无论选择哪种检索方式，Satellite 都会为用户推荐相似词汇，待用户筛选完毕一起加入待检索集合。
上传词表检索需要用户提供合适格式的文本文件(.txt格式)，平台将会显示文件中的关键词。文件格式应以换行符为界，一行一词。样例如下：
```
关键词1
关键词2
关键词3
...
```

## 论文子库 / Subrepo
Satellite 检索平台按检索结果又分为：
* 简单检索
* 高级检索
简单检索即为用户首次输入检索条件后获取的检索结果。
高级检索，又称子库检索。子库是Satellite 平台用于区分用户粗略搜索而创建的概念，表明在粗搜的基础上进一步明确意向搜索结果。子库保存了用户精细搜索后的结果，作为后续分析平台的数据源，代表项目中最有价值的数据。




