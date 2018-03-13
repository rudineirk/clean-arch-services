from ujson import dumps


class Response:
    def __init__(
            self,
            body=None,
            status=200,
            headers=None,
            content_type=None,
    ):
        content_type = content_type if content_type else 'text/plain'
        if isinstance(body, str):
            body = body.encode()

        self.body = body if body else b''
        self.status = status
        self.headers = headers if headers else {}
        self.headers['Content-Type'] = self.headers.get(
            'Content-Type',
            content_type,
        )


def json_response(body, *args, content_type='application/json',
                  **kwargs) -> Response:
    body = dumps(body)
    return Response(
        body,
        *args,
        content_type=content_type,
        **kwargs,
    )
