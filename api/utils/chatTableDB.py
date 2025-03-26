import mysql.connector
import os
from ..models import ChatTable
from mysql.connector import Error
from datetime import datetime

def create_connection():
  try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),  # 根據你的 MySQL 伺服器配置來修改
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_NAME'),  # 請替換成你的資料庫名稱
            user=os.environ.get('DB_USER'),  # 你的 MySQL 使用者名稱
            password=os.environ.get('DB_PASS')  # 你的 MySQL 密碼
        )
        if connection.is_connected():
            print("成功連接到資料庫")
            return connection
  except Error as e:
			print(f"錯誤: {e}")
			return None
    
def add_chat_db(user, chatText): # 新增對話紀錄到 mySQL
	connection = create_connection()
	try:
		cursor = connection.cursor()
		query = "INSERT INTO ChatTable (user, chatText) VALUES (%s, %s)"
		values = (user, chatText)
		cursor.execute(query, values)
		connection.commit()
		print("對話紀錄已成功新增")
	except Error as e:
		print(f"新增錯誤: {e}")
	finally:
		cursor.close()
		connection.close()
  
def get_chat_db(): # 取得 mySQL 中的所有對話紀錄
	connection = create_connection()
	chat_list = []
	if connection:
		try:
			cursor = connection.cursor()
			query = "select id, user, chatText, timestamp from ChatTable"
			cursor.execute(query)
			records = cursor.fetchall()
			print(records)
			for row in records:
				chat = ChatTable(
					id=row[0],
					user=row[1],
					chatText=row[2],
					timestamp=row[3] if isinstance(row[3], datetime) else datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
				)
				chat_list.append(chat)
		except Error as e:
			print(f"讀取錯誤: {e}")
		finally:
			cursor.close()
			connection.close()
	return chat_list