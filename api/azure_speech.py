import azure.cognitiveservices.speech as speechsdk
import os

def evaluate_pronunciation(audio_path, reference_text):
  try:
    
    speech_config = speechsdk.SpeechConfig(
      subscription=os.environ.get("AZURE_SPEECH_KEY"),
      region=os.environ.get("AZURE_SPEECH_REGION")
		)
    speech_config.speech_recognition_language = "zh-TW"
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
			reference_text=reference_text,
			grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
			granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
			enable_miscue=True
		)
    recognizer = speechsdk.SpeechRecognizer(
			speech_config=speech_config,
			audio_config=audio_config
		)

    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
      pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
      
      errors = getattr(pronunciation_result, "errors", [])
      
      return {
				"accuracy_score": pronunciation_result.accuracy_score,
				"fluency_score": pronunciation_result.fluency_score,
				"completeness_score": pronunciation_result.completeness_score,
				"pronunciation_score": pronunciation_result.pronunciation_score,
				"errors": errors if errors else []
			}
    else:
      return {
				"error": "Speech recognition failed"
			}
  except Exception as e:
    return {
			"error": str(e)
		}