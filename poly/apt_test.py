import requests

url = "http://127.0.0.1:8000/gpt/search"
data = {
    "searching_word": "legings",
    "context_sentence": "I am wearing pretty legings"
}

# POST 요청 보내기
response = requests.post(url, json=data)

# 응답 데이터 출력
response_data = response.json()
print("Full Response:", response_data)

# 이미지 결과 추출
if "image_results" in response_data and response_data["image_results"]:
    first_image = response_data["image_results"][0]
    print("First Image (Base64):", first_image)
else:
    print("No images found in the response.")
