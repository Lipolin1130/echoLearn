import azure.cognitiveservices.speech as speechsdk
from ..utils.azure_pronunciation_feedback import get_pronunciation_feedback
import os

def evaluate_pronunciation(audio_path, reference_text):
  try:
    speech_config = speechsdk.SpeechConfig(
      subscription=os.environ.get("AZURE_SPEECH_KEY"),
      region=os.environ.get("AZURE_SPEECH_REGION")
		)
    speech_config.speech_recognition_language = "zh-CN"
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
			reference_text=reference_text,
			grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
			granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
			enable_miscue=False
		)
    recognizer = speechsdk.SpeechRecognizer(
			speech_config=speech_config,
			audio_config=audio_config
		)

    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
      pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
      
      suggestion = get_pronunciation_feedback(pronunciation_result)
      
      return {
				"accuracy_score": pronunciation_result.accuracy_score,
				"fluency_score": pronunciation_result.fluency_score,
				"completeness_score": pronunciation_result.completeness_score,
				"pronunciation_score": pronunciation_result.pronunciation_score,
				"suggestion": suggestion
			}
    else:
      return {
				"error": "Speech recognition failed"
			}
  except Exception as e:
    return {
			"error": str(e)
		}
  finally:
    if os.path.exists(audio_path):
      os.remove(audio_path)