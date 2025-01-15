import requests
from bs4 import BeautifulSoup
import base64
from io import BytesIO
from PIL import Image
from typing import List

def fetch_google_images(query, num_images=12):
    #안전빵 12개 리스팅
    # 검색어를 URL 인코딩
    search_query = query.replace(' ', '+')
    url = f'https://www.google.com/search?tbm=isch&q={search_query}'

    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 요청 보내기
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch Google search results")
        return []

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # Base64 데이터 추출
    base64_images = []
    for script in soup.find_all('script'):
        if 'data:image/jpeg;base64,' in script.text:
            start_idx = script.text.find('data:image/jpeg;base64,')
            end_idx = script.text.find(';var', start_idx)
            if end_idx == -1:  # Handle case where ";var" is not found
                end_idx = script.text.find('"', start_idx)
            base64_data = script.text[start_idx:end_idx]
            base64_images.append(base64_data)
            if len(base64_images) >= num_images:
                break

    return base64_images

def fix_base64_padding(base64_data):
    # Base64 문자열 길이를 4로 나눴을 때 나머지가 있다면, '=' 추가
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)
    return base64_data

def get_image_size_from_base64(base64_data):
    try:
        # Base64 문자열에서 데이터 디코딩
        base64_data = fix_base64_padding(base64_data.split(',')[1])  # 'data:image/jpeg;base64,' 부분 제거 및 패딩 복구
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))  # 이미지를 메모리에서 로드

        # 이미지 크기 반환 (너비, 높이)
        return image.size
    except Exception as e:
        print(f"Error decoding Base64 or getting image size: {e}")
        return None

def remove_trailing_data(base64_data):
    try:
        # 마지막에 처음 등장하는 '/'를 기준으로 문자열 분리 및 제거
        last_slash_idx = base64_data.rfind('/')
        if last_slash_idx != -1:
            base64_data = base64_data[:last_slash_idx]
        return base64_data
    except Exception as e:
        print(f"Error processing Base64 data: {e}")
        return base64_data

# 테스트 실행
def search_imgs(query:str, num_images:int = 12)-> List[str]:
    base64_images = fetch_google_images(query, num_images)

    # 크기 조건에 맞는 이미지를 저장할 리스트
    output1 = []
    output2 = []
    output3 = []

    for base64_image in base64_images:
        # 문자열 처리
        cleaned_base64_image = remove_trailing_data(base64_image)

        # 이미지 크기 확인
        size = get_image_size_from_base64(cleaned_base64_image)
        if size and size[0] >= 100 and size[1] >= 100:
            if not output1:
                output1.append(cleaned_base64_image)
            elif not output2:
                output2.append(cleaned_base64_image)
            elif not output3:
                output3.append(cleaned_base64_image)

    img_list = []
    for img in output1:
        img_list.append(img)
        

    
    for img in output2:
        img_list.append(img)


    for img in output3:
        img_list.append(img)

    return img_list

#print(search_imgs("puppies", 12)[0])
