from django.db import models
from rest_framework import serializers
# Create your models here.


class Message(models.Model):
	subject = models.TextField(max_length=3)
	body = models.TextField(max_length=200)


class MessageSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Message
		fields = ('url', 'subject', 'body', 'pk')


class Uploadcorpus(models.Model):
	corpus_name = models.TextField(max_length=30)
	corpus_kws = models.TextField(max_length=200)
	create_timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-create_timestamp',)


class UploadcorpusSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Uploadcorpus
		fields = ('url', 'corpus_name', 'corpus_kws', 'pk')


class Extractor(models.Model):
	originkws = models.CharField(max_length=200)


class ExtractorSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Extractor
		fields = ('url', 'originkws', 'pk')


class Recommend(models.Model):
	recommendkws = models.CharField(max_length=200)


class RecommendSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Recommend
		fields = ('url', 'recommendkws', 'pk')


class Simplesearch(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=50)
	source = models.CharField(max_length=10)
	info = models.TextField()
	date = models.TextField()
	kws = models.CharField(max_length=50)
	cited = models.TextField()
	downed = models.TextField()
	download = models.TextField()
	abstract = models.TextField()
	fund = models.TextField()


class SimplesearchSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Simplesearch
		fields = ('url', 'title', 'author', 'source', 'info', 'date', 'kws', 'cited', 'downed', 'download', 'abstract', 'fund', 'pk')


class Filerepo(models.Model):
	name = models.TextField()
	introduction = models.TextField()


class FilerepoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Filerepo
		fields = ('url', 'name', 'introduction', 'pk')


class Detailsearch(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=50)
	source = models.CharField(max_length=10)
	info = models.TextField()
	date = models.TextField()
	kws = models.CharField(max_length=50)
	cited = models.TextField()
	downed = models.TextField()
	download = models.TextField()
	abstract = models.TextField()
	fund = models.TextField()
	name = models.TextField(default="")
	introduction = models.TextField(default="")


class DetailsearchSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Detailsearch
		fields = ('url', 'title', 'author', 'source', 'info', 'date', 'kws', 'cited', 'downed', 'download', 'abstract', 'fund', 'name', 'introduction', 'pk')


class Temp(models.Model):
	record_id = models.TextField()
	record_db = models.TextField()


class TempSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Temp
		fields = ('url', 'record_id', 'record_db', 'pk')


class Folder(models.Model):
	folder = models.TextField()


class FolderSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Folder
		fields = ('url', 'folder', 'pk')


class Collection(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=50)
    info = models.TextField()
    date = models.TextField()
    folder = models.TextField(default="")
    flag = models.TextField(default="")


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Collection
		fields = ('url', 'title', 'author', 'info', 'date', 'folder', 'flag', 'pk')


class Repository(models.Model):
	repository = models.TextField()


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Repository
		fields = ('url', 'repository', 'pk')


class Corpus(models.Model):
	kws = models.TextField()
	repository = models.TextField()


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Corpus
		fields = ('url', 'kws', 'repository', 'pk')


class Pending(models.Model):
	project = models.TextField()
	extract = models.TextField()
	recommend = models.TextField()


class PendingSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Pending
		fields = ('url', 'project', 'extract', 'recommend', 'pk')


class Project(models.Model):
	project = models.TextField()


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Project
		fields = ('url', 'project', 'pk')


class Projectinfo(models.Model):
	project = models.TextField()
	date = models.TextField()
	type = models.TextField()
	source = models.TextField()
	description = models.TextField()
	method = models.TextField()
	extract = models.TextField()
	recommend = models.TextField()
	corpus = models.TextField(default="")
	subrepo = models.TextField(default="")
	introduction = models.TextField(default="")


class ProjectinfoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Projectinfo
		fields = ('url', 'project', 'date', 'type', 'source', 'description', 'method', 'extract', 'recommend', 'corpus', 'subrepo', 'introduction', 'pk')


class Personal(models.Model):
	name = models.TextField()
	gender = models.TextField()
	age = models.TextField()
	job = models.TextField()
	place = models.TextField()
	email = models.TextField()
	post = models.TextField(default="")
	sign = models.TextField()


class PersonalSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Personal
		fields = ('url', 'name', 'gender', 'age', 'email', 'job', 'place', 'post', 'sign', 'pk')
