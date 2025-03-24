import azure.cognitiveservices.speech as speechsdk
import os


def speech_to_text(audio_path):
  print("開始語音轉文字...")
  
  try:
    speech_config = speechsdk.SpeechConfig(
			subscription=os.environ.get("AZURE_SPEECH_KEY"),
			region=os.environ.get("AZURE_SPEECH_REGION")
		)
    
    speech_config.speech_recognition_language = "zh-TW"
    
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    result = recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
      return {
				"text": result.text
			}
    elif result.reason == speechsdk.ResultReason.NoMatch:
      return {
				"error": "未能辨識語音"
			}
    else: return {
			"error": "語音辨識失敗"
		}
  except Exception as e:
    return {
			"error": str(e)
		}
  finally:
    if os.path.exists(audio_path):
      os.remove(audio_path)