import random
import time


def generateUniqueID():
    return (
        f"{int(time.time() * 1000)}x{random.randint(100000000000000, 999999999999999)}"
    )


def mask_phone(phone):
    if not phone:
        return None
    visible_digits = 2
    masked = '*' * (len(phone) - visible_digits) + phone[-visible_digits:]
    return '_'.join([masked[i:i+3] for i in range(0, len(masked), 3)])

def mask_email(email):
    if not email:
        return None
    username, domain = email.split('@')
    masked_username = username[0] + '*' * (len(username) - 4) + username[-3:]
    domain_parts = domain.split('.')
    masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 4) + domain_parts[0][-3:] + '.' + domain_parts[1]
    return f"{masked_username}@{masked_domain}"