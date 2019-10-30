from datetime import timedelta, datetime
from settings import automatic_ban_minutes
standart_delta = timedelta(minutes=automatic_ban_minutes)


class Banned():
    def __init__(self, ip):
        self.ip = ip
        self.banned_for = datetime.now() + standart_delta


class User():
    def __init__(self, ip):
        self.ip = ip
        self.messages = []
        self.passwod_attemps = 0

    def message(self, mess):
        self.messages.append(mess)
        if len(self.messages) > 15:
            del self.messages[0]
        return self.messages.count(mess)


class Antispam():
    def __init__(self):
        self.banned = []

    def ban(self, ip):
        self.banned.append(Banned(ip))

    def is_banned(self, ip):
        if not self.banned:
            return False
        self.update_list()
        for user in self.banned:
            if user.ip == ip:
                return True
        return False

    def update_list(self):
        new_banned = []
        for user in self.banned:
            if datetime.now() < user.banned_for:
                new_banned.append(user)
        self.banned = new_banned
