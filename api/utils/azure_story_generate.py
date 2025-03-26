import os
import openai

def build_story_prompt(story):
  return f"""
	你是一位擅長創作故事的作家。請根據以下設定，撰寫一個具有吸引力的故事，依照五段式結構（起、承、轉、合）。
	角色設定：
	{story.character}
	故事風格：
	{story.style}

	開頭（起）：
	{story.introduction}

	發展（承）：
	{story.development}

	轉折（轉）：
	{story.twist}

	結局（合）：
	{story.conclusion}

	請以自然、連貫的方式將這些段落串接成一個完整故事，風格符合上述指定，使用繁體中文，並保持語氣一致、故事流暢。
	因為使用者為18歲以下的學生，請確保故事內容不會太難理解或過於複雜。
	故事需要小於500字，並且不要包含任何色情、暴力或不當用語。
	"""

def story_generate(story):
  
  client = openai.AzureOpenAI(
		api_version=os.environ.get("AZURE_OPENAI_VERSION"),
		azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
		api_key=os.environ.get("AZURE_OPENAI_KEY")
	)
  
  prompt = build_story_prompt(story)
  
  response = client.chat.completions.create(
		model="gpt-4o",
		messages=[{
			"role": "system", "content": "你是一位專業的小說作家，擅長創作吸引人的故事。",
      "role": "user", "content": prompt
		}],
		temperature=0.8,
		max_tokens=500,
	)
  
  return response.choices[0].message.content.strip()