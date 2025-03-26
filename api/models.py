from django.db import models
from dataclasses import dataclass
from typing import List

# Create your models here.

class PronunciationAssessment(models.Model):
	accuracy_score = models.FloatField() # 準確度分數
	fluency_score = models.FloatField() # 流暢度分數
	completeness_score = models.FloatField() # 完整度分數
	pronunciation_score = models.FloatField() # 總體發音分數
	suggestion = models.TextField(default="") # 建議

class VisemeData(models.Model):
  viseme_id = models.IntegerField()
  timestamp = models.DecimalField(max_digits=10, decimal_places=2) #單位：毫秒
  
class VisemeResult(models.Model):
  audio_file = models.FileField(upload_to="viseme_audio/")
  viseme_data = models.ManyToManyField(VisemeData)
  
class ChatTable(models.Model):
  id = models.AutoField(primary_key=True)
  user = models.TextField(default="")
  chatText = models.TextField(default="")
  timestamp = models.DateTimeField()