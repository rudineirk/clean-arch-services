from functools import wraps
from wsgiref.simple_server import make_server

from falcon import API as FalconApi
from falcon import Request as FalconRequest
from falcon import Response as FalconResponse
from falcon import status_codes

from utils.http import Request, Response

STATUS_MAPPING = {}
for attr in dir(status_codes):
    if not attr.startswith('HTTP_'):
        continue

    try:
        http_status = attr.split('_')[1]
        http_status = int(http_status)
    except ValueError:
        continue

    STATUS_MAPPING[http_status] = getattr(status_codes, attr)


class FalconApp:
    def __init__(self, *args, **kwargs):
        self.falcon = FalconApi(*args, **kwargs)
        self.urls = {}

    def add_api(self, api_obj):
        self.urls[api_obj.api.url] = api_obj.api.get_methods(api_obj)
        return self

    def configure(self):
        for url, methods in self.urls.items():
            api = ApiMethods(methods)
            self.falcon.add_route(url, api)

    def __call__(self, *args, **kwargs):
        '''WSGI interface'''
        return self.falcon(*args, **kwargs)

    def run(self, host='', port=3000):
        with make_server(host, port, self.falcon) as httpd:
            httpd.serve_forever()

    def http_options(self, url: str, method):
        return self._create_method(url, 'OPTIONS', method)

    def _create_method(self, url: str, http_method: str, method):
        self._create_url(url)
        self.urls_map[url][http_method] = method

    def _create_url(self, url: str):
        if url not in self.urls_map:
            self.urls_map[url] = {}


class ApiMethods:
    def __init__(self, methods: dict):
        for method, func in methods.items():
            self.set_method(method, func)

    def set_method(self, method, func):
        @wraps(func)
        def wrapper(req: FalconRequest, resp: FalconResponse, *args):
            wrapper_req = Request(
                path=req.path,
                method=req.method,
                body=req.bounded_stream.read(),
                headers=req.headers,
                query=req.params,
                remote_addr=req.remote_addr,
            )
            wrapper_resp: Response = func(wrapper_req, *args)
            resp.data = wrapper_resp.body
            resp.status = STATUS_MAPPING[wrapper_resp.status]
            for header, value in wrapper_resp.headers.items():
                resp.set_header(header, value)

        setattr(
            self,
            'on_' + method.lower(),
            wrapper,
        )
