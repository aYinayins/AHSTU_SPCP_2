import random
import uuid
import ddddocr
import requests
import json
from requests import utils
from bs4 import BeautifulSoup
import datetime

# 生成32为uuid
def getUUID():
    return "".join(str(uuid.uuid4())).upper()


# token
token = '024240e3304643aba98c6b37df45d725'


def push(key, title, content):  # 函数用来发送填报失败信息
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": key,
        "title": title,
        "content": "<xmp>" + content + "</xmp>"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    requests.post(url, data=body, headers=headers)


# 验证码url
captchaUrl = "https://xg.fjsdxy.com/SPCP/Web/Account/GetLoginVCode"


def login():
    try:
        # 如果网络请求没有错误并且为其他错误，执行体温填报处理
        while True:
            # 验证码请求
            response = requests.post(url=captchaUrl, timeout=5)
            ocr = ddddocr.DdddOcr()
            image_bytes = response.content
            res = ocr.classification(image_bytes)       

            # 获取cookie
            cookies = response.cookies
            SessionId = utils.dict_from_cookiejar(cookies)['ASP.NET_SessionId']
            print (cookies)
            # 登录链接
            url = "https://xg.fjsdxy.com/SPCP/Web"
            ReSubmitFlag = getUUID()

            # 帐号信息
            login = {
                'ReSubmitFlag': ReSubmitFlag, 
                'StuLoginMode': '1',
                'txtUid': '1326200224',
                'txtPwd': '130054',
                'code': res
            }

            # cookies
            cookies = {
                'ASP.NET_SessionId': SessionId
            }

            # 创建session
            session = requests.Session()

            # 设置浏览器headers，这里用的我的浏览器信息，需要改的话，自己修改
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}

            # 验证码错误提示
            request = session.post(
                url=url, headers=headers, cookies=cookies, data=login)
            soup = BeautifulSoup(request.text, features='html.parser')
            soup = format(soup.select("script")[2]).split('\'')[1]
            # 这边可以整个推送获取状态
            # push(token, '验证码验证提示', soup)

    except requests.exceptions.ConnectTimeout:
        print("网络请求失败，学校服务器上游拒绝接受请求")
        push(token, '网络请求失败', '疫情填报登录失败，请检查平台是否能正常访问！')

    except:
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        data = {'TimeNowHour': hour, 'TimeNowMinute': minute,
                'Temper1': '36', 'Temper2': random.randint(0, 9)}
        print("登录成功,正在执行体温填报任务")
        push(token, '登录成功', '正在执行体温填报任务')
        # 这边可以整个推送获取状态
        StuTemperatureInfo = session.post(
            'https://xg.fjsdxy.com/SPCP/Web/Temperature/StuTemperatureInfo', headers=headers, data=data)
        soup = BeautifulSoup(StuTemperatureInfo.text, features='html.parser')
        soup = format(soup.select("script")[2]).split('\'')[1]
        push(token, '体温填报情况', soup)
        print(soup)
        return soup


if __name__ == '__main__':
    login()

