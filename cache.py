import hashlib

class SimpleCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def hash_input(self, task, code, target_lang=None):
        full = f"{task}|{target_lang}|{code}"
        return hashlib.md5(full.encode()).hexdigest()
      
