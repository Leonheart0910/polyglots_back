from openai import OpenAI
from typing import List

openai_api_key = "no key"
client = OpenAI(api_key = openai_api_key)


def search_word(searching_word:str, context_sentence:str, mother_tongue:str, target_language:str)->str:
    """Todo: Implementing exception when the response is not following the format.
    searching_word: The word that the user tries to search for the corresponding word in his/her mother tongue.
    context_sentence: The sentence that includes the searching_word
    mother_tongue: The user's mother tougue.
    target_language: The language that the user is learning."""
    system_message_content = f"You are language learner assistant. You should yield a response in the designated format.\nThe response format is following:\ntranslated word into {mother_tongue}/the meaning of the word in the context explained in the {mother_tongue}/a simple example sentence in {target_language} with the queried word"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message_content},
                {"role": "user", "content": f"원어 문장: {context_sentence}\n사용자가 모르는 단어: {searching_word}"}],
        stream=False,
        temperature=0,
        max_completion_tokens=512
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def gen_review(searched_words:List[str], target_language)->str:
    """No need to implement the exception
    searched_words: The words in our database which are searched by user in the past.
    target_language: The language that the user is learning."""
    if not searched_words:
        return -1
    system_message_content = f"You are language learner assistant. Your task is to generate a complex sentence into a single paragraph in {target_language}. The paragraph must include all the words included in the given list and be completed within 2048 tokens. The words in the list are seperated by comma."
    words = ""
    for word in searched_words:
        words += word
        words += ", "
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message_content},
                {"role": "user", "content": f"{words}"}],
        stream=False,
        temperature=0,
        max_completion_tokens=2048
    )
    return response.choices[0].message.content


def sent_seg(complex_sentence:str, mother_tongue:str, target_language:str)->str:
    """No need to implement the exception
    mother_tongue: The user's mother tougue.
    target_language: The language that the user is learning."""
    system_message_content = f"You are language learner assistant. Your task is to decompose a complex sentence into two or more simple sentences. Simple sentence refers to a sentence with at least one noun and one verb. Each sentence must be separated by slash(/) with no space"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message_content},
                {"role": "user", "content": f"{complex_sentence}"}],
        stream=False,
        temperature=0,
        max_completion_tokens=2048
    )
    return response.choices[0].message.content

#search_word("hello", "This is hello", "korean", "en")