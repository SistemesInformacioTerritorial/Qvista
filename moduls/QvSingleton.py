class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

# Decorador
class singleton:
    def __init__(self, cls):
        self._cls = cls

    def __call__(self, *args, **kwargs):
        if hasattr(self, '_instance'):
            return self._instance
        else:
            self._instance = self._cls(*args, **kwargs)
            return self._instance

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)
