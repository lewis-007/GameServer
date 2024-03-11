import io
import traceback
import weakref



class Functor():
    def __init__(self, obj, funcName, *args, **kwargs):
        self.obj = weakref.ref(obj)
        self.funcName = funcName
        self.args = args
        self.kwargs = kwargs

    def isCanCall(self):
        obj = self.obj()
        if obj is None:
            return False
        return True

    def __call__(self, *args, **kwargs):
        obj = self.obj()
        if obj is None:
            return
        try:
            return getattr(obj, self.funcName)(*self.args, *args, **self.kwargs, **kwargs)
        except:
            traceback.print_exc()


