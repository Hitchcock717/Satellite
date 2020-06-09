"""IDataSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from django.conf.urls import url
from backdoor import views
from backdoor.views import MessageViewSet, UploadcorpusViewSet, ExtractorViewset, RecommedViewset, SimplesearchViewset, DetailsearchViewset, TempViewset, FolderViewset, CollectionViewset, RepositoryViewset, CorpusViewset, FilerepoViewset, PendingViewset, ProjectViewset, ProjectinfoViewset, PersonalViewset

router = routers.DefaultRouter()
router.register('messages', MessageViewSet)
router.register('uploadcorpus', UploadcorpusViewSet)
router.register('extractors', ExtractorViewset)
router.register('recommends', RecommedViewset)
router.register('simplesearch', SimplesearchViewset)
router.register('detailesearch', DetailsearchViewset)
router.register('temp', TempViewset)
router.register('folder', FolderViewset)
router.register('collection', CollectionViewset)
router.register('repository', RepositoryViewset)
router.register('corpus', CorpusViewset)
router.register('filerepo', FilerepoViewset)
router.register('pending', PendingViewset)
router.register('project', ProjectViewset)
router.register('projectinfo', ProjectinfoViewset)
router.register('personal', PersonalViewset)

app_name = 'backdoor'

urlpatterns = [

    # http://localhost:8000/api/<router-viewsets>
    path('api/', include(router.urls)),

    url('api/scrapy/', views.scrapy),

    url('api/extract/', views.extract),

    url('api/recommend/', views.recommend),

    url('api/deletextract/', views.deletextract),

    url('api/deleterecommend/', views.deleterecommend),

    url('api/mockupload/', views.mockupload),

    url('api/parseupload/', views.parseupload),

    url('api/startspider/', views.startspider),

    url('api/rawresult/', views.rawresult),

    url('api/getrecordrawId/', views.getrecordrawId),

    url('api/getexpression/', views.getexpression),

    url('api/getsubrepo/', views.getsubrepo),

    url('api/filteresult/', views.filteresult),

    url('api/getrecordId/', views.getrecordId),

    url('api/selectedrawresult/', views.selectedrawresult),

    url('api/selectedfilterresult/', views.selectedfilterresult),

    url('api/getfolder/', views.getfolder),

    url('api/addfolder/', views.addfolder),

    url('api/deletefolder/', views.deletefolder),

    url('api/getcollection/', views.getcollection),

    url('api/addcollection/', views.addcollection),

    url('api/deletecollection/', views.deletecollection),

    url('api/getrepository/', views.getrepository),

    url('api/addrepository/', views.addrepository),

    url('api/deleterepository/', views.deleterepository),

    url('api/getfilerepo/', views.getfilerepo),

    url('api/deletefilerepo/', views.deletefilerepo),

    url('api/getfile/', views.getfile),

    url('api/getcorpus/', views.getcorpus),

    url('api/addcorpus/', views.addcorpus),

    url('api/appendcorpus/', views.appendcorpus),

    url('api/deletecorpus/', views.deletecorpus),

    url('api/saveproject/', views.saveproject),

    url('api/getproject/', views.getproject),

    url('api/addproject/', views.addproject),

    url('api/deleteproject/', views.deleteproject),

    url('api/getpending/', views.getpending),

    url('api/deletepending/', views.deletepending),

    url('api/savepersonal/', views.savepersonal),

    url('api/getpersonal/', views.getpersonal),

    url('api/getrecommend/', views.getrecommend),

    url('api/getprojectinfo/', views.getprojectinfo),

    url('api/titleprediction/', views.titleprediction),

    url('api/aititleprediction/', views.aititleprediction),

    url('api/genderprediction/', views.genderprediction),

    url('api/identityprediction/', views.identityprediction),

    url('api/hoppingprediction/', views.hoppingprediction),

    url('api/scholarrecommend/', views.scholarrecommend),

    url('api/paperprediction/', views.paperprediction),

    url('api/frequencyanalyze/', views.frequencyanalyze),

    url('api/volumeanalyze/', views.volumeanalyze),

    url('api/relationanalyze/', views.relationanalyze),

    url('api/classifyanalyze/', views.classifyanalyze),

    url('api/cooperationanalyze/', views.cooperationanalyze),

    # http://localhost:8000/api/admin/
    path('api/admin/', admin.site.urls),
]