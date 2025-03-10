from django.urls import path
from .views import PronunciationAssessmentView

urlpatterns = [
    path('evaluate/', PronunciationAssessmentView.as_view(), name='pronunciation-evaluate'),
]