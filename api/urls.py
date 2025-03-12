from django.urls import path
from .views import PronunciationAssessmentView
from .views import TextToSpeechView
from .views import VisemeSyncView

urlpatterns = [
    path('evaluate/', PronunciationAssessmentView.as_view(), name='pronunciation-evaluate'),
    path('generate/tts/', TextToSpeechView.as_view(), name='text-to-speech'),
    path('viseme/', VisemeSyncView.as_view(), name='viseme-sync')
]