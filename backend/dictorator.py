import inspect

class Dictorator(dict):
    "dictionary that registers functions with decorator"
    def __call__(self, f):
        "decorator"
        self[f.__name__] = f
        return f

    def register_subparsers(self, subparsers: 'argparse._SubParsersAction'):
        "call this to set up argparse"
        for name, fn in self.items():
            p = subparsers.add_parser(name, help=fn.__doc__)
            spec = inspect.getfullargspec(fn)
            for argname in spec.args:
                annot = spec.annotations.get(argname)
                defaults = dict(zip(spec.args[-len(spec.defaults):], spec.defaults)) if spec.defaults else {}
                if annot is bool:
                    assert defaults.get(argname) is False # bools must be flags
                    p.add_argument('--' + argname, action='store_true')
                else:
                    prefix = '--' if argname in defaults else ''
                    p.add_argument(prefix + argname, type=annot or str, default=defaults.get(argname))
