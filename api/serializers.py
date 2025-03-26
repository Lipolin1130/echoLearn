from rest_framework import serializers
from .models import PronunciationAssessment
from .models import VisemeData, VisemeResult
from .models import ChatTable
from .models import Story
class PronunciationAssessmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = PronunciationAssessment
		fields = '__all__'
  
class VisemeDataSerializer(serializers.Serializer):
	class Meta:
		model = VisemeData
		fields = '__all__'

class VisemeResultSerializer(serializers.Serializer):
	viseme_data = VisemeDataSerializer(many=True, read_only=True)
	audio_file = serializers.FileField()
	class Meta:
		model = VisemeResult
		fields = '__all__'
  
class ChatTableSerializer(serializers.Serializer):
	class Meta:
		model = ChatTable
		fields = '__all__'
  
class StorySerializer(serializers.Serializer):
  class Meta:
    model = Story
    fields = '__all__'