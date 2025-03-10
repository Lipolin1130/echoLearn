from rest_framework import serializers
from .models import PronunciationAssessment
  
class PronunciationAssessmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = PronunciationAssessment
		fields = '__all__'