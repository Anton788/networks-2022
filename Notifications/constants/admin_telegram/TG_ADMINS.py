ID_ILIN = 408434193

USERNAME_ILIN = "ilin_an"
USERNAME_UNDEFINED = "<undefined>"

ADMIN_TG_IDS = [ID_ILIN]


class PersonInfo:
    def __init__(self, tg_username):
        self.TG_USERNAME = tg_username


class ADMIN_INFO:
    UNDEFINED = PersonInfo(USERNAME_UNDEFINED)
    ILIN = PersonInfo(USERNAME_ILIN)
