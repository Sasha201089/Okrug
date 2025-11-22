import requests
from gigachat import GigaChat
import json
import DataBase.Manager as db
import EventDataBase.Manager as event

def ai_response(prompt):
    auth_code = "MDE5YTY4ZDAtOTdlYS03M2JhLTg4MWYtZDc2ZjU4NmIzOWM1OjJkYzdlNjhiLTcwODUtNDU1My05YmI5LTlkYzIyZjEzNGQ2YQ=="
    with GigaChat(credentials=auth_code, verify_ssl_certs=False) as giga:
        response = giga.chat(prompt)
        return response.choices[0].message.content

def ai_search(user_id):
    auth_code = "MDE5YTY4ZDAtOTdlYS03M2JhLTg4MWYtZDc2ZjU4NmIzOWM1OjJkYzdlNjhiLTcwODUtNDU1My05YmI5LTlkYzIyZjEzNGQ2YQ=="
    with GigaChat(credentials=auth_code, verify_ssl_certs=False) as giga:
        user_data = db.get_from_base(str(user_id))
        base = event.get_all_events()
        if "filters" in user_data:
            filt = user_data["filters"]
        else:
            return []
        response = giga.chat('''Тебе даны фильтры, по которым пользователь ищет мероприятие: '''+str(filt)+'''
        Также тебе дана база мероприятий:'''+str(base)+''' Выведи просто через запятую названия мероприятий, которые по твоему мнению
        подходят пользователю. Выведи только список, без лишних слов и форматирования! Выводи в формате: Название1, Название2 и т. д.
        Если ничего не найдено, то выведи пустую строку''')
        result = response.choices[0].message.content.split(", ")
        return result
#print(ai_search(6785595088))