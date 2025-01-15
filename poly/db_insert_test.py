import requests


def test_insert_user_email():
    # FastAPI 서버 URL 및 엔드포인트
    url = "http://43.201.113.85:8000/user/insert"

    # 테스트 데이터
    test_data = {
        "user_email": "testuser@example.com"
    }

    try:
        # POST 요청 보내기
        response = requests.post(url, json=test_data)

        # 응답 상태 코드 확인
        if response.status_code == 200:
            print("Request succeeded.")
            print("Response:", response.json())
        else:
            print(f"Request failed with status code {response.status_code}.")
            print("Response:", response.json())
    except Exception as e:
        print(f"An error occurred: {e}")


# 테스트 실행
if __name__ == "__main__":
    test_insert_user_email()
