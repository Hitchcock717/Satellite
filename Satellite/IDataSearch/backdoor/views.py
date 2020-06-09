import re
import ast
import requests
import json
from .utils import ExtractAndRecommend, GetRawResult, GetDetailResult

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .models import Message, Uploadcorpus, Extractor, Recommend, Simplesearch, Detailsearch, Temp, Folder, Collection, Repository, Corpus, Filerepo, Pending, Project, Projectinfo, Personal, MessageSerializer, UploadcorpusSerializer, ExtractorSerializer, RecommendSerializer, SimplesearchSerializer, DetailsearchSerializer, TempSerializer, FolderSerializer, CollectionSerializer, RepositorySerializer, CorpusSerializer, FilerepoSerializer, PendingSerializer, ProjectSerializer, ProjectinfoSerializer, PersonalSerializer


@api_view(('POST', 'GET',))
def scrapy(request):
    if request.method == 'POST':

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        scrapy_dict = ast.literal_eval(raw_dict_key)
        print(scrapy_dict)

        extractors = scrapy_dict['extractors']
        recommends = scrapy_dict['recommends']

        keywords = []
        from backdoor.main import cnki_main, cqvip_main, wf_main
        data = Projectinfo.objects.last()
        source = model_to_dict(data)['source'].split(',')
        project = model_to_dict(data)['project']
        extract = model_to_dict(data)['extract'].split(',')
        recommend = model_to_dict(data)['recommend'].split(',')
        keywords.extend(extract)
        keywords.extend(recommend)
        for k in keywords:
            if k == '':
                keywords.remove(k)
        print(keywords)

        if not Pending.objects.filter(project=project):
            pend = Pending(project=project, extract=extractors, recommend=recommends)
            pend.save()
        else:
            print('待办项目已存在!')

        # ****** 自此开始, 根据source字段启动相应爬虫 ****** #

        if len(source) == 1:
            if source[0] == '知网':
                for word in keywords:
                    cnki_main(word)
            elif source[0] == '维普':
                for word in keywords:
                    cqvip_main(word)
            else:
                for word in keywords:
                    wf_main(word)

        elif len(source) == 2:
            if re.search('知网,维普', model_to_dict(data)['source']):
                for word in keywords:
                    cnki_main(word)
                    cqvip_main(word)
            elif re.search('维普,万方', model_to_dict(data)['source']):
                for word in keywords:
                    cqvip_main(word)
                    wf_main(word)
            else:
                for word in keywords:
                    cnki_main(word)
                    wf_main(word)

        else:
            for word in keywords:
                cnki_main(word)
                cqvip_main(word)
                wf_main(word)

        # ****** 截此为止, 数据已插入ES中 ****** #

        # ****** 自动发送邮件 ****** #
        from backdoor.gmail import SendMail
        SendMail().automatic_send_email(project, keywords)

        return Response('待办项目已完成!')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def extract(request):

    latest = Message.objects.last()
    raw_dict = model_to_dict(latest)
    print(raw_dict)

    serializer_context = {
        'request': request,
    }

    base_router = 'http://127.0.0.1:8000/api/extract/'

    extractors = []
    extractors_group = []

    db = 'extractor'
    raw_temps = Temp.objects.filter(record_db=db)
    print(raw_temps)

    if raw_temps:
        temps = []
        for raw_temp in raw_temps:  # 最新的extractor id
            raw_temp_dict = model_to_dict(raw_temp)
            temps.append(raw_temp_dict)
        temp_dict = temps[-1]
        print(temp_dict)
        pre_id = temp_dict['record_id']
        post_id = raw_dict['id']  # 更新id
        temp = Temp(record_id=post_id, record_db=db)
        temp.save()

        updates = Message.objects.filter(id__gt=pre_id)
        print(updates)
        for update in updates:
            update_dict = model_to_dict(update)
            ex = ExtractAndRecommend()
            extr_kws = ex.extract_kws(update_dict)

            for kws in extr_kws:
                extr = Extractor(originkws=kws)
                extr.save()

                # retrieve kws
                data = Extractor.objects.filter(originkws=kws)

                raw_d_dict = []
                for d in data:
                    d_dict = model_to_dict(d)
                    raw_d_dict.append(d_dict)

                set_only = []
                set_only.append(raw_d_dict[0])

                # drop reqeated
                for item in raw_d_dict:
                    k = 0
                    for iitem in set_only:
                        if item['originkws'] != iitem['originkws']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)
                for only in set_only:
                    pkid = only['id']
                    extractor = ExtractorSerializer(data=only, context=serializer_context)
                    if extractor.is_valid():
                        ordered_li = extractor.validated_data
                        ordered_li['pk'] = pkid
                        ordered_li['url'] = base_router + str(pkid) + '/'
                        ordered_li = dict(ordered_li)
                        extractors.append(ordered_li)

                if extractors is not None:
                    extractors.sort(key=lambda x: (x['pk']), reverse=False)
                    extractors_group.extend(extractors)
                    extractors.clear()
                else:
                    print('The extractors are empty!')

        try:
            if extractors_group is not None:
                print(extractors_group)
                return Response(extractors_group)
        except Exception as e:
            return Response('None extracted objects!')

    else:
        pre_id = raw_dict['id']
        print(pre_id)
        temp = Temp(record_id=pre_id, record_db=db)
        temp.save()

        updates = Message.objects.all()
        print(updates)
        for update in updates:
            update_dict = model_to_dict(update)
            ex = ExtractAndRecommend()
            extr_kws = ex.extract_kws(update_dict)

            for kws in extr_kws:
                extr = Extractor(originkws=kws)
                extr.save()

                # retrieve kws
                data = Extractor.objects.filter(originkws=kws)

                raw_d_dict = []
                for d in data:
                    d_dict = model_to_dict(d)
                    raw_d_dict.append(d_dict)

                set_only = []
                set_only.append(raw_d_dict[0])

                # drop reqeated
                for item in raw_d_dict:
                    k = 0
                    for iitem in set_only:
                        if item['originkws'] != iitem['originkws']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)

                for only in set_only:
                    pkid = only['id']
                    extractor = ExtractorSerializer(data=only, context=serializer_context)
                    if extractor.is_valid():
                        ordered_li = extractor.validated_data
                        ordered_li['pk'] = pkid
                        ordered_li['url'] = base_router + str(pkid) + '/'
                        ordered_li = dict(ordered_li)
                        extractors.append(ordered_li)

                if extractors is not None:
                    extractors.sort(key=lambda x: (x['pk']), reverse=False)
                    extractors_group.extend(extractors)
                    extractors.clear()
                else:
                    print('The extractors are empty!')

        try:
            if extractors_group is not None:
                print(extractors_group)
                return Response(extractors_group)
        except Exception as e:
            return Response('None extracted objects!')


@api_view(('GET',))
def recommend(request):

    latest = Message.objects.last()
    raw_dict = model_to_dict(latest)

    serializer_context = {
        'request': request,
    }

    base_router = 'http://127.0.0.1:8000/api/recommend/'

    recommends = []
    recommends_group = []

    db = 'recommend'
    raw_temps = Temp.objects.filter(record_db=db)

    if raw_temps:
        temps = []
        for raw_temp in raw_temps:
            raw_temp_dict = model_to_dict(raw_temp)
            temps.append(raw_temp_dict)
        temp_dict = temps[-1]
        pre_id = temp_dict['record_id']
        post_id = raw_dict['id']
        temp = Temp(record_id=post_id, record_db=db)
        temp.save()

        updates = Message.objects.filter(id__gt=pre_id)
        print(updates)
        for update in updates:
            update_dict = model_to_dict(update)

            ex = ExtractAndRecommend()
            recom_kws = ex.recommend_kws(update_dict)

            try:
                if recom_kws:
                    for rkws in recom_kws:
                        recom = Recommend(recommendkws=rkws)
                        recom.save()

                        # retrieve kws
                        data = Recommend.objects.filter(recommendkws=rkws)

                        raw_d_dict = []
                        for d in data:
                            d_dict = model_to_dict(d)
                            raw_d_dict.append(d_dict)

                        set_only = []
                        set_only.append(raw_d_dict[0])

                        # drop reqeated
                        for item in raw_d_dict:
                            k = 0
                            for iitem in set_only:
                                if item['recommendkws'] != iitem['recommendkws']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)

                        for only in set_only:
                            pkid = only['id']
                            recommend = RecommendSerializer(data=only, context=serializer_context)
                            if recommend.is_valid():
                                ordered_li = recommend.validated_data
                                ordered_li['pk'] = pkid
                                ordered_li['url'] = base_router + str(pkid) + '/'
                                ordered_li = dict(ordered_li)
                                recommends.append(ordered_li)

                        if recommends:
                            recommends.sort(key=lambda x: (x['pk']), reverse=False)
                            recommends_group.extend(recommends)
                            recommends.clear()
                        else:
                            print('The recommends are empty!')
            except Exception as e:
                return Response(['暂无推荐'])

        try:
            return Response(recommends_group)
        except Exception as e:
            return Response(['暂无推荐'])

    else:
        pre_id = raw_dict['id']
        print(pre_id)
        temp = Temp(record_id=pre_id, record_db=db)
        temp.save()

        updates = Message.objects.all()
        print(updates)
        for update in updates:
            update_dict = model_to_dict(update)
            ex = ExtractAndRecommend()
            recom_kws = ex.recommend_kws(update_dict)

            try:
                if recom_kws:
                    for rkws in recom_kws:
                        recom = Recommend(recommendkws=rkws)
                        recom.save()

                        # retrieve kws
                        data = Recommend.objects.filter(recommendkws=rkws)

                        raw_d_dict = []
                        for d in data:
                            d_dict = model_to_dict(d)
                            raw_d_dict.append(d_dict)

                        set_only = []
                        set_only.append(raw_d_dict[0])

                        # drop reqeated
                        for item in raw_d_dict:
                            k = 0
                            for iitem in set_only:
                                if item['recommendkws'] != iitem['recommendkws']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)

                        for only in set_only:
                            pkid = only['id']
                            recommend = RecommendSerializer(data=only, context=serializer_context)
                            if recommend.is_valid():
                                ordered_li = recommend.validated_data
                                ordered_li['pk'] = pkid
                                ordered_li['url'] = base_router + str(pkid) + '/'
                                ordered_li = dict(ordered_li)
                                recommends.append(ordered_li)

                        if recommends is not None:
                            recommends.sort(key=lambda x: (x['pk']), reverse=False)
                            recommends_group.extend(recommends)
                            recommends.clear()
                        else:
                            print('The recommends are empty!')
            except Exception as e:
                return Response(['暂无推荐'])

        try:
            return Response(recommends_group)
        except Exception as e:
            return Response(['暂无推荐'])


@api_view(('DELETE','GET',))
def deletextract(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        extract_dict = ast.literal_eval(raw_dict_key)

        delete_id = extract_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            print('1')
            get_object_or_404(Extractor, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deleterecommend(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        recommend_dict = ast.literal_eval(raw_dict_key)

        delete_id = recommend_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            get_object_or_404(Recommend, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


# 承接前台upload组件action路径
# 不作实际操作
@api_view(('POST', 'GET',))
def mockupload(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.FILES.keys(), request.FILES.values()))
        corpus_name = raw_dict['file']
        print(corpus_name)
        return Response('Saved')

    if request.method == 'GET':
        return Response('No method!')


# 处理前台解析后的词表数据
@api_view(('POST', 'GET',))
def parseupload(request):

    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/extract/'

        # 包含抽取词和推荐词的列表
        total = []

        extractors = []
        extractors_group = []

        recommends = []
        recommends_group = []

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        upload_dict = ast.literal_eval(raw_dict_key)
        print(upload_dict)

        raw_upload_data = upload_dict['content']
        upload_name = upload_dict['name']
        print(upload_name)

        up = Uploadcorpus(corpus_name=upload_name, corpus_kws=raw_upload_data)
        up.save()

        upload_data = raw_upload_data.split('\n')
        print(upload_data)
        ex = ExtractAndRecommend()
        extract_data = upload_data
        recommend_data = ex.recommend_upload_kws(upload_data)

        # ********************************************************* #
        # 有推荐数据
        if recommend_data:

            # ********************************************************* #
            # 存储清洗抽取词/词表内词汇
            for kws in extract_data:
                extr = Extractor(originkws=kws)
                extr.save()

                # retrieve kws
                data = Extractor.objects.filter(originkws=kws)

                raw_d_dict = []
                for d in data:
                    d_dict = model_to_dict(d)
                    raw_d_dict.append(d_dict)

                set_only = []
                set_only.append(raw_d_dict[0])

                # drop reqeated
                for item in raw_d_dict:
                    k = 0
                    for iitem in set_only:
                        if item['originkws'] != iitem['originkws']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)

                for only in set_only:
                    pkid = only['id']
                    extractor = ExtractorSerializer(data=only, context=serializer_context)
                    if extractor.is_valid():
                        ordered_li = extractor.validated_data
                        ordered_li['pk'] = pkid
                        ordered_li['url'] = base_router + str(pkid) + '/'
                        ordered_li = dict(ordered_li)
                        extractors.append(ordered_li)

                extractors.sort(key=lambda x: (x['pk']), reverse=False)
                extractors_group.extend(extractors)
                extractors.clear()

            # ********************************************************* #
            # 存储清洗推荐词
            for rkws in recommend_data:
                recom = Recommend(recommendkws=rkws)
                recom.save()

                # retrieve kws
                data = Recommend.objects.filter(recommendkws=rkws)

                raw_d_dict = []
                for d in data:
                    d_dict = model_to_dict(d)
                    raw_d_dict.append(d_dict)

                set_only = []
                set_only.append(raw_d_dict[0])

                # drop reqeated
                for item in raw_d_dict:
                    k = 0
                    for iitem in set_only:
                        if item['recommendkws'] != iitem['recommendkws']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)

                for only in set_only:
                    pkid = only['id']
                    recommend = RecommendSerializer(data=only, context=serializer_context)
                    if recommend.is_valid():
                        ordered_li = recommend.validated_data
                        ordered_li['pk'] = pkid
                        ordered_li['url'] = base_router + str(pkid) + '/'
                        ordered_li = dict(ordered_li)
                        recommends.append(ordered_li)

                recommends.sort(key=lambda x: (x['pk']), reverse=False)
                recommends_group.extend(recommends)
                recommends.clear()

            try:
                if extractors_group and recommends_group:
                    total.append(extractors_group)
                    total.append(recommends_group)
                    print(total)
                    return Response(total)

                else:
                    return Response('failed')

            except Exception as e:
                return Response('failed')

        # 无推荐词汇, 只返回抽取词即可(一般若无推荐词, 会随机推荐, 此处防止意外)
        else:
            print('The recommends are empty')
            # ********************************************************* #
            # 存储清洗抽取词/词表内词汇
            for kws in extract_data:
                extr = Extractor(originkws=kws)
                extr.save()

                # retrieve kws
                data = Extractor.objects.filter(originkws=kws)

                raw_d_dict = []
                for d in data:
                    d_dict = model_to_dict(d)
                    raw_d_dict.append(d_dict)

                set_only = []
                set_only.append(raw_d_dict[0])

                # drop reqeated
                for item in raw_d_dict:
                    k = 0
                    for iitem in set_only:
                        if item['originkws'] != iitem['originkws']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)

                for only in set_only:
                    pkid = only['id']
                    extractor = ExtractorSerializer(data=only, context=serializer_context)
                    if extractor.is_valid():
                        ordered_li = extractor.validated_data
                        ordered_li['pk'] = pkid
                        ordered_li['url'] = base_router + str(pkid) + '/'
                        ordered_li = dict(ordered_li)
                        extractors.append(ordered_li)

                extractors.sort(key=lambda x: (x['pk']), reverse=False)
                extractors_group.extend(extractors)
                extractors.clear()

            try:
                if extractors_group:
                    total.append(extractors_group)
                    print(total)
                    return Response(total)

                else:
                    return Response('failed')

            except Exception as e:
                return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST', 'GET',))
def startspider(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        spider_dict = ast.literal_eval(raw_dict_key)
        print(spider_dict)
        print(spider_dict['recommends'])
        # spider_names = spider_dict['spiders']

        # 转义符处理
        drop_slash_extractors = re.sub('\\\\*', '', spider_dict['extractors'])
        drop_quotation_extractors = re.sub('^"|"$', '', drop_slash_extractors)
        spider_extractors = ast.literal_eval(drop_quotation_extractors.strip(']['))  # tuple
        extractors, recommends, search_keywords = [], [], []

        if isinstance(spider_extractors, tuple):
            for extractors_dict in spider_extractors:
                extracted_words = extractors_dict['originkws']
                extractors.append(extracted_words)
        else:
            extracted_words = spider_extractors['originkws']
            extractors.append(extracted_words)
        search_keywords.extend(extractors)

        if spider_dict['recommends'] != '"[]"' and spider_dict['recommends'] != '[]':
            drop_slash_recommends = re.sub('\\\\*', '', spider_dict['recommends'])
            drop_quotation_recommends = re.sub('^"|"$', '', drop_slash_recommends)
            spider_recommends = ast.literal_eval(drop_quotation_recommends.strip(']['))
            if isinstance(spider_recommends, tuple):
                for recommends_dict in spider_recommends:
                    recommend_words = recommends_dict['recommendkws']
                    recommends.append(recommend_words)
            else:
                recommend_words = spider_recommends['recommendkws']
                recommends.append(recommend_words)
            search_keywords.extend(recommends)
        else:
            print('暂无推荐词')

        keywords = list(set(search_keywords))
        print(keywords)

        new_keywords = []

        # 匹配检索表达式1
        if len(keywords) < 2:
            new_keywords.append(keywords[0])
        else:
            for word in keywords[:-2]:
                new_word = word + ' OR '
                new_keywords.append(new_word)
            new_keywords.append(keywords[-1])

        query = ''.join(new_keywords)

        sum_count = 0
        sum_doc = []

        # 爬虫字段存储
        queries = []  # 结构复杂，前台暂无法解析 --- {'query': {'multi_match': {'query': '氨基酸', 'fields': ['abstract', 'kws', 'title', 'info', 'fund', 'source']}}}
        # title, author, source, info, date, kws, fund, abstract, cited, downed, download = [], [], [], [], [], [], [], [], [], [], []
        for word in keywords:
            raw_search_result = GetRawResult()
            # 匹配检索表达式2
            query_body = raw_search_result.get_raw_result(word)[0]  # {}
            queries.append(query_body)

            word_count = raw_search_result.get_raw_result(word)[1]
            sum_count += word_count

            word_doc = raw_search_result.get_raw_result(word)[2]  # [{}]
            sum_doc.extend(word_doc)  # [{}]

        set_only = []
        set_only.append(sum_doc[0])

        # drop reqeated
        for item in sum_doc:
            k = 0
            for iitem in set_only:
                if item['title'] != iitem['title']:
                    k += 1
                else:
                    break

                if k == len(set_only):
                    set_only.append(item)  # [{no repeated}]

        # 过滤后的搜索结果数
        filter_count = len(set_only)

        for each_word_doc in set_only:

            title = each_word_doc['title']
            author = each_word_doc['author']
            if re.search(';', author):
                author = re.sub(';', '', author)
            source = each_word_doc['source']
            info = each_word_doc['info']
            date = each_word_doc['date']
            kws = each_word_doc['kws']
            if kws == 'nan':
                kws = '暂无'
            fund = each_word_doc['fund']
            if fund == 'nan':
                fund = '暂无'
            abstract = each_word_doc['abstract']
            cited = each_word_doc['cited'].rstrip('.0')
            if cited == 'nan':
                cited = '0'

            downed = each_word_doc['downed'].rstrip('.0')
            if downed == 'nan':
                downed = '0'
            download = each_word_doc['download']

            sim = Simplesearch(title=title, author=author, source=source, info=info, date=date, kws=kws, fund=fund,
                               abstract=abstract, cited=cited, downed=downed, download=download)
            sim.save()

        data = {
            'keywords': keywords,
            'query': query,
            'raw_search_count': sum_count,
            'filter_search_count': filter_count
        }

        # 暂时指定idata，后续增加引擎
        # for name in spider_names:
            # for word in keywords:
                # execute_spider(name, word)
                # subprocess.check_output(['scrapy', 'crawl', name, '-a', 'keyword='+word])

        if filter_count > 50:  # 阈值根据es数据量设置
            return Response(data)
        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def rawresult(request):
    if request.method == 'GET':

        latest = Simplesearch.objects.last()
        raw_dict = model_to_dict(latest)

        db = 'rawresult'
        raw_temps = Temp.objects.filter(record_db=db)

        if raw_temps:
            temps = []
            for raw_temp in raw_temps:
                raw_temp_dict = model_to_dict(raw_temp)
                temps.append(raw_temp_dict)
            temp_dict = temps[-1]
            pre_id = temp_dict['record_id']
            post_id = raw_dict['id']
            temp = Temp(record_id=post_id, record_db=db)
            temp.save()

            updates = Simplesearch.objects.filter(id__gt=pre_id)
            # updates = Simplesearch.objects.all()[:50]  # for test

            rawresults = []
            # 自增序号刷新【前端改】
            # uid = 1
            for update in updates:
                update_dict = model_to_dict(update)
                # update_dict['id'] = str(uid)
                # uid += 1

                rawresults.append(update_dict)

            if rawresults is not None:
                print(rawresults)
                data = {
                    'record_id': pre_id,
                    'result': rawresults
                }
                return Response(data)
            else:
                return Response('No suitable data!')

        else:
            pre_id = raw_dict['id']
            print(pre_id)
            temp = Temp(record_id=pre_id, record_db=db)
            temp.save()

            updates = Simplesearch.objects.all()
            # updates = Simplesearch.objects.all()[:20]  # for test

            rawresults = []
            # 自增序号刷新【前端改】
            # uid = 1
            for update in updates:
                update_dict = model_to_dict(update)
                # update_dict['id'] = str(uid)
                # uid += 1

                rawresults.append(update_dict)

            if rawresults is not None:
                print(rawresults)
                data = {
                    'record_id': '0',
                    'result': rawresults
                }
                return Response(data)
            else:
                return Response('No suitable data!')


@api_view(('POST', 'GET',))
def getrecordrawId(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        id_dict = ast.literal_eval(raw_dict_key)
        record_id = int(id_dict['record_id'].strip('"'))

        # 按前台存储id查找
        if record_id == '0':
            results = []
            updates = Simplesearch.objects.all()
            for update in updates:
                update_dict = model_to_dict(update)
                results.append(update_dict)

            if results:
                print(results)
                data = {
                    'record_id': '0',  # 首次检索
                    'result': results
                }
                return Response(data)
            else:
                return Response('No suitable data!')

        else:
            pre_id = record_id
            results = []

            updates = Simplesearch.objects.filter(id__gt=pre_id)
            for update in updates:
                update_dict = model_to_dict(update)

                results.append(update_dict)

            if results is not None:
                print(results)
                data = {
                    'record_id': pre_id,
                    'result': results
                }
                return Response(data)
            else:
                return Response('No suitable data!')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST', 'GET',))
def selectedrawresult(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        target_dict = ast.literal_eval(raw_dict_key)
        target_id = int(target_dict['target'].strip('"'))

        # 按对应id查找
        target_data = Simplesearch.objects.filter(id=target_id)
        for data in target_data:
            clean_data = model_to_dict(data)

            return Response(clean_data)

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST', 'GET',))
def getexpression(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        expression_dict = ast.literal_eval(raw_dict_key)
        print(expression_dict)

        subrepo_name = expression_dict['name']
        subrepo_intro = expression_dict['introduction']
        raw_expression_body = expression_dict['expression']
        expression_body = ast.literal_eval(raw_expression_body.strip(']['))
        print(expression_body)

        # 有无日期筛选
        expression_date = expression_body[-1]
        start_date = expression_date['startdate']
        end_date = expression_date['endate']

        # 无有效日期
        if start_date == 'null' or end_date == 'null':
            # 1.有且仅有一个表达式
            if len(expression_body) == 2:
                expression_context = expression_body[0]

                # 转换成ES中的字段
                if expression_context['type'] == '标题':
                    expression_context['type'] = 'title'
                elif expression_context['type'] == '作者':
                    expression_context['type'] = 'author'
                elif expression_context['type'] == '来源':
                    expression_context['type'] = 'source'
                elif expression_context['type'] == '机构/单位':
                    expression_context['type'] = 'info'
                elif expression_context['type'] == '基金':
                    expression_context['type'] = 'fund'
                elif expression_context['type'] == '关键词':
                    expression_context['type'] = 'kws'
                elif expression_context['type'] == '摘要':
                    expression_context['type'] = 'abstract'

                # 1.1 有且仅有必填项 关键词+单字段
                if not expression_context.get('relation'):
                    # 1.1.1 无正则
                    if expression_context['regex'] == '否':
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']

                        detail = GetDetailResult()
                        results = detail.get_only_expression(expression_type, expression_info)
                        print(results)

                        sum_doc = results[2]
                        set_only = []
                        set_only.append(sum_doc[0])

                        # drop reqeated
                        for item in sum_doc:
                            k = 0
                            for iitem in set_only:
                                if item['title'] != iitem['title']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)  # [{no repeated}]

                        # 过滤后的搜索结果数
                        filter_count = len(set_only)

                        # 清洗字段
                        for each_word_doc in set_only:

                            title = each_word_doc['title']
                            author = each_word_doc['author']
                            if re.search(';', author):
                                author = re.sub(';', '', author)
                            source = each_word_doc['source']
                            info = each_word_doc['info']
                            date = each_word_doc['date']
                            kws = each_word_doc['kws']
                            if kws == 'nan':
                                kws = '暂无'
                            fund = each_word_doc['fund']
                            if fund == 'nan':
                                fund = '暂无'
                            abstract = each_word_doc['abstract']
                            cited = each_word_doc['cited'].rstrip('.0')
                            if cited == 'nan':
                                cited = '0'

                            downed = each_word_doc['downed'].rstrip('.0')
                            if downed == 'nan':
                                downed = '0'
                            download = each_word_doc['download']

                            det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                               kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                               download=download, name=subrepo_name, introduction=subrepo_intro)
                            det.save()

                        data = {
                            'query': results[0],
                            'raw_count': results[1],
                            'filter_search_count': filter_count
                        }
                        print(data)
                        return Response(data)

                    # 1.1.2 有正则
                    else:
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']

                        detail = GetDetailResult()
                        results = detail.get_only_expression_with_regexp(expression_type, expression_info)

                        sum_doc = results[2]
                        set_only = []
                        set_only.append(sum_doc[0])

                        # drop reqeated
                        for item in sum_doc:
                            k = 0
                            for iitem in set_only:
                                if item['title'] != iitem['title']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)  # [{no repeated}]

                        # 过滤后的搜索结果数
                        filter_count = len(set_only)

                        # 清洗字段
                        for each_word_doc in set_only:

                            title = each_word_doc['title']
                            author = each_word_doc['author']
                            if re.search(';', author):
                                author = re.sub(';', '', author)
                            source = each_word_doc['source']
                            info = each_word_doc['info']
                            date = each_word_doc['date']
                            kws = each_word_doc['kws']
                            if kws == 'nan':
                                kws = '暂无'
                            fund = each_word_doc['fund']
                            if fund == 'nan':
                                fund = '暂无'
                            abstract = each_word_doc['abstract']
                            cited = each_word_doc['cited'].rstrip('.0')
                            if cited == 'nan':
                                cited = '0'

                            downed = each_word_doc['downed'].rstrip('.0')
                            if downed == 'nan':
                                downed = '0'
                            download = each_word_doc['download']

                            det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                               kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                               download=download, name=subrepo_name, introduction=subrepo_intro)
                            det.save()

                        data = {
                            'query': results[0],
                            'raw_count': results[1],
                            'filter_search_count': filter_count
                        }
                        print(data)
                        return Response(data)

                # 1.2 不止必填项 多关键字+单字段
                else:
                    # 1.2.1 无正则
                    if expression_context['regex'] == '否':
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']
                        expression_relation = expression_context['relation']
                        expression_otherinfo = expression_context['otherinfo']

                        detail = GetDetailResult()

                        if expression_relation == '并含':
                            in_method = '1'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '或含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '不含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = expression_type
                            exclude_kws = expression_otherinfo
                            results = detail.get_only_relation_expression(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                    # 1.2.2 有正则
                    else:
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']
                        expression_relation = expression_context['relation']
                        expression_otherinfo = expression_context['otherinfo']

                        detail = GetDetailResult()

                        if expression_relation == '并含':
                            in_method = '1'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_regexp(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '或含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_regexp(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '不含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = expression_type
                            exclude_kws = expression_otherinfo
                            results = detail.get_only_relation_expression_with_regexp(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

            # 2.多个表达式
            else:
                new_expression_body = []
                print(expression_body[:-1])
                for expression_context in expression_body[:-1]:
                    # 转换成ES中的字段
                    if expression_context['type'] == '标题':
                        expression_context['type'] = 'title'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '作者':
                        expression_context['type'] = 'author'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '来源':
                        expression_context['type'] = 'source'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '机构/单位':
                        expression_context['type'] = 'info'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '基金':
                        expression_context['type'] = 'fund'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '关键词':
                        expression_context['type'] = 'kws'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '摘要':
                        expression_context['type'] = 'abstract'
                        new_expression_body.append(expression_context)

                print('元数据:' + str(new_expression_body))
                detail = GetDetailResult()
                results = detail.get_multiple_expression(new_expression_body)

                sum_doc = results[2]
                set_only = []
                set_only.append(sum_doc[0])

                # drop reqeated
                for item in sum_doc:
                    k = 0
                    for iitem in set_only:
                        if item['title'] != iitem['title']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)  # [{no repeated}]

                # 过滤后的搜索结果数
                filter_count = len(set_only)

                # 清洗字段
                for each_word_doc in set_only:

                    title = each_word_doc['title']
                    author = each_word_doc['author']
                    if re.search(';', author):
                        author = re.sub(';', '', author)
                    source = each_word_doc['source']
                    info = each_word_doc['info']
                    date = each_word_doc['date']
                    kws = each_word_doc['kws']
                    if kws == 'nan':
                        kws = '暂无'
                    fund = each_word_doc['fund']
                    if fund == 'nan':
                        fund = '暂无'
                    abstract = each_word_doc['abstract']
                    cited = each_word_doc['cited'].rstrip('.0')
                    if cited == 'nan':
                        cited = '0'

                    downed = each_word_doc['downed'].rstrip('.0')
                    if downed == 'nan':
                        downed = '0'
                    download = each_word_doc['download']

                    det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                       kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                       download=download, name=subrepo_name, introduction=subrepo_intro)
                    det.save()

                data = {
                    'query': results[0],
                    'raw_count': results[1],
                    'filter_search_count': filter_count
                }
                print(data)
                return Response(data)

        # 有日期筛选
        else:
            # 1.有且仅有一个表达式
            if len(expression_body) == 2:
                expression_context = expression_body[0]

                # 转换成ES中的字段
                if expression_context['type'] == '标题':
                    expression_context['type'] = 'title'
                elif expression_context['type'] == '作者':
                    expression_context['type'] = 'author'
                elif expression_context['type'] == '来源':
                    expression_context['type'] = 'source'
                elif expression_context['type'] == '机构/单位':
                    expression_context['type'] = 'info'
                elif expression_context['type'] == '基金':
                    expression_context['type'] = 'fund'
                elif expression_context['type'] == '关键词':
                    expression_context['type'] = 'kws'
                elif expression_context['type'] == '摘要':
                    expression_context['type'] = 'abstract'

                # 1.1 有且仅有必填项 关键词+单字段
                if not expression_context['relation']:
                    # 1.1.1 无正则
                    if expression_context['regex'] == '否':
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']

                        detail = GetDetailResult()
                        results = detail.get_only_expression_with_date(expression_type, expression_info, start_date, end_date)

                        sum_doc = results[2]
                        set_only = []
                        set_only.append(sum_doc[0])

                        # drop reqeated
                        for item in sum_doc:
                            k = 0
                            for iitem in set_only:
                                if item['title'] != iitem['title']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)  # [{no repeated}]

                        # 过滤后的搜索结果数
                        filter_count = len(set_only)

                        # 清洗字段
                        for each_word_doc in set_only:

                            title = each_word_doc['title']
                            author = each_word_doc['author']
                            if re.search(';', author):
                                author = re.sub(';', '', author)
                            source = each_word_doc['source']
                            info = each_word_doc['info']
                            date = each_word_doc['date']
                            kws = each_word_doc['kws']
                            if kws == 'nan':
                                kws = '暂无'
                            fund = each_word_doc['fund']
                            if fund == 'nan':
                                fund = '暂无'
                            abstract = each_word_doc['abstract']
                            cited = each_word_doc['cited'].rstrip('.0')
                            if cited == 'nan':
                                cited = '0'

                            downed = each_word_doc['downed'].rstrip('.0')
                            if downed == 'nan':
                                downed = '0'
                            download = each_word_doc['download']

                            det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                               kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                               download=download, name=subrepo_name, introduction=subrepo_intro)
                            det.save()

                        data = {
                            'query': results[0],
                            'raw_count': results[1],
                            'filter_search_count': filter_count
                        }
                        print(data)
                        return Response(data)

                    # 1.1.2 有正则
                    else:
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']

                        detail = GetDetailResult()
                        results = detail.get_only_expression_with_regexp(expression_type, expression_info, start_date, end_date)

                        sum_doc = results[2]
                        set_only = []
                        set_only.append(sum_doc[0])

                        # drop reqeated
                        for item in sum_doc:
                            k = 0
                            for iitem in set_only:
                                if item['title'] != iitem['title']:
                                    k += 1
                                else:
                                    break

                                if k == len(set_only):
                                    set_only.append(item)  # [{no repeated}]

                        # 过滤后的搜索结果数
                        filter_count = len(set_only)

                        # 清洗字段
                        for each_word_doc in set_only:

                            title = each_word_doc['title']
                            author = each_word_doc['author']
                            if re.search(';', author):
                                author = re.sub(';', '', author)
                            source = each_word_doc['source']
                            info = each_word_doc['info']
                            date = each_word_doc['date']
                            kws = each_word_doc['kws']
                            if kws == 'nan':
                                kws = '暂无'
                            fund = each_word_doc['fund']
                            if fund == 'nan':
                                fund = '暂无'
                            abstract = each_word_doc['abstract']
                            cited = each_word_doc['cited'].rstrip('.0')
                            if cited == 'nan':
                                cited = '0'

                            downed = each_word_doc['downed'].rstrip('.0')
                            if downed == 'nan':
                                downed = '0'
                            download = each_word_doc['download']

                            det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                               kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                               download=download, name=subrepo_name, introduction=subrepo_intro)
                            det.save()


                        data = {
                            'query': results[0],
                            'raw_count': results[1],
                            'filter_search_count': filter_count
                        }
                        print(data)
                        return Response(data)

                # 1.2 不止必填项 多关键字+单字段
                else:
                    # 1.2.1 无正则
                    if expression_context['regex'] == '否':
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']
                        expression_relation = expression_context['relation']
                        expression_otherinfo = expression_context['otherinfo']

                        detail = GetDetailResult()

                        if expression_relation == '并含':
                            in_method = '1'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_date(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '或含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_date(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '不含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = expression_type
                            exclude_kws = expression_otherinfo
                            results = detail.get_only_relation_expression_with_date(include_fields, include_kws, exclude_fields,
                                                                          exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                    # 1.2.2 有正则
                    else:
                        expression_type = expression_context['type'].split()
                        expression_info = expression_context['info']
                        expression_relation = expression_context['relation']
                        expression_otherinfo = expression_context['otherinfo']

                        detail = GetDetailResult()

                        if expression_relation == '并含':
                            in_method = '1'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_regexp_and_date(include_fields, include_kws, exclude_fields, exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '或含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = ['']
                            exclude_kws = ''
                            results = detail.get_only_relation_expression_with_regexp_and_date(include_fields, include_kws, exclude_fields, exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

                        elif expression_relation == '不含':
                            in_method = '2'
                            include_fields = expression_type
                            include_kws = expression_info
                            exclude_fields = expression_type
                            exclude_kws = expression_otherinfo
                            results = detail.get_only_relation_expression_with_regexp_and_date(include_fields, include_kws, exclude_fields, exclude_kws, start_date, end_date, in_method)
                            sum_doc = results[2]
                            set_only = []
                            set_only.append(sum_doc[0])

                            # drop reqeated
                            for item in sum_doc:
                                k = 0
                                for iitem in set_only:
                                    if item['title'] != iitem['title']:
                                        k += 1
                                    else:
                                        break

                                    if k == len(set_only):
                                        set_only.append(item)  # [{no repeated}]

                            # 过滤后的搜索结果数
                            filter_count = len(set_only)

                            # 清洗字段
                            for each_word_doc in set_only:

                                title = each_word_doc['title']
                                author = each_word_doc['author']
                                if re.search(';', author):
                                    author = re.sub(';', '', author)
                                source = each_word_doc['source']
                                info = each_word_doc['info']
                                date = each_word_doc['date']
                                kws = each_word_doc['kws']
                                if kws == 'nan':
                                    kws = '暂无'
                                fund = each_word_doc['fund']
                                if fund == 'nan':
                                    fund = '暂无'
                                abstract = each_word_doc['abstract']
                                cited = each_word_doc['cited'].rstrip('.0')
                                if cited == 'nan':
                                    cited = '0'

                                downed = each_word_doc['downed'].rstrip('.0')
                                if downed == 'nan':
                                    downed = '0'
                                download = each_word_doc['download']

                                det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                                   kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                                   download=download, name=subrepo_name, introduction=subrepo_intro)
                                det.save()

                            data = {
                                'query': results[0],
                                'raw_count': results[1],
                                'filter_search_count': filter_count
                            }
                            print(data)
                            return Response(data)

            # 2.多个表达式
            else:
                new_expression_body = []
                for expression_context in expression_body[:-1]:
                    # 转换成ES中的字段
                    if expression_context['type'] == '标题':
                        expression_context['type'] = 'title'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '作者':
                        expression_context['type'] = 'author'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '来源':
                        expression_context['type'] = 'source'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '机构/单位':
                        expression_context['type'] = 'info'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '基金':
                        expression_context['type'] = 'fund'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '关键词':
                        expression_context['type'] = 'kws'
                        new_expression_body.append(expression_context)
                    elif expression_context['type'] == '摘要':
                        expression_context['type'] = 'abstract'
                        new_expression_body.append(expression_context)

                detail = GetDetailResult()
                results = detail.get_multiple_expression_with_date(new_expression_body, start_date, end_date)

                sum_doc = results[2]
                set_only = []
                set_only.append(sum_doc[0])

                # drop reqeated
                for item in sum_doc:
                    k = 0
                    for iitem in set_only:
                        if item['title'] != iitem['title']:
                            k += 1
                        else:
                            break

                        if k == len(set_only):
                            set_only.append(item)  # [{no repeated}]

                # 过滤后的搜索结果数
                filter_count = len(set_only)

                # 清洗字段
                for each_word_doc in set_only:

                    title = each_word_doc['title']
                    author = each_word_doc['author']
                    if re.search(';', author):
                        author = re.sub(';', '', author)
                    source = each_word_doc['source']
                    info = each_word_doc['info']
                    date = each_word_doc['date']
                    kws = each_word_doc['kws']
                    if kws == 'nan':
                        kws = '暂无'
                    fund = each_word_doc['fund']
                    if fund == 'nan':
                        fund = '暂无'
                    abstract = each_word_doc['abstract']
                    cited = each_word_doc['cited'].rstrip('.0')
                    if cited == 'nan':
                        cited = '0'

                    downed = each_word_doc['downed'].rstrip('.0')
                    if downed == 'nan':
                        downed = '0'
                    download = each_word_doc['download']

                    det = Detailsearch(title=title, author=author, source=source, info=info, date=date,
                                       kws=kws, fund=fund, abstract=abstract, cited=cited, downed=downed,
                                       download=download, name=subrepo_name, introduction=subrepo_intro)
                    det.save()

                data = {
                    'query': results[0],
                    'raw_count': results[1],
                    'filter_search_count': filter_count
                }
                print(data)
                return Response(data)

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def filteresult(request):
    if request.method == 'GET':

        latest = Detailsearch.objects.last()
        raw_dict = model_to_dict(latest)

        db = 'filteresult'
        raw_temps = Temp.objects.filter(record_db=db)

        if raw_temps:
            temps = []
            for raw_temp in raw_temps:
                raw_temp_dict = model_to_dict(raw_temp)
                temps.append(raw_temp_dict)
            temp_dict = temps[-1]
            pre_id = temp_dict['record_id']
            post_id = raw_dict['id']
            temp = Temp(record_id=post_id, record_db=db)
            temp.save()

            filteresults = []

            updates = Detailsearch.objects.filter(id__gt=pre_id)
            # updates = Detailsearch.objects.all()[:5]  # for test

            # 自增序号刷新【前端改】
            # uid = 1
            for update in updates:
                update_dict = model_to_dict(update)
                # update_dict['id'] = str(uid)
                # uid += 1

                filteresults.append(update_dict)

            if filteresults is not None:
                print(filteresults)
                data = {
                    'record_id': pre_id,
                    'result': filteresults
                }
                return Response(data)
            else:
                return Response('No suitable data!')

        else:
            pre_id = raw_dict['id']
            print(pre_id)
            temp = Temp(record_id=pre_id, record_db=db)
            temp.save()

            filteresults = []
            updates = Detailsearch.objects.all()
            # updates = Detailsearch.objects.all()[:5]  # for test

            # 自增序号刷新 【前端改】
            # uid = 1
            for update in updates:
                update_dict = model_to_dict(update)
                # update_dict['id'] = str(uid)
                # uid += 1

                filteresults.append(update_dict)

            if filteresults:
                print(filteresults)
                data = {
                    'record_id': '0', # 首次检索
                    'result': filteresults
                }
                return Response(data)
            else:
                return Response('No suitable data!')


@api_view(('GET',))
def getsubrepo(request):
    if request.method == 'GET':

        latest = Projectinfo.objects.last()
        if latest:
            name = model_to_dict(latest)['subrepo']
            intro = model_to_dict(latest)['introduction']
            data = {
                'name': name,
                'intro': intro
            }
            return Response(data)
        else:
            return Response('failed')


@api_view(('POST', 'GET',))
def getrecordId(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        id_dict = ast.literal_eval(raw_dict_key)
        record_id = int(id_dict['record_id'].strip('"'))

        # 按前台存储id查找
        if record_id == '0':
            results = []
            updates = Detailsearch.objects.all()
            for update in updates:
                update_dict = model_to_dict(update)
                results.append(update_dict)

            if results:
                print(results)
                data = {
                    'record_id': '0',  # 首次检索
                    'result': results
                }
                return Response(data)
            else:
                return Response('No suitable data!')

        else:
            pre_id = record_id
            results = []

            updates = Detailsearch.objects.filter(id__gt=pre_id)
            for update in updates:
                update_dict = model_to_dict(update)

                results.append(update_dict)

            if results is not None:
                print(results)
                data = {
                    'record_id': pre_id,
                    'result': results
                }
                return Response(data)
            else:
                return Response('No suitable data!')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST', 'GET',))
def selectedfilterresult(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        target_dict = ast.literal_eval(raw_dict_key)
        target_id = int(target_dict['target'].strip('"'))

        # 按对应id查找
        target_data = Detailsearch.objects.filter(id=target_id)
        for data in target_data:
            clean_data = model_to_dict(data)

            return Response(clean_data)

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def getcollection(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/collection/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        collection_dict = ast.literal_eval(raw_dict_key)
        print(collection_dict)

        # 收藏词表
        collection = collection_dict['collection'].strip('"')

        collections = []

        if Collection.objects.filter(folder=collection):
            data = Collection.objects.filter(folder=collection)

            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                print(d_dict)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['title'] != iitem['title'] and item['author'] != iitem['author']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                print(only)
                pkid = only['id']
                collection_data = CollectionSerializer(data=only, context=serializer_context)
                if collection_data.is_valid():
                    ordered_li = collection_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    collections.append(ordered_li)
            print(collections)

            return Response(collections)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def addcollection(request):
    if request.method == 'POST':

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        collection_dict = ast.literal_eval(raw_dict_key)
        print(collection_dict)

        # 接口数据
        raw_collected_data = collection_dict['collect']
        flag = collection_dict['flag'].strip('"')
        folder = collection_dict['folder'].strip('"')

        drop_quotation_data = re.sub('^"|"$', '', raw_collected_data)
        collected_data = ast.literal_eval(drop_quotation_data.strip(']['))

        # 收藏论文字段
        title = collected_data['title']
        author = collected_data['author']
        info = collected_data['info']
        date = collected_data['date']

        if not Collection.objects.filter(title=title, author=author, info=info, date=date, flag=flag, folder=folder):
            collect = Collection(title=title, author=author, info=info, date=date, flag=flag, folder=folder)
            collect.save()
            return Response('success')

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deletecollection(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        collection_dict = ast.literal_eval(raw_dict_key)

        delete_id = collection_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            get_object_or_404(Collection, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def getcorpus(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/corpus/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        corpus_dict = ast.literal_eval(raw_dict_key)
        print(corpus_dict)

        # 收藏词表
        corpus = corpus_dict['corpus'].strip('"')

        corpuss = []

        if Corpus.objects.filter(repository=corpus):
            data = Corpus.objects.filter(repository=corpus)

            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['kws'] != iitem['kws']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                corpus_data = CorpusSerializer(data=only, context=serializer_context)
                if corpus_data.is_valid():
                    ordered_li = corpus_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    corpuss.append(ordered_li)
            print(corpuss)

            return Response(corpuss)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


# 添加词汇方式1. 详情页点击收藏
@api_view(('POST','GET',))
def appendcorpus(request):
    if request.method == 'POST':

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        corpus_dict = ast.literal_eval(raw_dict_key)
        print(corpus_dict)

        # 接口数据
        raw_corpus_data = corpus_dict['corpus']
        repo = corpus_dict['repository'].strip('"')

        # 收藏词汇
        kws = ast.literal_eval(raw_corpus_data.strip(']['))['name']
        print(kws)
        print(repo)

        if not Corpus.objects.filter(kws=kws, repository=repo):
            corp = Corpus(kws=kws, repository=repo)
            corp.save()
            return Response('success')

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


# 添加词汇方式2. 词表库内直接添加
@api_view(('POST','GET',))
def addcorpus(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/corpus/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        corpus_dict = ast.literal_eval(raw_dict_key)
        print(corpus_dict)

        # 词汇名称
        kws = corpus_dict['kws']
        print(kws)

        corpus = corpus_dict['corpus'].strip('"')
        print(corpus)

        corpuss = []
        # 重复值判断
        if Corpus.objects.filter(kws=kws):
            return Response('failed')
        else:
            corp = Corpus(kws=kws, repository=corpus)
            corp.save()

            data = Corpus.objects.filter(kws=kws, repository=corpus)
            print(data)
            for d in data:
                raw_dict = model_to_dict(d)

                pkid = raw_dict['id']
                corpus_data = CorpusSerializer(data=raw_dict, context=serializer_context)
                if corpus_data.is_valid():
                    ordered_li = corpus_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    corpuss.append(ordered_li)
                    print(ordered_li)

        return Response(corpuss[0])

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deletecorpus(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        corpus_dict = ast.literal_eval(raw_dict_key)

        delete_id = corpus_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            get_object_or_404(Corpus, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getfolder(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/folder/'

        data = Folder.objects.all()

        folders = []
        if data:
            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['folder'] != iitem['folder']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                folder_data = FolderSerializer(data=only, context=serializer_context)
                if folder_data.is_valid():
                    ordered_li = folder_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    folders.append(ordered_li)
            print(folders)

            return Response(folders)

        else:
            return Response('failed')


@api_view(('POST','GET',))
def addfolder(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/folder/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        folder_dict = ast.literal_eval(raw_dict_key)
        print(folder_dict)

        # 收藏夹名称
        fold_name = folder_dict['foldername']
        print(fold_name)

        folders = []

        if not Folder.objects.filter(folder=fold_name):  # 未找到重复值, 先存再取
            folder = Folder(folder=fold_name)
            folder.save()

            data = Folder.objects.filter(folder=fold_name)

            for d in data:
                raw_dict = model_to_dict(d)

                pkid = raw_dict['id']
                corpus_data = FolderSerializer(data=raw_dict, context=serializer_context)
                if corpus_data.is_valid():
                    ordered_li = corpus_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    folders.append(ordered_li)
            print(folders)

            return Response(folders[0])

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deletefolder(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        folder_dict = ast.literal_eval(raw_dict_key)

        delete_id = folder_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            data = Folder.objects.filter(pk=int(delete_id))
            d_dict = model_to_dict(data[0])
            folder_name = d_dict['folder']
            Collection.objects.filter(folder=folder_name).delete()
            get_object_or_404(Folder, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getrepository(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/repository/'

        data = Repository.objects.all()

        repositorys = []

        if data:
            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['repository'] != iitem['repository']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                repository_data = RepositorySerializer(data=only, context=serializer_context)
                if repository_data.is_valid():
                    ordered_li = repository_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    repositorys.append(ordered_li)
            print(repositorys)

            return Response(repositorys)

        else:
            return Response('failed')


@api_view(('POST','GET',))
def addrepository(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/repository/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        repository_dict = ast.literal_eval(raw_dict_key)
        print(repository_dict)

        # 词表库名称
        repo_name = repository_dict['reponame']
        print(repo_name)

        repos = []

        if not Repository.objects.filter(repository=repo_name):
            repository = Repository(repository=repo_name)
            repository.save()

            data = Repository.objects.filter(repository=repo_name)

            for d in data:
                raw_dict = model_to_dict(d)

                pkid = raw_dict['id']
                corpus_data = RepositorySerializer(data=raw_dict, context=serializer_context)
                if corpus_data.is_valid():
                    ordered_li = corpus_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    repos.append(ordered_li)
            print(repos)

            return Response(repos[0])

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deleterepository(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        repository_dict = ast.literal_eval(raw_dict_key)

        delete_id = repository_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            data = Repository.objects.filter(pk=int(delete_id))
            d_dict = model_to_dict(data[0])
            repo_name = d_dict['repository']
            Corpus.objects.filter(repository=repo_name).delete()
            get_object_or_404(Repository, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getfilerepo(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/filerepo/'

        data = Filerepo.objects.all()

        filerepos = []

        if data:
            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['name'] != iitem['name']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)
            print(set_only)
            for only in set_only:
                pkid = only['id']
                filerepo_data = FilerepoSerializer(data=only, context=serializer_context)
                if filerepo_data.is_valid():
                    ordered_li = filerepo_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    filerepos.append(ordered_li)
            print(filerepos)

            return Response(filerepos)

        else:
            return Response('failed')


@api_view(('DELETE','GET',))
def deletefilerepo(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        filerepo_dict = ast.literal_eval(raw_dict_key)

        delete_id = filerepo_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            data = Filerepo.objects.filter(pk=int(delete_id))
            d_dict = model_to_dict(data[0])
            subrepo_name = d_dict['name']
            Detailsearch.objects.filter(name=subrepo_name).delete()
            get_object_or_404(Filerepo, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET', 'POST',))
def getfile(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/detailsearch/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        file_dict = ast.literal_eval(raw_dict_key)

        subrepo_name = file_dict['name'].strip('"')
        print(subrepo_name)

        if Detailsearch.objects.filter(name=subrepo_name):
            data = Detailsearch.objects.filter(name=subrepo_name)

            files = []

            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                print(d_dict)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['title'] != iitem['title'] and item['author'] != iitem['author']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                print(only)
                pkid = only['id']
                file_data = DetailsearchSerializer(data=only, context=serializer_context)
                if file_data.is_valid():
                    ordered_li = file_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    files.append(ordered_li)
            print(files)

            return Response(files)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET', 'POST',))
def saveproject(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        project_dict = ast.literal_eval(raw_dict_key)
        print(project_dict)
        name = project_dict['name']
        date = project_dict['date']
        type = project_dict['type']
        source = project_dict['source']
        description = project_dict['description']
        method = project_dict['method']
        corpus = project_dict['corpus']
        subrepo = project_dict['subrepo']
        introduction = project_dict['intro']
        raw_extract = project_dict['extract']
        raw_recommend = project_dict['recommend']

        extract, recommend = [], []

        extracts = ast.literal_eval(raw_extract.strip(']['))
        if isinstance(extracts, tuple):
            for extractors_dict in extracts:
                extracted_words = extractors_dict['originkws']
                extract.append(extracted_words)
        else:
            extracted_words = extracts['originkws']
            extract.append(extracted_words)

        if raw_recommend != '[]':
            recommends = ast.literal_eval(raw_recommend.strip(']['))
            if isinstance(recommends, tuple):
                for recommends_dict in recommends:
                    recommend_words = recommends_dict['recommendkws']
                    recommend.append(recommend_words)
            else:
                recommend_words = recommends['recommendkws']
                recommend.append(recommend_words)
        else:
            print('暂无推荐词')

        # print(extract)
        # print(recommend)
        print(Project.objects.filter(project=name))
        print(Projectinfo.objects.filter(project=name))
        if not Projectinfo.objects.filter(project=name):
            projectinfo = Projectinfo(project=name, date=date, type=type, source=source, description=description, method=method, extract=','.join(extract), recommend=','.join(recommend), corpus=corpus, subrepo=subrepo, introduction=introduction)
            projectinfo.save()
            return Response('success')
        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getproject(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/project/'

        data = Project.objects.all()
        print(data)

        projects = []
        if data:
            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['project'] != iitem['project']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                project_data = ProjectSerializer(data=only, context=serializer_context)
                if project_data.is_valid():
                    ordered_li = project_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    projects.append(ordered_li)
            print(projects)

            return Response(projects)

        else:
            return Response('failed')


@api_view(('GET', 'POST',))
def addproject(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/project/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        project_dict = ast.literal_eval(raw_dict_key)
        print(project_dict)

        # 收藏夹名称
        project_name = project_dict['name']
        print(project_name)

        projects = []

        if not Project.objects.filter(project=project_name):  # 未找到重复值, 先存再取
            project = Project(project=project_name)
            project.save()

            data = Project.objects.filter(project=project_name)

            for d in data:
                raw_dict = model_to_dict(d)

                pkid = raw_dict['id']
                project_data = ProjectSerializer(data=raw_dict, context=serializer_context)
                if project_data.is_valid():
                    ordered_li = project_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    projects.append(ordered_li)
            print(projects)

            return Response(projects[0])

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('DELETE','GET',))
def deleteproject(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        project_dict = ast.literal_eval(raw_dict_key)

        delete_id = project_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            data = Project.objects.filter(pk=int(delete_id))
            d_dict = model_to_dict(data[0])
            project_name = d_dict['project']
            Projectinfo.objects.filter(project=project_name).delete()
            get_object_or_404(Project, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getpending(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/pending/'

        data = Pending.objects.all()
        print(data)

        pendings = []
        if data:
            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['project'] != iitem['project']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                if only['recommend'] == '':
                    temp = []
                    only['recommend'] = str(temp.append('暂无'))
                pending_data = PendingSerializer(data=only, context=serializer_context)
                if pending_data.is_valid():
                    ordered_li = pending_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    pendings.append(ordered_li)
            print(pendings)

            return Response(pendings)

        else:
            return Response('failed')


@api_view(('DELETE','GET',))
def deletepending(request):
    if request.method == 'DELETE':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        pending_dict = ast.literal_eval(raw_dict_key)

        delete_id = pending_dict['delid']
        print(delete_id)

        if not delete_id:
            return Response('failed')
        else:
            get_object_or_404(Pending, pk=int(delete_id)).delete()
            return Response('success')

    if request.method == 'GET':
        return Response('No method!')

@api_view(('GET', 'POST',))
def getprojectinfo(request):
    if request.method == 'POST':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/projectinfo/'

        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        projectinfo_dict = ast.literal_eval(raw_dict_key)

        project_name = projectinfo_dict['name'].strip('"')
        print(project_name)

        if Projectinfo.objects.filter(project=project_name):
            data = Projectinfo.objects.filter(project=project_name)

            infos = []

            raw_d_dict = []
            for d in data:
                d_dict = model_to_dict(d)
                raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['project'] != iitem['project'] and item['date'] != iitem['date']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)

            for only in set_only:
                pkid = only['id']
                if only['recommend'] == '':
                    temp = []
                    only['recommend'] = str(temp.append('暂无'))
                info_data = ProjectinfoSerializer(data=only, context=serializer_context)
                if info_data.is_valid():
                    ordered_li = info_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    ordered_li['extract'] = re.sub('\'', '', ordered_li['extract'].strip(']['))
                    ordered_li['recommend'] = re.sub('\'', '', ordered_li['recommend'].strip(']['))
                    infos.append(ordered_li)
                else:
                    print('暂无推荐词')
            print(infos[0])

            return Response(infos[0])

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET', 'POST',))
def savepersonal(request):
    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        print(raw_dict_key)
        personal_dict = ast.literal_eval(raw_dict_key)
        print(personal_dict)
        name = personal_dict['name']
        gender = personal_dict['gender']
        age = personal_dict['age']
        email = personal_dict['email']
        job = personal_dict['job']
        place = personal_dict['place']
        post = personal_dict['post']
        sign = personal_dict['sign']

        if not Personal.objects.filter(name=name, gender=gender, age=age, email=email, job=job, place=place, post=post, sign=sign):
            personalinfo = Personal(name=name, gender=gender, age=age, email=email, job=job, place=place, post=post, sign=sign)
            personalinfo.save()
            return Response('success')
        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('GET',))
def getpersonal(request):
    if request.method == 'GET':

        serializer_context = {
            'request': request,
        }

        base_router = 'http://127.0.0.1:8000/api/personal/'

        data = Personal.objects.last()
        print(data)

        personals = []
        if data:
            raw_d_dict = []
            d_dict = model_to_dict(data)
            raw_d_dict.append(d_dict)

            set_only = []
            set_only.append(raw_d_dict[0])

            # drop reqeated
            for item in raw_d_dict:
                k = 0
                for iitem in set_only:
                    if item['name'] != iitem['name'] and item['gender'] != iitem['gender'] and item['age'] != iitem['age'] and item['email'] != iitem['email']:
                        k += 1
                    else:
                        break

                    if k == len(set_only):
                        set_only.append(item)
            for only in set_only:
                pkid = only['id']
                personal_data = PersonalSerializer(data=only, context=serializer_context)
                if personal_data.is_valid():
                    ordered_li = personal_data.validated_data
                    ordered_li['pk'] = pkid
                    ordered_li['url'] = base_router + str(pkid) + '/'
                    ordered_li = dict(ordered_li)
                    personals.append(ordered_li)
            print(personals)

            return Response(personals[0])

        else:
            return Response('failed')


@api_view(('GET',))
def getrecommend(request):
    if request.method == 'GET':
        data = Personal.objects.last()
        print(data)
        if data:
            d_dict = model_to_dict(data)
            region = d_dict['job']
            print(region)
        else:
            print('还未填写个人信息!')
            region = '氨基酸'
        from .recommend.SSRP_recommend_data import GetRecommendResult
        get = GetRecommendResult()
        daily_recommend = get.get_daily_recommend(region)
        print(daily_recommend)
        return Response(daily_recommend)


@api_view(('POST','GET',))
def titleprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        title_dict = ast.literal_eval(raw_dict_key)
        print(title_dict)

        title = title_dict['titles'].split()
        print(title)

        data = {
            'titles': title
        }
        api = 'https://innovaapi.aminer.cn/tools/v1/predict/nsfc?'

        try:
            response = requests.post(url=api, data=json.dumps(data), timeout=10)
            res = ast.literal_eval(response.text)['data']
            print(res)
            levels = res.keys()
            print(levels)
            tableData = []
            for k in range(1, (len(levels)+1)):
                for v in list(res.values())[k-1]:
                    v['group'] = 'level' + str(k)
                    v.pop('code')
                    tableData.append(v)
            print(tableData)

            return Response(tableData)
        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def aititleprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        title_dict = ast.literal_eval(raw_dict_key)
        print(title_dict)

        words = title_dict['words']
        if len(words) > 1:
            words = words.split('，')
        else:
            words = words.split()
        print(words)

        data = {
            'words': words
        }
        api = 'https://innovaapi.aminer.cn/tools/v1/predict/nsfc/ai?'

        try:
            response = requests.post(url=api, data=json.dumps(data), timeout=10)
            res = ast.literal_eval(response.text)['data']
            res.pop('tree')
            print(res)
            levels = list(res.keys())
            print(levels)
            tableData = []
            for k in range(1, (len(levels)+1)):
                for v in list(res.values())[k-1]:
                    v.pop('name')
                    v['name'] = v.pop('name_zh')
                    v['group'] = 'level' + str(k)
                    tableData.append(v)
            print(tableData)

            return Response(tableData)
        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def genderprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        gender_dict = ast.literal_eval(raw_dict_key)
        print(gender_dict)

        name = gender_dict['name']
        org = gender_dict['org']
        image_url = gender_dict['image_url']
        print(name)
        print(org)

        # api请求内容发生变化
        # api = 'https://innovaapi.aminer.cn/tools/v1/predict/gender?name=' + name + '&org=' + org + '&image_url=' + image_url
        # print(api)
        # try:
            # response = requests.get(url=api, timeout=50)
            # res = ast.literal_eval(response.text)['data']
            # print(response.text)
        try:
            # 选择导入脚本执行预测
            from .prediction_api.src.gender import Gender
            g = Gender()
            res = g.predict(name=name, org=org, image_url=image_url)
            print(res)
            data = {}
            if res['male'] > res['female']:
                data['result'] = '男'
            elif res['male'] < res['female']:
                data['result'] = '女'
            else:
                data['result'] = '性别不明'

            res.pop('male')
            res.pop('female')

            values = list(res.values())

            genders = []
            datas = []
            for v in values:
                if v['male'] > v['female']:
                    genders.append('男')
                elif v['male'] < v['female']:
                    genders.append('女')
                else:
                    genders.append('男女都可能')
            print(genders)

            data['name'] = genders[0]
            data['search'] = genders[1]
            data['face'] = genders[2]

            print(data)
            datas.append(data)
            return Response(datas)

        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def identityprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        identity_dict = ast.literal_eval(raw_dict_key)
        print(identity_dict)

        pc = identity_dict['pc']
        cn = identity_dict['cn']
        hi = identity_dict['hi']
        gi = identity_dict['gi']
        year_range = identity_dict['year_range']
        print(pc)
        print(cn)
        print(hi)
        print(gi)
        print(year_range)

        api = 'https://innovaapi.aminer.cn/tools/v1/predict/identity?' + 'pc=' + pc + '&cn=' + cn + '&hi=' + hi + '&gi=' + gi + '&year_range=' + year_range

        try:
            response = requests.get(url=api, timeout=10)
            res = ast.literal_eval(response.text)['data']
            print(res)
            datas = []
            data = {}
            if res['label'] == 'teacher':
                data['label'] = '老师'
            else:
                data['label'] = '学生'

            if res['degree'] == 'undergraduate':
                data['degree'] = '本科'
            elif res['degree'] == 'master':
                data['degree'] = '硕士'
            else:
                data['degree'] = '博士'

            data['p'] = res['p']
            datas.append(data)
            return Response(datas)

        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def hoppingprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        hopping_dict = ast.literal_eval(raw_dict_key)
        print(hopping_dict)
        ntop = hopping_dict['ntop']
        org_name = hopping_dict['org_name']

        if re.search('，', org_name):
            org_names = org_name.split('，')
            print(org_names)
        else:
            org_names = []
            org_names.append(org_name)
            print(org_names)

        # api请求内容发生变化
        # api = 'https://innovaapi.aminer.cn/tools/v1/predict/career?' + 'per_name=' + per_name + '&org_name=' + org_name

        # try:
        #    response = requests.get(url=api, timeout=10, verify=False)
        #   res = ast.literal_eval(response.text)['data']
        #    print(response.text)

        try:
            # 调用脚本执行预测
            from .prediction_api.src.jobhopping import JobHopping
            j = JobHopping()
            res = j.predict(org_names, int(ntop))
            print(res)
            return Response(res)
        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def scholarrecommend(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        scholar_dict = ast.literal_eval(raw_dict_key)
        print(scholar_dict)
        text = scholar_dict['text']
        num = scholar_dict['num']

        data = {
            'text': text,
            'num': int(num)
        }
        api = 'https://innovaapi.aminer.cn/tools/v1/predict/experts?'

        try:
            from .data.user_agent import USER_AGENT
            import random
            headers = {
                'User-Agent': random.choice(USER_AGENT)
            }
            response = requests.post(url=api, data=json.dumps(data), headers=headers, timeout=10)
            res = ast.literal_eval(response.text)['data']
            print(res)
            return Response(res)

        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def paperprediction(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        print(raw_dict)
        raw_dict_key = list(raw_dict.keys())[0]
        paper_dict = ast.literal_eval(raw_dict_key)
        print(paper_dict)
        pid = paper_dict['pid']

        api = 'https://innovaapi.aminer.cn/tools/v1/predict/nsfc/person?' + 'pid=' + pid
        try:
            from .data.user_agent import USER_AGENT
            import random
            headers = {
                'User-Agent': random.choice(USER_AGENT)
            }
            response = requests.get(url=api, headers=headers, timeout=10)
            print(response.text)
            res = ast.literal_eval(response.text)['data']
            flag = list(res.keys())[0]
            tableData = []
            if res[flag] == 'No pubs':
                return Response('No result')
            else:
                res.pop('tree')
                print(res)
                levels = list(res.keys())
                print(levels)
                for k in range(1, (len(levels) + 1)):
                    for v in list(res.values())[k - 1]:
                        v.pop('name')
                        v['name'] = v.pop('name_zh')
                        v['group'] = 'level' + str(k)
                        tableData.append(v)
                print(tableData)

            return Response(tableData)
        except Exception as e:
            print(e)
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def frequencyanalyze(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        frequency_dict = ast.literal_eval(raw_dict_key)
        source = frequency_dict['source']
        print(source)

        if Detailsearch.objects.filter(name=source):
            data = Detailsearch.objects.filter(name=source)

            kwss = []
            titles = []
            abstracts = []

            for d in data:
                d_dict = model_to_dict(d)
                if d_dict['kws'] == '暂无':
                    pass
                else:
                    if re.search('；', d_dict['kws']):
                        new_kws = re.sub('"', '', d_dict['kws'])
                        new_kws1 = re.sub('； |;', ', ', new_kws)
                        kwss.append(new_kws1)
                    else:
                        new_kws = re.sub(';', ', ', d_dict['kws'])
                        kwss.append(new_kws)
                titles.append(d_dict['title'])
                abstracts.append(d_dict['abstract'])

            kws_data = []
            for kws in kwss:
                for kw in kws.split():
                    kws_data.append(kw.strip(','))

            from .analysis.SSRP_cloud_analysis import CloudAnalysis
            cloud = CloudAnalysis()
            frequent_kws = cloud.keyword_count(kws_data)
            frequent_title = cloud.title_or_abstract_count(titles)
            frequent_abstract = cloud.title_or_abstract_count(abstracts)
            print(frequent_kws)
            print(frequent_title)
            print(frequent_abstract)

            new_data = {
                'kws': frequent_kws,
                'title': frequent_title,
                'abstract': frequent_abstract
            }
            return Response(new_data)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def volumeanalyze(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        volume_dict = ast.literal_eval(raw_dict_key)
        start_date = volume_dict['start']
        end_date = volume_dict['end']
        source = volume_dict['source']
        print(start_date)
        print(end_date)
        print(source)

        if Detailsearch.objects.filter(name=source, source='期刊', date__range=(start_date, end_date)):
            data = Detailsearch.objects.filter(name=source, source='期刊', date__range=(start_date, end_date))
            infos = []
            for d in data:
                d_dict = model_to_dict(d)
                infos.append(d_dict['info'])

            from .analysis.SSRP_cloud_analysis import CloudAnalysis
            cloud = CloudAnalysis()
            frequent_infos = cloud.keyword_count(infos)
            print(frequent_infos)

            return Response(frequent_infos)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def relationanalyze(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        relation_dict = ast.literal_eval(raw_dict_key)
        source = relation_dict['source']
        print(source)

        if Detailsearch.objects.filter(name=source):
            data = Detailsearch.objects.filter(name=source)

            kwss = []
            for d in data:
                d_dict = model_to_dict(d)
                if d_dict['kws'] != '暂无':
                    if re.search('；', d_dict['kws']):
                        new_kws = re.sub('"', '', d_dict['kws'])
                        new_kws1 = re.sub('； |;', ',', new_kws)
                        kws = new_kws1.split(',')
                        kwss.append(kws)

                    else:
                        new_kws = re.sub(';', ',', d_dict['kws'])
                        kws = new_kws.split(',')
                        kwss.append(kws)
                else:
                    continue

            from .analysis.SSRP_network_analysis import WordVector
            vec = WordVector()
            network_data = {
                'nodes': vec.build_network_scipy_data()[0],
                'edges': vec.build_network_scipy_data()[1]
            }
            return Response(network_data)

        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def classifyanalyze(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        classify_dict = ast.literal_eval(raw_dict_key)
        source = classify_dict['source']
        print(source)
        theme = int(classify_dict['theme'])
        themeword = int(classify_dict['themeword'])

        if Detailsearch.objects.filter(name=source):
            data = Detailsearch.objects.filter(name=source)

            abs = []
            for d in data:
                d_dict = model_to_dict(d)
                if d_dict['abstract']:
                    abs.append(d_dict['abstract'])
            print(abs)

            from .analysis.SSRP_classify_analysis import ClassifyAnalysis
            classify = ClassifyAnalysis()
            lda_data = classify.simple_LDA_analysis(abs, theme, themeword)
            return Response(lda_data)
        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


@api_view(('POST','GET',))
def cooperationanalyze(request):

    if request.method == 'POST':
        raw_dict = dict(zip(request.POST.keys(), request.POST.values()))
        raw_dict_key = list(raw_dict.keys())[0]
        cooperation_dict = ast.literal_eval(raw_dict_key)
        source = cooperation_dict['source']
        print(source)

        if Detailsearch.objects.filter(name=source):
            data = Detailsearch.objects.filter(name=source)

            two_aus = []
            more_aus = []
            for d in data:
                d_dict = model_to_dict(d)
                if not re.search('[a-zA-Z]', d_dict['author']):
                    if len(d_dict['author'].split()) == 2:
                        two_aus.append(d_dict['author'])
                    elif len(d_dict['author'].split()) > 2:
                        more_aus.append(d_dict['author'])
                    else:
                        continue
                else:
                    continue

            print(len(two_aus))
            print(len(more_aus))

            from .analysis.SSRP_cooperation_analysis import CooperateAnalysis
            cooper = CooperateAnalysis()
            id_relation = cooper.build_au_relation(two_aus[:5], more_aus[:3])
            print(id_relation)
            cooper_data = {
                'nodes': id_relation[0],
                'edges': id_relation[1]
            }
            return Response(cooper_data)
        else:
            return Response('failed')

    if request.method == 'GET':
        return Response('No method!')


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or edited.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class UploadcorpusViewSet(viewsets.ModelViewSet):

    queryset = Uploadcorpus.objects.all()
    serializer_class = UploadcorpusSerializer


class ExtractorViewset(viewsets.ModelViewSet):
    queryset = Extractor.objects.all()
    serializer_class = ExtractorSerializer


class RecommedViewset(viewsets.ModelViewSet):
    queryset = Recommend.objects.all()
    serializer_class = RecommendSerializer


class SimplesearchViewset(viewsets.ModelViewSet):
    queryset = Simplesearch.objects.all()
    serializer_class = SimplesearchSerializer


class DetailsearchViewset(viewsets.ModelViewSet):
    queryset = Detailsearch.objects.all()
    serializer_class = DetailsearchSerializer


class TempViewset(viewsets.ModelViewSet):
    queryset = Temp.objects.all()
    serializer_class = TempSerializer


class FolderViewset(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class CollectionViewset(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class RepositoryViewset(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


class CorpusViewset(viewsets.ModelViewSet):
    queryset = Corpus.objects.all()
    serializer_class = CorpusSerializer


class FilerepoViewset(viewsets.ModelViewSet):
    queryset = Filerepo.objects.all()
    serializer_class = FilerepoSerializer


class PendingViewset(viewsets.ModelViewSet):
    queryset = Pending.objects.all()
    serializer_class = PendingSerializer


class ProjectViewset(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectinfoViewset(viewsets.ModelViewSet):
    queryset = Projectinfo.objects.all()
    serializer_class = ProjectinfoSerializer


class PersonalViewset(viewsets.ModelViewSet):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer


