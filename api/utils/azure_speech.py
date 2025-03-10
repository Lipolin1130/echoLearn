import azure.cognitiveservices.speech as speechsdk
import os

def generate_speech(text, output_filename='tts_output.wav'):
  try:
    speech_config = speechsdk.SpeechConfig(
		subscription=os.environ.get("AZURE_SPEECH_KEY"),
		region=os.environ.get("AZURE_SPEECH_REGION")
    )
    speech_config.speech_synthesis_voice_name = "zh-TW-HsiaoChenNeural"

    '''
    zh-TW-HsiaoChenNeural (女性)
    zh-TW-YunJheNeural (男性)
    zh-TW-HsiaoYuNeural (女性)
    '''

    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
      print("語音合成成功！已儲存為 tts_output.wav")
      return output_filename
    elif result.reason == speechsdk.ResultReason.Canceled:
      cancellation_details = result.cancellation_details
      print(f"語音合成失敗: {cancellation_details.reason}")
      return None
  except Exception as e:
    print(f"語音合成失敗: {e}")
    return None