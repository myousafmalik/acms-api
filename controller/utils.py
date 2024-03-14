import random
from cachetools import TTLCache


users_dict = TTLCache(maxsize=100, ttl=300)


def generate_random_number(size: int = 4):
    """
    Generate random number

    :param size: ``(int)``: The size of the random number.

    :return:  ``(int)``: The random number.
    """
    min_size = pow(10, size - 1)
    max_size = pow(10, size) - 1

    return random.randint(min_size, max_size)
