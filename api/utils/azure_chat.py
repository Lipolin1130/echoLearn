import os
import openai
from .chatTableDB import add_chat_db, get_chat_db

def chat_response(chat_prompt): # 使用 Azure OpenAI 進行對話回覆對話結果，並儲存進 MySQL
  
  client = openai.AzureOpenAI(
		api_version=os.environ.get("AZURE_OPENAI_VERSION"),
		azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
		api_key=os.environ.get("AZURE_OPENAI_KEY")
	)
  
  # 從 mySQL 取得過去的對話紀錄
  add_chat_db("user", chat_prompt)
  
  history = get_chat_db()
  
  messages = []
  
  for chat in history:
    messages.append({
			"role": chat.user,
			"content": chat.chatText
		})
  
  prompt = f"""
  以上內容為過去的對話，最後一筆為使用者的最新問題，內容需要在 150 內回覆，並判斷此句對話是否為延伸話題，若是，則回覆延伸話題，若否，則回覆新話題。
  """
  
  try:
    response = client.chat.completions.create(
			model="gpt-4o",
			messages=messages,
      temperature=0.7,
      max_tokens=150
		)
    
    reply = response.choices[0].message.content.strip()
    
    add_chat_db("assistant", reply)
    
    return reply
  except Exception as e:
    print(f"Error: {e}")