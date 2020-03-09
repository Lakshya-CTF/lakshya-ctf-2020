from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin


# Create your models here. Use set_password 
EASY = 'EA'
MEDIUM = 'ME'
HARD = 'HA'

CATEGORY_CHOICE = ((EASY,'Easy'),(MEDIUM,'Medium'),(HARD,'Hard'))

class Team(AbstractUser):

	points = models.IntegerField(default=0)
	timeRequired = models.FloatField(default=0)
	played = models.BooleanField(default=False)

	def convert(self):
		return '{}:{}'.format(int(self.timeRequired//60),int(self.timeRequired%60))

	def __str__(self):
		return self.username


class TeamAdmin(admin.ModelAdmin):

	list_display = ('username','timeRequired','points')
	readonly_fields = ('password','points','timeRequired')
	search_fields = ['username','timeRequired','points']


class Questions(models.Model):

	questionId = models.AutoField(primary_key = True)
	questionDescription = models.TextField()
	questionPoints = models.IntegerField(default=0)
	questionData = models.FileField(blank=True)
	questionFlag = models.CharField(max_length=50,default='lakshya_CTF{hack_me_now}')
	questionHint = models.TextField(default="Sample Hint")
	questionSolvers = models.IntegerField(default=0)
	questionDifficulty = models.CharField(max_length=2,choices=CATEGORY_CHOICE,default=EASY)


	def __str__(self):
		return self.questionDescription

	class Meta:
		verbose_name = 'Question'
		verbose_name_plural = 'Questions'


class QuestionsAdmin(ImportExportActionModelAdmin):
	
	pass