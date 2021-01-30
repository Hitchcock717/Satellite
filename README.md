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

## 项目归属 / Owner
Satellite属于北京大学软件与微电子学院-计算机辅助翻译方向的工程实践评定成果，开发者为Hitchcock。

## 致谢 / Thanks
Satellite 的界面完全依赖于D2Admin框架。D2Admin使用最新的前端技术栈，小于 60kb 的本地首屏 js 加载，已经做好大部分项目前期准备工作，从而省去了许多从零起步的时间。另外界面组件遵循了许多ElementUI的设计风格，很好地融合了D2Admin框架。
在使用本平台前或打算二次开发，推荐先阅读[D2Admin官方文档](https://d2.pub/zh/)和[Element桌面端组件库](https://element.eleme.cn/#/zh-CN)，将会节省您的时间。

<a href="https://github.com/d2-projects/d2-admin" target="_blank"><img src="https://raw.githubusercontent.com/FairyEver/d2-admin/master/docs/image/d2-admin@2x.png" width="200"></a>

## 预览 / Preview
Satellite 暂未提供服务器部署的访问地址，或将选择在后续的版本中提供链接。如需快速了解本平台，请查阅下方GIF图片：
![Satellite演示](https://github.com/Hitchcock717/Satellite/blob/master/docs/introduction.gif)

## 演示 / Demonstration
视频演示地址：
[Youtube Satellite Scholar Research Platform](https://youtu.be/2PzagmhpOYg)

## 流程 / Flow
![Satellite 流程示意图](https://github.com/Hitchcock717/Satellite/blob/master/docs/flow.png)

## 模块 / Module
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

若存在大规模地爬取任务，平台内的爬虫引擎可另外使用[阿布云](https://www.abuyun.com/)提供的付费IP隧道，一键启动爬取。(Satellite 不作任何付费平台推介，如有付费需要，请务必自行考虑。）

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

相比简单搜索，子库搜索增加了以下限制条件：

| 搜索字段 | 格式 |
| --- | --- |
| 搜索类型 | Field |
| 论文信息1 | Text1 |
| 搜索关系 | 并含/或含/不含 |
| 论文信息2 | Text2 |
| 启用正则 | 是/否 |
| 相邻表达式关系 | 无/并且/或者/不含 |
| 日期 | Date |

其中，搜索类型Field包括以下字段：
- 标题
- 作者
- 机构/单位
- 来源
- 基金
- 关键词
- 摘要
其中，若检索表达式个数等于1时，**相邻表达式关系**选择”无“；否则依据实际需求选择。
其中，搜索类型、论文信息1、是否启用正则、相邻表达式关系均为必填项。

## 检索结果 / Result
Satellite 通常借助表格形式分页展示检索结果，用户可以自定义每页展示的数量。通过点击表格每行scope中的”详情”按钮，可以打开该篇论文的详情页。在详情页中，用户可以向项目自定义词表中添加意向关键词，也可以选择平台默认推荐关键词。对于心仪的文章，用户可以点击“收藏”按钮加入收藏夹中。
无论简单还是高级搜索结果，Satellite 均使用接口取数，所以对于数据量较大的情况用户需要耐心等待加载状态结束。

## 分析平台 / Analysis
Satellite 分析平台提供了两处分析入口：
* 智能预测分析
* 学术文献分析

## 智能预测 / Prediction
预测分析主要依赖于由清华大学计算机系研发的[Aminer](https://www.aminer.cn/)数据赋能平台提供的预测接口，在此特别向其致谢。
根据Aminer的[prediction_api](https://github.com/AMinerOpen/prediction_api)文档，Satellite 将预测分析方法分为以下三类：
* 标题分类预测
* 作者特征预测
* 专家推荐和研究方向预测
由于预测领域多倾向于人工智能，所以平台在测试完整性欠佳。若有兴趣体验，可按照如下提示输入文本：
> 对于标题分类

| 预测领域 | 预测信息 |
| --- | --- |
| 一般领域/AI领域 | Text/Keyword |

其中，一般领域需输入文本信息，如标题。参考样例：
```
基于多通道卷积神经网络的中文微博情感分析
```
AI领域需输入关键词。参考样例：
```
搜索引擎/Search Engine
```
预测接口内置了有道翻译接口，同时支持中英预测。
> 对于作者特征，在性别预测中，Aminer调用了旷视Face++接口，利用搜索引擎识别查找到的个人头像，因此对于预测知名人物，该方法更有效。

| 预测类型 | 
| --- |
| 性别 | 
| 身份 |
| 是否跳槽 |

各预测类型所需字段要求如下：
- 性别预测

| 预测字段 | 格式 |
| --- | --- |
| 姓名 | String |
| 单位 | String |
| 图片链接 | URL |

- 身份预测

| 预测字段 | 格式 |
| --- | --- |
| 论文发表数 | Int |
| 论文引用数 | Int |
| H-index | Int |
| G-index | Int |
| 年份范围 | Int |

[H-index](https://zh.wikipedia.org/wiki/H%E6%8C%87%E6%95%B0)的解释为：H指数的计算基于其研究者的论文数量及其论文被引用的次数。一个人在其所有学术文章中有N篇论文分别被引用了至少N次，他的H指数就是N.
[G-index](https://en.wikipedia.org/wiki/G-index)的解释为：G指数是根据给定研究人员的出版物收到的引用文献分布计算得出的，因此，如果给定一组文章，按其引用次数的降序排列，则g指数是唯一的最大数字， g篇文章至少获得g²引用。

- 工作变更预测

| 预测字段 | 格式 |
| --- | --- |
| 作者原单位 | String(可填多个，逗号分隔) |
| 返回预测数 | Int |

> 对于专家推荐和研究方向预测
- 专家推荐

| 预测字段 | 格式 |
| --- | --- |
| 推荐领域 | String |
| 推荐专家数 | INT |

- 研究方向预测

| 预测字段 | 格式 |
| --- | --- |
| 学者编号 | ID |

学者编号可在[Aminer学者库](https://www.aminer.cn/scikg)查询。

## 文献分析 / Literature
Satellite 学术文献分析平台提供了五种分析方法：
* 高频词分析
* 期刊发文量分析
* 主题分布分析
* 词间关系分析
* 作者合作关系分析
> 对于高频词分析，主要以词云图的形式来展示，分别涵盖了所选子库数据中的标题、关键词和摘要三个领域。

| 预测字段 | 格式 |
| --- | --- |
| 数据来源 | String(子库名称) |

> 对于期刊发文量分析，主要以饼图的形式来展示。

| 预测字段 | 格式 |
| --- | --- |
| 数据来源 | String(子库名称) |
| 日期范围 | Date |

> 对于主题分布分析，主要以条形图的形式来展示。

| 预测字段 | 格式 |
| --- | --- |
| 数据来源 | String(子库名称) |
| 主题数 | Int(1-10) |
| 主题词数 | Int(5/10/15) |

> 对于词间关系和作者合作关系分析，主要以关系图的形式来展示。

| 预测字段 | 格式 |
| --- | --- |
| 数据来源 | String(子库名称) |

- 以上基础图分析，主要依赖于[v-charts](https://v-charts.js.org/#/)插件包。v-charts是基于 Vue2.0 和 echarts 封装的 v-charts 图表组件，解决了使用 echarts 生成图表时，经常需要做繁琐的数据类型转化、修改复杂的配置项这一痛点。
- 以上关系图分析，主要依赖于[vis-network](https://github.com/visjs/vis-network)插件包。效果图样例如下：

![合作关系图](https://github.com/visjs/vis-network/blob/master/common-docs-files/img/network.png)


## 推荐平台 / Recommend
Satellite 通常基于文献元数据、用户收藏记录和用户个人信息综合考虑进行推荐，平台内以**每日推荐**的形式随机向用户展示5篇论文，平台外以**发送邮件**的形式定时向用户传输含推荐论文信息的附件。
平台推荐方法目前略显粗糙，后续将致力于打磨更精准、精细的推荐方法以飨用户。

## 版本号 / Version
- Scrapy1.7.4 or just Request
- Elasticsearch 7.6.1 & Kibana 7.6.1
- Django 3.0.4
- D2_admin(Vue) 1.8
- ...

## 快速查阅 / Reference
**About frontend**
- 暂时使用vue框架下的中后台管理系统d2_admin_smart_kit，后续根据需求更换
- 框架说明来自[d2_admin](https://d2.pub/zh/doc/d2-admin/component/container.html#%E6%A8%A1%E5%BC%8F-card)
- 页面组件来自[element-ui](https://element.eleme.cn/#/zh-CN/component/menu)
- icon来自[fontawesome](https://fontawesome.com)
- ...

**About backend**
- Django教程来自[刘江的博客](https://www.liujiangblog.com/course/django/2)
- Django DRF框架来自[django-restful-framework](https://q1mi.github.io/Django-REST-framework-documentation/tutorial/2-requests-and-responses_zh)
- ...

**About Vue & Django**
- [掘金文章](https://juejin.im/post/5e36d5dc51882520ea398f21)
- [知乎文章](https://zhuanlan.zhihu.com/p/54776124)
- ...

**About Scrapy & Django**
- [Scrapy官方文档](https://scrapy-chs.readthedocs.io/zh_CN/0.24/topics/djangoitem.html)
- [Theodo Blog](https://blog.theodo.com/2019/01/data-scraping-scrapy-django-integration/)
- ...

**About Elasticsearch & Django**
- [CSDN Blog](https://blog.csdn.net/weixin_42149982/article/details/82390900)
- [简书](https://www.jianshu.com/p/46eb88a4e489)
- ...

## 写在最后 / Final
- Satellite 1.0版本历时一个半月断断续续独立开发而成，总会有许多细节不甚完善或功能不甚全面或bug出现的情况，相信经过逐步改进后能够实现真正的”快速检索“ + ”全面分析“ + “好文推荐”。若出现以上所提到的不足之处，望多提宝贵意见和issue。
- 祝好，各位。





