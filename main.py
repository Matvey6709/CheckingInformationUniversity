import asyncio
import logging
import re
import sys
import time
from threading import Thread
from time import sleep
import os
import requests
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from bs4 import BeautifulSoup
from aiogram.types import Message
import json
from aiogram import Bot, Dispatcher, html
from Direction import Direction
from User import User
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
dp = Dispatcher()
MainTime = 0
directions = []


def getFullInfoDirections():
    direction = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        url_json = 'https://urfu.ru/api/ratings/info/89/1235/'
        response_json = requests.get(url_json)

        f = json.loads(response_json.text)
        print(f['url'], f['updatedAt'])

        url_table = f'https://urfu.ru/{f["url"]}'
        response_table = requests.get(url_table, timeout=15, headers=headers)
        response_table.encoding = 'utf-8'
        soup = BeautifulSoup(response_table.text, 'html5lib')

        firstParametr = soup.find_all('table', class_="supp")

        for i in firstParametr:
            if i.get('id') is not None:
                direction_row = i.find_all('tr')
                v1 = i.get('id')
                v2 = '-'
                v3 = '-'
                for row in direction_row:
                    cells = row.find('th').text
                    cells2 = row.find('td').text
                    if cells == 'Вид конкурса': v2 = cells2
                    if cells == 'Направление (образовательная программа)': v1 = cells2
                    if cells == 'План приема': v3 = cells2
                direction.append(Direction(v1, v2, v3, []))
            else:
                secondParametr = i.find_all('tr', class_=['tr-odd', 'tr-even'])
                # print(direction[-1].getInfo())
                for headline in secondParametr:
                    id = headline.find_all('td', class_='td-center')[1].text
                    number = headline.find_all('td', class_='td-center')[0].text
                    is_document = len(headline.find_all('td', class_='td-center')[2].text) > 1
                    priority = headline.find_all('td', class_='td-center')[3].text
                    direction[-1].Users.append(User(id, number, is_document, priority))
                    # print(direction[-1].Users[-1].getInfo())
                    # input()
    except Exception:
        print('Erores', Exception)
    global directions
    directions = direction


def getFunction(id, dirs):
    st = '1)Название\n2)Какое у тебя место в списке и твой приоритет\n3)Сколько человек, с первым приоритетом и с согласием, выше тебя\n4)Количество людей всего\n\n'
    for direct in dirs:
        tr = direct.getNmberInThelist(id)
        nn = direct.getUser(id)
        if tr != -1 and nn != -1:
            st += f'1){html.bold(direct.name)}\n2){direct.getUser(id).number_list} {direct.getUser(id).priority}\n3){str(tr)}\n4){str(len(direct.Users))}\n\n'
    return st

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\nНапиши мне свой id с сайта, чтобы узнать подробную информацию")


@dp.message()
async def edit_POST_TEXT(message: Message) -> None:
    if not message.text.isdigit():
        await message.answer(f'Ошибка 1')
    else:
        msg_time = await message.answer(f'Загрузка')
        global MainTime
        global directions
        if time.time() - MainTime > 1800:
            MainTime = time.time()
            thread = Thread(target=getFullInfoDirections)
            thread.start()

        if len(directions) > 0:
            await msg_time.delete()
            await message.answer(getFunction(int(message.text), directions))
        else:
            await msg_time.delete()
            await message.answer(f'Повторите попытку через 3 минуты')


async def main() -> None:
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
