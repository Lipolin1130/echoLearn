from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import PronunciationAssessment
from .serializers import PronunciationAssessmentSerializer
from .azure_speech import evaluate_pronunciation

class PronunciationAssessmentView(APIView):
	parser_classes = (MultiPartParser, FormParser)

	@swagger_auto_schema(
			operation_description="上傳音檔並進行發音評估",
			request_body=openapi.Schema(
					type=openapi.TYPE_OBJECT,
					properties={
							'audio': openapi.Schema(
									type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY,
									description="上傳音檔 (wav, mp3 等格式)"
							),
							'text': openapi.Schema(
									type=openapi.TYPE_STRING,
									description="用來比對的參考文本"
							)
					},
					required=['audio', 'text']
			),
			responses={
					201: PronunciationAssessmentSerializer(),
					400: openapi.Response("Bad Request: 缺少必要參數或評估失敗")
			}
    )
	def post(self, request, *ages, **kwargs):
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
  
		return Response(serializer.data, status=201)