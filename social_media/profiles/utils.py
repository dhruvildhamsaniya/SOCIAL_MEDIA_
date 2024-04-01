import uuid

def get_random_str():
    str1 = str(uuid.uuid4())[:8].replace('-', '').lower()
    return str1