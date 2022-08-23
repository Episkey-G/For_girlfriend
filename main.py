from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from zhdate import ZhDate

today = datetime.now() + timedelta(hours=8)
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday1 = os.environ['BIRTHDAY1']
birthday2 = os.environ['BIRTHDAY2']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://wthrcdn.etouch.cn/weather_mini?city=" + city
  res = requests.get(url).json()
  weather = res['data']['forecast'][0]
  wendu = res['data']
  return weather['type'], wendu['wendu'], weather['high'], weather['low']

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday(birthday):
  data = birthday.split("-")
  next = ZhDate(date.today().year, int(data[0]), int(data[1]))
  if (next - datetime.now() < 0):
    next = ZhDate(date.today().year + 1, int(data[0]), int(data[1]))
  return (next.to_datetime() - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, highest, lowest = get_weather()
data = {"date":{"value":today.strftime('%Y年%m月%d日'),"color":get_random_color()},"weather":{"value":wea,"color":get_random_color()},"temperature":{"value":temperature,"color":get_random_color()},"love_days":{"value":get_count(),"color":get_random_color()},"birthday1":{"value":get_birthday(birthday1),"color":get_random_color()},"birthday2":{"value":get_birthday(birthday2),"color":get_random_color()},"words":{"value":get_words(),"color":get_random_color()},"highest": {"value":highest,"color":get_random_color()},"lowest":{"value":lowest, "color":get_random_color()},"city": {"value":city,"color":get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
