def ONLY_GROUP(func):
    def wrapper(*args, **kwargs):
        # logika ONLY_GROUP di sini
        return func(*args, **kwargs)
    return wrapper

def ONLY_ADMIN(func):
    def wrapper(*args, **kwargs):
        # logika ONLY_ADMIN di sini
        return func(*args, **kwargs)
    return wrapper
