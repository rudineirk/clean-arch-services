from ujson import loads

REMOTE_ADDR_HEADERS = [
    'Forwarded',
    'X-Forwarded-For',
    'X-Real-IP',
]


class Request:
    def __init__(
            self,
            path,
            method,
            body,
            headers,
            query,
            remote_addr=None,
    ):
        self.path = path
        self.method = method
        self.body = body
        self.headers = headers
        self.query = query
        self.content_type = headers.get('Content-Type', 'text/plain')
        self.authorization = headers.get('Authorization', '')

        self.host = headers.get('Host', '')
        port = self.host.split(':')
        self.port = int(port[1]) if len(port) >= 2 else 80
        self.remote_addr = remote_addr if remote_addr else ''
        for header in REMOTE_ADDR_HEADERS:
            self.remote_addr = self.headers.get(header, self.remote_addr)

        self._json = None

    @property
    def json(self):
        if self._json is None:
            self._json = loads(self.body)
        return self._json
