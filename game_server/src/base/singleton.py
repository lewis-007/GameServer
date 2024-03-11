#coding=utf-8
class SingletonBase():
    _ins = None
    @classmethod
    def getObj(cls, *args: object, **kwargs: object):
        if cls._ins is None:
            cls._ins = cls(*args,**kwargs)
            return cls._ins
        return cls._ins
    @classmethod
    def haveObj(cls):
        if cls._ins is None:
            return True
        return False