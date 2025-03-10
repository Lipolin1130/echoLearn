import azure.cognitiveservices.speech as speechsdk
from django.test import TestCase
import os

AZURE_SPEECH_KEY = "AkC9lQuqDKfrIxWP2sSvBs2kuFi3IYIQ0cAwDsAtH7LOB0hCmIgtJQQJ99BCACHYHv6XJ3w3AAAAACOG5bCi"
AZURE_SPEECH_REGION = "eastus2"

class AzurePronunciationAssessmentTest(TestCase):
    def test_pronunciation_assessment(self):
        """
        測試 Azure Speech Service 的繁體中文發音評估
        """
        try:
            # 設定 Azure 語音服務
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
            speech_config.speech_recognition_language = "zh-TW"  # 設定為台灣繁體中文

            # 測試音訊檔案
            audio_file_path = "/Users/funghi/Documents/Contest/AI EXPO/EchoLearn/echoLearnProject/assets/Text to Speech.wav"
            if not os.path.exists(audio_file_path):
                self.fail(f"音訊檔案不存在: {audio_file_path}")

            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

            # **設定發音評估參考文本**
            reference_text = "這是語音轉文字可不可以使用"  # 這應該與音訊檔案內容相符

            # 設定發音評估配置
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,  # 100 分制
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,  # 細到音素級
                enable_miscue=True  # 允許錯誤檢測
            )

            # 建立語音辨識器
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            # 套用發音評估設定
            pronunciation_config.apply_to(recognizer)

            print("開始發音評估...")
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # 取得發音評估結果
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)

                print(f"辨識結果: {result.text}")
                print(f"準確度分數 (Accuracy): {pronunciation_result.accuracy_score}")
                print(f"流暢度分數 (Fluency): {pronunciation_result.fluency_score}")
                print(f"完整度分數 (Completeness): {pronunciation_result.completeness_score}")
                print(f"總體發音分數 (Pronunciation): {pronunciation_result.pronunciation_score}")

                # 驗證評分是否合理（可以根據需求調整門檻）
                self.assertGreaterEqual(pronunciation_result.accuracy_score, 0)
                self.assertGreaterEqual(pronunciation_result.fluency_score, 0)
                self.assertGreaterEqual(pronunciation_result.completeness_score, 0)
                self.assertGreaterEqual(pronunciation_result.pronunciation_score, 0)

            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.fail("未能辨識語音")
            else:
                self.fail(f"語音辨識失敗: {result.reason}")

        except Exception as e:
            self.fail(f"測試失敗: {str(e)}")