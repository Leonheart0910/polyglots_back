from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_insert import write, read
from gpt_feature import search_word, gen_review, sent_seg
from pydantic import BaseModel
from img_searching_google import search_imgs
import mysql.connector

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안을 위해 필요 시 특정 도메인으로 변경)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

#---회원가입 user 아이디 입력---
class EmailRequest(BaseModel):
    user_email: str

@app.post("/user/insert")
async def insert_user_email(request: EmailRequest):
    """
    Insert a user's email into the database.
    """
    try:
        DB_CONFIG = {
            "host": "43.201.113.85",  # 업데이트 필요
            "port": 3306,
            "user": "ubuntu",
            "password": "****",
            "database": "polyglot_db"
        }

        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        insert_query = "INSERT INTO user (user_email, created_at) VALUES (%s, NOW())"
        cursor.execute(insert_query, (request.user_email,))

        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "Email inserted successfully!"}
    except mysql.connector.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# 데이터 삽입 예시 엔드포인트
@app.post("/db/insert")
async def insert_data(user_email: str, word_origin: str, word_mean: str, word_explain: str, word_example: str):
    try:
        write(user_email, word_origin, word_mean, word_explain, word_example)
        return {"message": "Data inserted successfully!"}
    except Exception as e:
        return -1

# 데이터 읽기 엔드포인트
@app.get("/db/read")
async def read_data():
    try:
        read()
        return {"message": "Data read successfully (check server logs)."}
    except Exception as e:
        return -1

class GPTSearchRequest(BaseModel):
    searching_word: str
    context_sentence: str

@app.post("/gpt/search")
async def gpt_search(request: GPTSearchRequest):
    """
    Endpoint to search for word information using the GPT feature and fetch related images.
    """
    try:
        mother_tongue = "english"
        target_language = "korean"

        searching_word = request.searching_word
        context_sentence = request.context_sentence

        gpt_result = search_word(searching_word, context_sentence, mother_tongue, target_language)
        image_results = search_imgs(searching_word, num_images=12)

        return {
            "gpt_result": gpt_result,
            "image_results": image_results
        }
    except Exception as e:
        return {"error": str(e)}

# FastAPI 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
