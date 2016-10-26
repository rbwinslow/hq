import os
import re
from inspect import isclass, isfunction
from pkgutil import walk_packages

from hq.verbosity import verbose_print
from hq.hquery.evaluation_error import HqueryEvaluationError


class FunctionSupport:
    all_functions = None


    def call_function(self, name, *args):
        self._load_all_functions()

        py_name = name.replace('-', '_')

        try:
            fn = self.all_functions[py_name]
        except KeyError:
            raise HqueryEvaluationError('Unknown function name "{0}"'.format(name))

        try:
            return fn(*args)
        except TypeError as err:
            if re.search(r'\d+ (?:.+ )?argument', err.args[0]):
                raise HqueryEvaluationError(err.args[0])
            else:
                raise


    def _load_all_functions(self):
        if self.all_functions is None:
            self.all_functions = dict()
            my_package = '{0}/__init__.py'.format(os.path.dirname(__file__))
            verbose_print('FunctionSupport loading all function modules near {0}.'.format(my_package),
                          indent_after=True)
            for importer, modname, ispkg in walk_packages(my_package):
                if not ispkg and modname.startswith('hq.hquery.functions.'):
                    verbose_print('Found candidate module {0} -- loading.'.format(modname))
                    module = importer.find_module(modname).load_module(modname)
                    if hasattr(module, 'exports'):
                        exports = {name.rstrip('_'): getattr(module, name) for name in getattr(module, 'exports')}
                        verbose_print('Module {0} exports are: {1}'.format(modname, exports.keys()))
                        if any(not (isclass(obj) or isfunction(obj)) for obj in exports.values()):
                            raise RuntimeError('Non-class/function export(s) loaded from module {0}'.format(modname))
                        self.all_functions.update(exports)
                    else:
                        verbose_print('Module {0} defined no exports.'.format(modname))
            verbose_print('Finished loading function modules.', outdent_before=True)
