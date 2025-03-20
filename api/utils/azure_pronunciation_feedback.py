import os
import openai

endpoint =  "https://lipol-m85mbe2y-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
subscription_key = "BXZzIwfzP0UooUNC2YQhZhNgY3IFgH0UcVlyVBbk6yQzktIh9yv5JQQJ99BCACfhMk5XJ3w3AAAAACOGbAZz"
api_version = "2024-12-01-preview"
deployment = "gpt-4o"

def get_pronunciation_feedback(pronunciation_result): # PronunciationAssessmentConfig
  
	client = openai.AzureOpenAI(
		api_version=api_version,
		# api_version=os.environ.get("AZURE_OPENAI_VERSION"),
		azure_endpoint=endpoint,
		# azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
		api_key=subscription_key,
		# api_key=os.environ.get("AZURE_OPENAI_API_KEY")
	)

	accuracy_score = pronunciation_result.accuracy_score
	fluency_score = pronunciation_result.fluency_score
	completeness_score = pronunciation_result.completeness_score
	pronunciation_score = pronunciation_result.pronunciation_score

	words = []
	for word in pronunciation_result.words:
		words.append({
				"word": word.word,
				"accuracy_score": word.accuracy_score,
				"error_type": word.error_type
		})
  
	prompt = f"""
	你是一位專業的語音老師，擅長指導 16 歲以下的學生提升發音能力。請根據學生的發音評估結果提供 **清晰、簡單且具體** 的建議。

	### **整體發音評估**
	- 準確度: {accuracy_score}
	- 流暢度: {fluency_score}
	- 完整度: {completeness_score}
	- 發音分數: {pronunciation_score}

	### **發音建議**
	1. **如果發音分數高於 85 分**，請給予學生鼓勵，例如「你的發音表現非常棒！」，不需要詳細建議。
	2. **如果發音分數低於 85 分**，請針對發音錯誤的單詞提供具體的發音技巧與練習方法：
	"""

	# 只處理有錯誤的單詞
	problem_words = [word for word in words if word["accuracy_score"] < 85]

	if problem_words:
			prompt += "\n\n### **需要改善的單詞**\n"
			for word in problem_words:
					prompt += f"\n- **{word['word']}** (準確度: {word['accuracy_score']}): {word['error_type']} → "
					prompt += "請提供具體的發音矯正技巧與簡單易懂的練習方法。\n"

	prompt += """
	### **重要提醒**
	- 只提供需要改善的單詞的建議，不要對流暢度或完整度給過多解釋。
	- 如果學生表現很好，請簡單給予正向回饋，不要強調錯誤。
	- 你的回應應該清楚、簡單且適合 16 歲以下的學生理解。
	- **請確保建議句子的長度不超過 50 字，避免使用複雜的專業術語。**
	"""

	try:
			response = client.chat.completions.create(
					model=deployment,
					messages=[
							{"role": "system", "content": "你是一位專業的語音老師，專門協助學生改善發音技巧。"},
							{"role": "user", "content": prompt}
					],
					max_tokens=500
			)

			return response.choices[0].message.content.strip()

	except openai.OpenAIError as e:
		return f"OpenAI API request error: {str(e)}"