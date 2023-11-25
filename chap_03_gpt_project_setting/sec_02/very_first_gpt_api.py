import openai
import api_keys
import requests
from bs4 import BeautifulSoup

# openai.api_key = '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'
# from api_keys import openai_api_key # API key가 github에 올라가면 폐기되기 때문에 따로 import 했습니다.
openai.api_key = api_keys.openai_api_key  # API key가 github에 올라가면 폐기되기 때문에 따로 import 했습니다.

main_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"  # 마지막 회차를 얻기 위한 주소
basic_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo="  # 임의의 회차를 얻기 위한 주소


# 마지막 회차 정보를 가져옴
def GetLast():
    resp = requests.get(main_url)
    soup = BeautifulSoup(resp.text, "lxml")
    #print(soup)
    result = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])
    s_idx = result.find(" ")
    e_idx = result.find("회")
    return int(result[s_idx + 1: e_idx])


# 지정된 파일에 지정된 범위의 회차 정보를 기록함
def Crawler(s_count, e_count, fp):
    lastStr = ""
    for i in range(s_count, e_count + 1):
        crawler_url = basic_url + str(i)
        resp = requests.get(crawler_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        text = soup.text

        s_idx = text.find(" 당첨결과")
        s_idx = text.find("당첨번호", s_idx) + 4
        e_idx = text.find("보너스", s_idx)
        numbers = text[s_idx:e_idx].strip().split()

        s_idx = e_idx + 3
        e_idx = s_idx + 3
        bonus = text[s_idx:e_idx].strip()

        s_idx = text.find("1등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money1 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("2등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money2 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("3등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money3 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("4등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money4 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("5등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money5 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        line = str(i) + ',' + numbers[0] + ',' + numbers[1] + ',' + numbers[2] + ',' + numbers[3] + ',' + numbers[
            4] + ',' + numbers[5] + ',' + bonus

        # + ',' + money1 + ',' + money2 + ',' + money3 + ',' + money4 + ',' + money5
        # print(line)
        line += '\n'
        lastStr += line
        fp.write(line)
    return lastStr


def ask_to_gpt_35_turbo(user_input, lastStr):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        top_p=0.1,
        temperature=0.1,
        messages=[
            {"role": "system",
             "content": '''You are a competent statistician, and the user is asking a question about Lotto 645 in Korea.
             The data listed next is separated by commas and will tell you the data of the round, 6 winning numbers, and 1 bonus number, the numbers that appear frequently, combinations of consecutive numbers, combinations of odd and even numbers, etc. We analyze it based on the standards of a statistician and create data likely to appear in the next episode. Each set requires 6 numbers, but exclude combinations that have already won. Explain in detail the reason for your selection. Please provide the explanation in Korean.
             Now I will pass on the data.
             {0}
             '''.format(lastStr)},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content


def main():
    print("Start...")
    last = GetLast()  # 마지막 회차를 가져옴

    fp = open('lotto_v{0}_data.csv'.format(last), 'w')
    lastStr = Crawler(last-25, last, fp)  # 처음부터 마지막 회차까지 저장
    #print(lastStr)
    fp.close()

    users_request = '''
    다음 회차에 나올꺼 같은 숫자 조합 5세트만 알려줘 1세트 마다 6개의 숫자를 골라줘
    '''
    r = ask_to_gpt_35_turbo(users_request, lastStr)
    print(r)


main()
