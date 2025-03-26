from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import PronunciationAssessment, VisemeData, VisemeResult, ChatTable, Story
from .serializers import PronunciationAssessmentSerializer, VisemeResultSerializer
from .utils.chatTableDB import add_chat_db, get_chat_db
from .utils.azure_speech_evaluate import evaluate_pronunciation
from .utils.azure_speech import generate_speech
from .utils.azure_speech_to_text import speech_to_text
from .utils.azure_chat import chat_response
from .utils.azure_story_generate import story_generate
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
  
class SpeechToTextView(APIView):
  parser_classes = (MultiPartParser, FormParser)
  
  @swagger_auto_schema(
		operation_description="上傳音檔並進行語音轉文字",
		manual_parameters=[
			openapi.Parameter(
				'audio', openapi.IN_FORM, description="上傳音檔 (支援格式：wav, mp3)", type=openapi.TYPE_FILE, required=True
			)
		],
		responses={
			200: openapi.Response("語音辨識成功"),
			400: "音檔為提供或辨識失敗",
			500: "伺服器錯誤"
		}
	)
  def post(self, request, *args, **kwargs):
    
    audio_file = request.FILES.get('audio')
    
    if not audio_file:
      return Response({"error": "audio is required"}, status=400)
    
    audio_path = default_storage.save(f"uploads/{audio_file.name}", ContentFile(audio_file.read()))
    full_audio_path = default_storage.path(audio_path)
    
    result = speech_to_text(full_audio_path)
    
    return Response(result, status=200)
  
class ChatTableView(APIView):
  @swagger_auto_schema(
		operation_description="取得所有聊天紀錄"
	)
  def get(self, request):
    try:
      chat_list = get_chat_db()
      data = []
      for chat in chat_list:
        data.append({
					"id": chat.id,
					"user": chat.user,
					"chatText": chat.chatText,
					"timestamp": chat.timestamp
				})
      return Response(data, status=200)
    except Exception as e:
      return Response({"error": str(e)}, status=500)
  
  @swagger_auto_schema(
		operation_summary="新增一筆聊天紀錄",
		manual_parameters=[
			openapi.Parameter(
				'user',
				openapi.IN_QUERY,
				description="使用者名稱 ex: (assistant, user), AI, 使用者",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'chatText',
				openapi.IN_QUERY,
				description="聊天內容",
				type=openapi.TYPE_STRING,
				required=True
			),
		],
		responses={
				201: "對話紀錄新增成功",
				400: "參數缺失",
				500: "伺服器錯誤"
		}
	)
  def post(self, request, *args, **kwargs):
    user = request.query_params.get("user")
    chatText = request.query_params.get("chatText")
    print("user: ", user, "chatText: ", chatText)
    if not user or not chatText:
      return Response({"error": "user and chatText are required"}, status=400)
    
    try:
      add_chat_db(user, chatText)
      return Response({"message": "對話紀錄已成功新增"}, status=200)
    except Exception as e:
      return Response({"error": str(e)}, status=500)
    
class ChatResponseView(APIView):
  
  @swagger_auto_schema(
		operation_description="使用 Azure OpenAI 進行對話回覆，不用新增對話紀錄到資料庫，後端處理",
		manual_parameters=[
			openapi.Parameter(
				'chat_prompt',
				openapi.IN_QUERY,
				description="使用者輸入內容",
				type=openapi.TYPE_STRING,
				required=True
			),
		],
	)
  def post(self, request, *args, **kwargs):
    try:
      chat_prompt = request.query_params.get('chat_prompt')
      response = chat_response(chat_prompt)
      if response:
        return Response({"response": response}, status=200)
      else:
        return Response({"error": "無法取得回應"}, status=500)
    except Exception as e:
      return Response({"error": str(e)}, status=500)

class StoryView(APIView):
  
	@swagger_auto_schema(
		operation_description="使用 Azure OpenAI 進行故事生成",
		manual_parameters=[
			openapi.Parameter(
				'character',
				openapi.IN_QUERY,
				description="角色名稱",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'style',
				openapi.IN_QUERY,
				description="故事風格",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'introduction',
				openapi.IN_QUERY,
				description="開頭（起）",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'development',
				openapi.IN_QUERY,
				description="發展（承）",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'twist',
				openapi.IN_QUERY,
				description="轉折（轉）",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'conclusion',
				openapi.IN_QUERY,
				description="結局（合）",
				type=openapi.TYPE_STRING,
				required=True
			),
		],
		responses={
			200: "成功生成故事",
			400: "參數缺失",
			500: "伺服器錯誤"
		}
	)
	def post(self, request, *args, **kwargs):
		character = request.query_params.get('character')
		style = request.query_params.get('style')
		introduction = request.query_params.get('introduction')
		development = request.query_params.get('development')
		twist = request.query_params.get('twist')
		conclusion = request.query_params.get('conclusion')
  
		print("character: ", character, "style: ", style, "introduction: ", introduction, "development: ", development, "twist: ", twist, "conclusion: ", conclusion)
		
		if not character or not style or not introduction or not development or not twist or not conclusion:
			return Response({"error": "character, style, introduction, development, twist, conclusion are required"}, status=400)
		
		story = Story(
			character = character,
			style = style,
			introduction = introduction,
			development = development,
			twist = twist,
			conclusion = conclusion
		)
		create_story = story_generate(story)
		return Response({"story": create_story}, status=200)