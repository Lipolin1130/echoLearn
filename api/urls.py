from django.urls import path
from .views import PronunciationAssessmentView
from .views import TextToSpeechView

urlpatterns = [
    path('evaluate/', PronunciationAssessmentView.as_view(), name='pronunciation-evaluate'),
    path('generate/tts/', TextToSpeechView.as_view(), name='text-to-speech'),
]