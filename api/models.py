from django.db import models

# Create your models here.

class PronunciationAssessment(models.Model):
	accuracy_score = models.FloatField() # 準確度分數
	fluency_score = models.FloatField() # 流暢度分數
	completeness_score = models.FloatField() # 完整度分數
	pronunciation_score = models.FloatField() # 總體發音分數
	errors = models.JSONField(default=list)