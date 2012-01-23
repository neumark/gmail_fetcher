# from http://docs.python.org/library/traceback.html
import sys, traceback

def maybe_ex(fun, args = None):
    try:
        return ("ok", fun(args) if args is not None else fun())
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return ("exception", {
            'args': args,
            'type': exc_type.__name__,
            'value': str(exc_value),
            #'lines': traceback.format_exc().splitlines(),
            #'formatted': traceback.format_exception(exc_type, exc_value, exc_traceback),
            'traceback': traceback.extract_tb(exc_traceback)
        })


if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    def testfn():
        return tuple()[0]
    print pp.pformat(maybe_ex(testfn))
