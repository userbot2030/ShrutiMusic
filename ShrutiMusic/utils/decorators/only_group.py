def ONLY_GROUP(func):
    def wrapper(*args, **kwargs):
        # logika ONLY_GROUP
        return func(*args, **kwargs)
    return wrapper
