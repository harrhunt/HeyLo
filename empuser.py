from user import User
from empath import Empath
import json


class EmpUser(User):
    emp = Empath()

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        try:
            with open("data/original.json", "r") as file:
                topics = json.load(file)
            raw_data = self.emp.analyze(clean, categories=topics["topics"])

        # Otherwise, run empath without topics filter
        except IOError as err:
            print(err, "\r\nUsing all categories")
            raw_data = self.emp.analyze(clean)

        # Delete interests generated if they have a hit score of 0
        keys_to_delete = []
        for key in raw_data:
            if raw_data[key] <= 0:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del raw_data[key]

        return raw_data
