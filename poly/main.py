from fastapi import FastAPI
from db_insert import write, read
from gpt_feature import search_word, gen_review, sent_seg
from pydantic import BaseModel
from img_searching_google import search_imgs

app = FastAPI()

# 데이터 삽입 예시 엔드포인트
@app.post("/db/insert")
async def insert_data(user_email: str, word_origin: str, word_mean: str, word_explain: str, word_example: str):
    try:
        write(user_email, word_origin, word_mean, word_explain, word_example)
        return {"message": "Data inserted successfully!"}
    except Exception as e:
        return {"error": str(e)}

# 데이터 읽기 엔드포인트
@app.get("/db/read")
async def read_data():
    try:
        read()  # 이 함수는 결과를 print로 출력합니다.
        return {"message": "Data read successfully (check server logs)."}
    except Exception as e:
        return {"error": str(e)}

# GPT-기능: 단어 검색 엔드포인트

"""
@app.post("/gpt/search")
async def gpt_search(searching_word: str, context_sentence: str, mother_tongue: str, target_language: str):
    try:
        result = search_word(searching_word, context_sentence, mother_tongue, target_language)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# GPT-기능: 리뷰 생성 엔드포인트
@app.post("/gpt/review")
async def gpt_review(searched_words: list, target_language: str):
    try:
        result = gen_review(searched_words, target_language)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# GPT-기능: 문장 분리 엔드포인트
@app.post("/gpt/sent_seg")
async def gpt_sentence_segmentation(complex_sentence: str, mother_tongue: str, target_language: str):
    try:
        result = sent_seg(complex_sentence, mother_tongue, target_language)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# 이미지 검색 엔드포인트
@app.get("/images/search")
async def image_search(query: str, num_images: int = 12):
    try:
        images = search_imgs(query, num_images)
        return {"images": images}
    except Exception as e:
        return {"error": str(e)}
"""

class GPTSearchRequest(BaseModel):
    searching_word: str
    context_sentence: str

@app.post("/gpt/search")
async def gpt_search(request: GPTSearchRequest):
    """
    Endpoint to search for word information using the GPT feature and fetch related images.
    Args:
        request (GPTSearchRequest): The request containing searching_word and context_sentence.
    Returns:
        dict: The result or error message, including GPT search result and image search result.
    """
    try:
        # Language parameters
        mother_tongue = "korean"  # Replace with appropriate value or accept from frontend
        target_language = "english"  # Replace with appropriate value or accept from frontend

        # Extract values from request object
        searching_word = request.searching_word
        context_sentence = request.context_sentence

        # Call the search_word function
        gpt_result = search_word(searching_word, context_sentence, mother_tongue, target_language)

        # Call the search_imgs function for image search
        image_results = search_imgs(searching_word, num_images=12)  # Fetch top 3 images

        # Return both GPT and image search results to the frontend
        return {
            "gpt_result": gpt_result,
            "image_results": image_results
        }
    except Exception as e:
        return {"error": str(e)}


# FastAPI 실행 테스트
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
