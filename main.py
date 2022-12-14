import telebot
import logging
import numpy as np
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

logger = telebot.logger
TOKEN = "5604821697:AAEh1e-iem_ZaxXgYqRKSBiKPKub_XqGwMo"
PALINDROME_LEN = 0
PALINDROME_CNT = 0
PALINDROME_CNT_ALL = 0
ADJ_CNT = 1
IS_ADJ = 0
SIRIUS_CNT = 0
SIRIUS_MSG = 0

bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=["start"])
def send_start(msg):
    bot.send_message(msg.chat.id,
                     '''Привет! Это бот, сделанный на паре Сириуса. Его функционал можно спросить по команде /help''')


@bot.message_handler(commands=["finish"])
def send_start(msg):
    global PALINDROME_CNT, PALINDROME_CNT_ALL, PALINDROME_LEN, ADJ_CNT, SIRIUS_CNT, SIRIUS_MSG, IS_ADJ
    bot.send_message(msg.chat.id,
                     f'{PALINDROME_LEN / max(1, PALINDROME_CNT)} {PALINDROME_CNT_ALL} {ADJ_CNT * IS_ADJ} {SIRIUS_CNT / max(1, SIRIUS_MSG)}')
    PALINDROME_CNT_ALL = 0
    ADJ_CNT = 1
    IS_ADJ = 0
    PALINDROME_CNT = 0
    PALINDROME_LEN = 0
    PALINDROME_CNT = 0
    SIRIUS_CNT = 0
    SIRIUS_MSG = 0



@bot.message_handler(commands=["help"])
def help(msg):
    bot.send_message(msg.chat.id, '''Для простого текста нужно посчитать суммарное количество слов-палиндромов в тексте, бот будет накапливать сумму по всем таким сообщениям (словом считается последовательность буквенных символов).

Для текстовых файлов нужно посчитать максимальную длину подстроки-палиндрома в тексте, бот будет подсчитывать среднюю длину по всем таким сообщениям.

Для картинок с подписью нужно посчитать количество прилагательных в тексте (на русском языке), бот будет подсчитать произведение по всем таким сообщениям.

Для аудио с подписью нужно посчитать число слов "сириус" в тексте, бот будет вывести среднее количество по всем таким сообщениям.

По команде /finish бот выведет в одном сообщении ответы для всех четырех задач через пробел: 1 2 3 4. После вывода все посчитанные статистики обнуляются.''')


def get_lens_palindrome(a):
    cnt = 0  # sum lens of palindromes
    for phrase in a:
        if phrase == phrase[::-1]:
            cnt += 1
    return cnt


def get_max_palindrome(s):
    t = ''
    for c in s:
        t += c
        t += '#'
    s = t[:-1]
    n = len(s)
    d = np.full(n, 0, dtype=int)
    l, r = 0, -1
    cnt = 0
    for i in range(n):
        k = 1 if i > r else min(d[l + r - i], r - i + 1)
        while i + k < n and i - k > 0 and s[i + k] == s[i - k]:
            k += 1
        d[i] = k
        if i % 2 == 0:
            cnt = max(cnt, (k - 1) // 2 * 2 + 1)
        else:
            cnt = max(cnt, k // 2 * 2)
        if i + k - 1 > r:
            r = i + k - 1
            l = i - k + 1
    return cnt


def spl(s: str):
    a = []
    cur = ''
    for i in s:
        if i.isalpha():
            cur += i
        else:
            if cur != '':
                a.append(cur)
            cur = ''
    if cur != '':
        a.append(cur)
    return a


def analyze_text(a):
    cnt = 0
    for word in a:
        ps = morph.parse(word)[0].tag.POS[:3]
        if ps == 'ADJ' or ps == 'PRT':
            cnt += 1
    return cnt


@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
def get_document(msg):
    file_info = bot.get_file(msg.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('sample.txt', 'wb') as new_file:
        new_file.write(downloaded_file)
    text = open('sample.txt', 'rb').read().decode('utf8')
    x = get_max_palindrome(text)
    global PALINDROME_CNT, PALINDROME_LEN
    PALINDROME_LEN += x
    PALINDROME_CNT += 1
    bot.send_message(msg.chat.id, 'Документ принят!')


@bot.message_handler(content_types=["text"])
def get_text(msg):
    s = msg.text
    global PALINDROME_CNT_ALL
    PALINDROME_CNT_ALL += get_lens_palindrome(spl(s))
    bot.send_message(msg.chat.id, 'Сообщение принято!')


@bot.message_handler(content_types=["photo"])
def get_photo(msg):
    s = msg.caption
    global ADJ_CNT, IS_ADJ
    ADJ_CNT *= analyze_text(spl(s))
    IS_ADJ = 1
    bot.send_message(msg.chat.id, 'Фото принято!')


@bot.message_handler(content_types=["audio"])
def get_audio(msg):
    s = msg.caption
    global SIRIUS_CNT, SIRIUS_MSG
    for phrase in spl(s):
        if phrase == "сириус":
            SIRIUS_CNT += 1
    SIRIUS_MSG += 1
    bot.send_message(msg.chat.id, "Аудио принято!")


if __name__ == "__main__":
    telebot.logger.setLevel(logging.DEBUG)
    logger.info('Bot started')
    bot.infinity_polling()
