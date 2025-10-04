import importlib.util
import inspect
import sys
from pathlib import Path


class CodeLoader:
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.module = None
        self.module_name = None
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if self.file_path.suffix != '.py':
            raise ValueError(f"Not a Python file: {file_path}")
    
    def load(self):
        self.module_name = f"loaded_{self.file_path.stem}"
        spec = importlib.util.spec_from_file_location(self.module_name, self.file_path)
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load: {self.file_path}")
        
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[self.module_name] = self.module
        spec.loader.exec_module(self.module)
        
        return self.module
    
    def get_functions(self):
        if self.module is None:
            self.load()
        
        return {name: obj for name, obj in inspect.getmembers(self.module, inspect.isfunction)
                if obj.__module__ == self.module_name}
    
    def get_classes(self):
        if self.module is None:
            self.load()
        
        return {name: obj for name, obj in inspect.getmembers(self.module, inspect.isclass)
                if obj.__module__ == self.module_name}
    
    def get_variables(self):
        if self.module is None:
            self.load()
        
        variables = {}
        for name in dir(self.module):
            if not name.startswith('_'):
                obj = getattr(self.module, name)
                if not inspect.isfunction(obj) and not inspect.isclass(obj) and not inspect.ismodule(obj):
                    variables[name] = obj
        return variables
    
    def get(self, name):
        if self.module is None:
            self.load()
        return getattr(self.module, name, None)
    
    def call(self, name, *args, **kwargs):
        func = self.get(name)
        if func is None:
            raise AttributeError(f"'{name}' not found")
        if not callable(func):
            raise TypeError(f"'{name}' is not callable")
        return func(*args, **kwargs)
    
    def instantiate(self, name, *args, **kwargs):
        cls = self.get(name)
        if cls is None:
            raise AttributeError(f"'{name}' not found")
        if not inspect.isclass(cls):
            raise TypeError(f"'{name}' is not a class")
        return cls(*args, **kwargs)
