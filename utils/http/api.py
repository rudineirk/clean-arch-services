class Api:
    def __init__(self, url):
        self.url = url
        self.methods = {}

    def get(self, func):
        self._save_method('GET', func)
        return func

    def post(self, func):
        self._save_method('POST', func)
        return func

    def put(self, func):
        self._save_method('PUT', func)
        return func

    def delete(self, func):
        self._save_method('DELETE', func)
        return func

    def head(self, func):
        self._save_method('HEAD', func)
        return func

    def options(self, func):
        self._save_method('OPTIONS', func)
        return func

    def _save_method(self, method: str, func):
        self.methods[method] = func.__name__

    def get_methods(self, obj):
        methods = {}
        for method, func_name in self.methods.items():
            func = getattr(obj, func_name)
            methods[method] = func

        return methods
