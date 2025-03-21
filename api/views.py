from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import PronunciationAssessment, VisemeData, VisemeResult
from .serializers import PronunciationAssessmentSerializer, VisemeResultSerializer

from .utils.azure_speech_evaluate import evaluate_pronunciation
from .utils.azure_speech import generate_speech
import json

class PronunciationAssessmentView(APIView):
	parser_classes = (MultiPartParser, FormParser)
	serializer_class = PronunciationAssessmentSerializer

	@swagger_auto_schema(
		operation_summary="上傳音檔並進行發音評估",
		operation_description="使用 Azure Speech 進行發音評估，回傳準確度、流暢度、完整度、總體發音分數與錯誤資訊。",
		consumes=["multipart/form-data"],
		manual_parameters=[
			openapi.Parameter(
            'audio',
            openapi.IN_FORM,
            description="上傳音檔 (支援格式：wav, mp3)",
            type=openapi.TYPE_FILE,
            required=True
        ),
        openapi.Parameter(
            'text',
            openapi.IN_FORM,
            description="用來比對的參考文本",
            type=openapi.TYPE_STRING,
            required=True
        ),
		],
		responses={
				200: PronunciationAssessmentSerializer(),
				400: openapi.Response("Bad Request: 缺少必要參數或評估失敗")
		}
	)
	def post(self, request, *args, **kwargs):
		audio_file = request.FILES.get("audio")
		reference_text = request.data.get('text')
  
		if not audio_file or not reference_text:
			return Response({"error": "audio and text are required"}, status=400)
		
		audio_path = default_storage.save(f"uploads/{audio_file.name}", ContentFile(audio_file.read()))
		full_audio_path = default_storage.path(audio_path)
		
		result = evaluate_pronunciation(full_audio_path, reference_text)
		if "error" in result:
			return Response(result, status=400)

		assessment = PronunciationAssessment.objects.create(**result)
		serializer = PronunciationAssessmentSerializer(assessment)
  
		return Response(serializer.data, status=200)

class TextToSpeechView(APIView):
  @swagger_auto_schema(
		operation_description="文字轉語音(TTS)",
		operation_summary="使用 Azure Speech 進行文字轉語音，回傳 wav 音檔。",
		manual_parameters=[
			openapi.Parameter(
				'text',
				openapi.IN_QUERY,
				description="要轉換的文字",
				type=openapi.TYPE_STRING,
				required=True
			),
		],
		responses={
			200: "成功回傳 wav 音檔",
			400: "請求錯誤"
		}
	)
  def get(self, request, *args, **kwargs):
    
    text = request.GET.get("text", "")
    
    if not text:
      return Response({"error": "text is required"}, status=400)
    
    audio_path = generate_speech(text)
    
    if audio_path:
      return FileResponse(open(audio_path, "rb"), as_attachment=True, filename="tts_output.wav")
    else:
      return Response({"error": "語音合成失敗"}, status=500)
    
class VisemeSyncView(APIView):
  """
  產生語音並返回 Viseme (嘴形動畫同步數據)
  """
  
  @swagger_auto_schema(
		operation_summary="文字轉語音 + Viseme 嘴形同步",
		operation_description="使用 Azure Speech 產生語音並提取 Viseme 嘴型同步數據",
		manual_parameters=[
			openapi.Parameter(
				'text',
				openapi.IN_QUERY,
				description="要轉換為語音的文字",
				type=openapi.TYPE_STRING,
				required=True
			),
		],
		responses={
			200: VisemeResultSerializer(),
			400: "請求錯誤"
		}
	)
  def get(self, request, *args, **kwargs):
    """
    取得輸入文字，產生語音並返回 Viseme 嘴形同步數據
    """
    
    text = request.GET.get("text", "")
    
    if not text:
      return Response({"error": "請提供文本內容"}, status=400)
    
    output_filename, viseme_data_raw = generate_speech(text, return_viseme=True)
    
    print("call Data: ", viseme_data_raw, output_filename)
    
    if output_filename is None or viseme_data_raw is None or not viseme_data_raw:
      return Response({"error": "語音合成失敗，未獲取 Viseme 數據"}, status=500)
      
    response = FileResponse(open(output_filename, "rb"), as_attachment=True, filename="tts_output.wav")
    response["Viseme-Data"] = json.dumps(viseme_data_raw)
    
    return response