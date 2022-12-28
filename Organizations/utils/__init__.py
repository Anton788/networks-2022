import random
import string


def get_random_code(amount=10):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits  # '0123456789'
    rand_string = ''.join(random.choice(letters) for _ in range(amount))
    return f'{rand_string}'
