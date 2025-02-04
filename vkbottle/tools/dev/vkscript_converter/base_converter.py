import ast
from inspect import getsource
from typing import Callable, Dict, Type, Union


class ConverterError(Exception):
    pass


class Converter:
    """Translate Python into the VKScript with AST"""

    def __init__(self):
        self.definitions: Dict[ast.AST, Callable] = {}

    def __call__(self, for_definition: Union[Type[ast.AST], ast.AST]):
        def decorator(func):
            self.definitions[for_definition] = func
            return func

        return decorator

    def find_definition(self, d):
        if d.__class__ not in self.definitions:
            raise ConverterError(
                f"Definition for {d.__class__} is undefined. Maybe vkscript doesn't support it"
            )
        return self.definitions[d.__class__](d)

    def scriptify(self, func: Callable, **values) -> str:
        """Translate function to VKScript"""
        source = getsource(func)
        code: ast.FunctionDef = ast.parse(source).body[0]  # type: ignore
        args = [a.arg for a in code.args.args]
        args.pop(0)
        if any(v not in values for v in args):
            raise ConverterError(
                "All values should be passed to func. Predefined kwargs are not allowed"
            )
        values_assignments = [f"var {k}={v!r};" for k, v in values.items()]
        return "".join(values_assignments) + "".join(
            self.find_definition(line) for line in code.body
        )
