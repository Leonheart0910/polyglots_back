from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_insert import write_word, read
from gpt_feature import search_word, gen_review, sent_seg
from pydantic import BaseModel
from img_searching_google import search_imgs
import mysql.connector
from typing import List, Optional

app = FastAPI()

#page - 1 (login)
#------------------------------------------------------------------------------#
# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안을 위해 필요 시 특정 도메인으로 변경)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# ---회원가입 user 아이디 입력---
class EmailRequest(BaseModel):
    user_email: str

@app.post("/user/insert")
async def insert_user_email(request: EmailRequest):
    """
    Insert a user's email into the database. If the email already exists, return the existing user_id.
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
        cursor = connection.cursor(dictionary=True)

        # Check if the email already exists
        select_query = "SELECT user_id FROM user WHERE user_email = %s"
        cursor.execute(select_query, (request.user_email,))
        result = cursor.fetchone()

        if result:
            user_id = result['user_id']
        else:
            # Insert new email into the database
            insert_query = "INSERT INTO user (user_email, created_at) VALUES (%s, NOW())"
            cursor.execute(insert_query, (request.user_email,))
            connection.commit()

            # Retrieve the newly inserted user_id
            user_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return {"message": "Email processed successfully!", "user_id": user_id}

    except mysql.connector.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



#page - 2 (feat 1 : 단어풀이 및 사진참조) * db 에 저장
#------------------------------------------------------------------------------#

class GPTSearchRequest(BaseModel):
    user_id : int
    searching_word: str
    context_sentence: str
    target_language: str


@app.post("/gpt/search")
async def gpt_search(request: GPTSearchRequest):
    """
    Endpoint to search for word information using the GPT feature and fetch related images.
    """
    try:
        mother_tongue = "english"
        target_language = request.target_language

        user_id = int(request.user_id)
        searching_word = request.searching_word
        context_sentence = request.context_sentence
        # Call GPT feature to get the result
        gpt_result = search_word(searching_word, context_sentence, mother_tongue, target_language)

        # Split the GPT result
        try:
            word_mean, word_explain, word_example = gpt_result.split("/")
        except ValueError:
            return {"error": "GPT result format is invalid. Expected format: 'word_mean/word_explain/word_example'"}

        # Example: Replace this with the email of the user
        user_email = "testuser@example.com"  # You can modify this to accept email dynamically

        # Write to the database
        write_word(user_id, searching_word, word_mean, word_explain, word_example)

        # Fetch related images
        image_results = search_imgs(searching_word, num_images=12)

        return {
            "gpt_result": gpt_result,
            "image_results": image_results
        }
    except Exception as e:
        return {"error": str(e)}



#------------------------------------------------------------------------------#
# 복합적인 문장을 split 하여 쉬운 문장 여러개로 분할 하는 post api

class SentenceSegmentationRequest(BaseModel):
    complex_sentence: str
    target_language: str

@app.post("/gpt/sentence-segment")
async def sentence_segment(request: SentenceSegmentationRequest):
    """
    Endpoint to segment a complex sentence into multiple simple sentences.
    """
    try:
        # Extract parameters from the request
        complex_sentence = request.complex_sentence
        mother_tongue = "english"
        target_language = request.target_language

        # Call the sent_seg function from gpt_feature.py
        segmented_sentence = sent_seg(complex_sentence, mother_tongue, target_language)

        return {
            "original_sentence": complex_sentence,
            "segmented_sentence": segmented_sentence
        }
    except Exception as e:
        return {"error": str(e)}


#------------------------------------------------------------------------------#
# feat - page 4 review를 위한 DB read

# Request 모델 정의
class ReadWordsRequest(BaseModel):
    user_id: int
    max_words: Optional[int] = 5  # 최대 읽어올 단어 개수 (기본값: 5)
    target_language: str  # 추가: 학습할 언어

@app.post("/db/read-words")
async def read_words(request: ReadWordsRequest):
    connection = None
    try:
        DB_CONFIG = {
            "host": "43.201.113.85",  # 업데이트 필요
            "port": 3306,
            "user": "ubuntu",
            "password": "****",
            "database": "polyglot_db"
        }
        # DB 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database")
        else:
            return {"error": "Failed to connect to the database"}

        cursor = connection.cursor()

        # user_id로 word_origin 데이터 읽기 (updated_at 기준 오래된 순)
        query = """
        SELECT word_origin
        FROM word_review
        WHERE user_id = %s
        ORDER BY updated_at ASC
        LIMIT %s
        """

        cursor.execute(query, (request.user_id, request.max_words))
        rows = cursor.fetchall()

        # word_origin 리스트 생성
        words = [row[0] for row in rows] if rows else []

        # words 리스트를 gen_review에 넣어 문단 생성
        if not words:
            return {"error": "No words found for the given user_id"}

        paragraph = gen_review(searched_words=words, target_language=request.target_language)

        return {
            "paragraph": paragraph
        }

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"error": f"Database error: {str(e)}"}

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")



# 데이터 읽기 엔드포인트
@app.get("/db/read")
async def read_data():
    try:
        read()
        return {"message": "Data read successfully (check server logs)."}
    except Exception as e:
        return -1

# FastAPI 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
