import mysql.connector
from mysql.connector import Error

# MySQL 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "43.201.113.85",
    "port": 3306,
    "user": "ubuntu",
    "password": "****",
    "database": "polyglot_db"
}

# User 테이블에 데이터 삽입 함수 (write_user)
def write_user(user_email):
    connection = None  # 초기화
    try:
        # DB 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database")
        else:
            print("Connection failed")
            return None

        cursor = connection.cursor()

        # User 테이블에 데이터 삽입
        user_query = "INSERT INTO user (user_email, created_at) VALUES (%s, NOW())"
        cursor.execute(user_query, (user_email,))
        user_id = cursor.lastrowid  # 삽입된 User의 ID 가져오기

        connection.commit()
        print("User inserted successfully!")
        return user_id

    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Word_Review 테이블에 데이터 삽입 함수 (write_word)
def write_word(user_id, word_origin, word_mean, word_explain, word_example):
    connection = None  # 초기화
    try:
        # DB 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database")
        else:
            print("Connection failed")
            return

        cursor = connection.cursor()

        # Word_Review 테이블에 데이터 삽입
        review_query = """
        INSERT INTO word_review (user_id, word_origin, word_mean, word_explain, word_example, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(review_query, (user_id, word_origin, word_mean, word_explain, word_example))

        # 트랜잭션 커밋
        connection.commit()
        print("Word review inserted successfully!")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def read():
    connection = None  # 초기화
    try:
        # DB 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database")
        else:
            print("Connection failed")
            return

        cursor = connection.cursor()

        # JOIN을 사용하여 두 테이블의 데이터 읽기
        query = """
        SELECT u.user_id, u.user_email, w.word_mean, w.word_explain, w.word_example, w.created_at
        FROM user u
        JOIN word_review w ON u.user_id = w.user_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # 결과 출력
        for row in rows:
            print(f"User ID: {row[0]}, Email: {row[1]}, Word: {row[2]}, Explanation: {row[3]}, Example: {row[4]}, Created At: {row[5]}")

    except Error as e:
        print(f"Error: {e}")
        return {"error": str(e)}  # 에러 메시지를 반환
    finally:
        # connection이 초기화되었는지 확인 후 닫기
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")

# 테스트 실행
if __name__ == "__main__":

    # SELECT 테스트
    read()
