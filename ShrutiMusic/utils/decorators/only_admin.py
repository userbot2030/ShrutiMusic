def ONLY_ADMIN(func):
    def wrapper(*args, **kwargs):
        # logika ONLY_ADMIN
        return func(*args, **kwargs)
    return wrapper
