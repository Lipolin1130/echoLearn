from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import PronunciationAssessment
from .serializers import PronunciationAssessmentSerializer
from .azure_speech import evaluate_pronunciation
import os

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