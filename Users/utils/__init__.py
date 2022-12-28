import random
import string


def get_random_password(amount=12):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits  # '0123456789'
    rand_string = ''.join(random.choice(letters) for _ in range(amount))
    part_size = amount // 4
    return '-'.join([rand_string[i:i + part_size] for i in range(0, amount, part_size)])


def get_full_name(user):
    return " ".join([user.last_name, user.first_name, user.middle_name])[1:]
