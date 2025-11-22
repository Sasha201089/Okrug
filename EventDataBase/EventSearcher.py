from openai import OpenAI
import json
import Manager

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5-nano",
  input='''Проанализируй эту веб страницу: https://it-event-hub.ru/ и напиши информацию только о мероприятиях, проходящих
        в Санкт-Петербурге. Ответ выведи в таком формате словаря без стороннего форматирования: {"{название мероприятия}" : {"место проведения" : "{место проведения}",
        "дата проведения" : "{дата проведения}", "тип" : "{тип мероприятия}", "стоимость" : "{стоимость, если есть}",
        "описание" : "{описание мероприятия}", "ссылка" : "{ссылка на мероприятие}"}, и т. д.}
        ''',
  tools=[{"type": "web_search_preview"}],
  store=True,
)
text = response.output_text
print(text)
text1 = json.load(text)
for t in text1:
  Manager.write_in_base(t, text1[t])
