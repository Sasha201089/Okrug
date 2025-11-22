import json

def write_in_base(key, vallue):
    with open("EventDataBase/EventBase.json", "r", encoding="utf8") as file:
        data = json.load(file)
        data[key] = vallue
        with open("EventDataBase/EventBase.json", "w", encoding="utf8") as new_file:
            json.dump(data, new_file)
            return True

def get_from_base(key):
    with open("EventDataBase/EventBase.json", "r", encoding="utf8") as file:
        data = json.load(file)
        return data[key]

def get_events_from_base():
    with open("EventDataBase/EventBase.json", "r", encoding="utf8") as file:
        result = []
        data = json.load(file)
        for k in data:
            result.append(k)
        return result

def get_all_events():
    with open("EventDataBase/EventBase.json", "r", encoding="utf8") as file:
        data = json.load(file)
        return data



