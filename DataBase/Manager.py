import json

def write_in_base(key, vallue):
    with open("DataBase/base.json", "r") as file:
        data = json.load(file)
        data[key] = vallue
        with open("DataBase/base.json", "w") as new_file:
            json.dump(data, new_file)
            return True

def write_user_params_in_base(key, key2, vallue):
    with open("DataBase/base.json", "r") as file:
        data = json.load(file)
        data[key][key2] = vallue
        with open("DataBase/base.json", "w") as new_file:
            json.dump(data, new_file)
            return True

def get_from_base(key):
    with open("DataBase/base.json", "r") as file:
        data = json.load(file)
        return data[key]

def get_users_from_base():
    with open("DataBase/base.json", "r") as file:
        result = []
        data = json.load(file)
        for k in data:
            result.append(k)
        return result

def get_all_users():
    with open("DataBase/base.json", "r") as file:
        data = json.load(file)
        users = []
        for user_id, user_data in data.items():
            user_data['user_id'] = user_id
            users.append(user_data)
        return users



