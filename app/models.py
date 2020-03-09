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


class Events(models.Model):
	
    receiptid = models.CharField(db_column='ReceiptID', primary_key=True, max_length=100)  # Field name made lowercase.
    college = models.CharField(max_length=250)
    slot = models.CharField(max_length=20, blank=True, null=True)
    noofmem = models.IntegerField()
    domain = models.CharField(max_length=250)
    city = models.CharField(db_column='City', max_length=100)  # Field name made lowercase.
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    date = models.CharField(db_column='Date', max_length=30)  # Field name made lowercase.
    name1 = models.CharField(max_length=100)
    gender = models.CharField(db_column='Gender', max_length=20)  # Field name made lowercase.
    email1 = models.CharField(max_length=100)
    phone1 = models.BigIntegerField()
    name2 = models.CharField(max_length=100)
    gender2 = models.CharField(db_column='Gender2', max_length=20)  # Field name made lowercase.
    email2 = models.CharField(max_length=100)
    phone2 = models.BigIntegerField()
    name3 = models.CharField(max_length=100)
    gender3 = models.CharField(db_column='Gender3', max_length=20)  # Field name made lowercase.
    email3 = models.CharField(max_length=100)
    phone3 = models.BigIntegerField()
    name4 = models.CharField(max_length=100)
    gender4 = models.CharField(db_column='Gender4', max_length=20)  # Field name made lowercase.
    email4 = models.CharField(max_length=100)
    phone4 = models.BigIntegerField()
    name5 = models.CharField(max_length=100)
    gender5 = models.CharField(db_column='Gender5', max_length=20)  # Field name made lowercase.
    email5 = models.CharField(max_length=100)
    phone5 = models.BigIntegerField()
    name6 = models.CharField(max_length=100)
    gender6 = models.CharField(db_column='Gender6', max_length=10)  # Field name made lowercase.
    email6 = models.CharField(max_length=100)
    phone6 = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'events'
