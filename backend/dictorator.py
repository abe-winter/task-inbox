import inspect, dataclasses, contextlib, functools, logging, argparse
from typing import Callable, Dict

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Injector:
    "manages injection of a special arg"
    # todo: support async eventually maybe
    name: str
    type_: type
    manager: Callable[[], contextlib.AbstractContextManager]

    def decorate(self, fn):
        "return decorated copy of fn which will inject self.name"
        # todo: figure out how to remove self.name from the wrapped function
        @functools.wraps(fn)
        def outer(*args, **kwargs):
            with self.manager() as val:
                return fn(*args, **{self.name: val, **kwargs})
        return outer

class Dictorator(dict):
    "dictionary that registers functions with decorator"
    def __init__(self, *args, injectors: 'Sequence[Injector]' = (), **kwargs):
        self.injectors = injectors
        super(*args, **kwargs)

    def __call__(self, f):
        "decorator"
        self[f.__name__] = f
        return f

    def register_subparsers(self, subparsers: 'argparse._SubParsersAction', injectors: 'Sequence[Injector]' = ()):
        """
        Call this to set up argparse.
        todo: doc how annotations, injectors, and default affect this.
        """
        # todo: allow certain special params to trigger an 'injection decorator' i.e. for sqlalchemy engine
        injectors_: Dict[str, Injector] = {(inject.name, inject.type_): inject for inject in injectors}
        for name, fn in self.items():
            p = subparsers.add_parser(name, help=fn.__doc__)
            spec = inspect.getfullargspec(fn)
            defaults = dict(zip(spec.args[-len(spec.defaults):], spec.defaults)) if spec.defaults else {}
            cli_args = []
            for argname in spec.args:
                annot = spec.annotations.get(argname)
                if (inject := injectors_.get((argname, annot))):
                    self[name] = fn = inject.decorate(fn)
                    logger.debug('decorated %s for arg %s %s', fn, argname, annot)
                    continue # i.e. don't put in cli_args
                if annot is bool:
                    assert defaults.get(argname) is False # bools must be flags
                    p.add_argument('--' + argname, action='store_true')
                else:
                    prefix = '--' if argname in defaults else ''
                    p.add_argument(prefix + argname, type=annot or str, default=defaults.get(argname))
                cli_args.append(argname)
            # note: if injector removed injected args from the wrapper fn, wouldn't need to track these
            fn.__cli_args__ = cli_args

    def mkargs(self) -> argparse.ArgumentParser:
        "return an arg parser with our known functions + their args"
        p = argparse.ArgumentParser()
        self.register_subparsers(
            p.add_subparsers(dest='command', required=True),
            self.injectors,
        )
        return p

    def main(self):
        "entrypoint with argparse for our known functions"
        args = self.mkargs().parse_args()
        # todo: add --log as var
        # todo: have I just replicated click? why did I not like click? bad async support?
        logging.basicConfig(level=logging.INFO)
        fn = self[args.command]
        fnargs = {
            name: getattr(args, name)
            for name in fn.__cli_args__
        }
        return fn(**fnargs)
