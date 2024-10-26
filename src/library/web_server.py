import asyncio
import gc
import re

HTTP_CODES = {
    200: 'Ok',
    400: 'Bad request',
    403: 'Forbidden',
    404: 'Not found',
    405: 'Method not allowed',
    500: 'Internal server error',

}


class MicroPyServer(object):

    def __init__(self, host='0.0.0.0', port=80):
        """ Constructor """
        self._host = host
        self._port = port
        self._routes = []
        self._connect = None
        self._on_request_handler = None
        self._on_not_found_handler = None
        self._on_error_handler = None
        self._sock = None
        self._loop = asyncio.get_event_loop()

    def make_http_response(self, response: str, http_code=200, content_type='text/html', extend_headers=None):
        """ send response """
        result = str('HTTP/1.1 ' + str(http_code) + ' ' +
                     HTTP_CODES.get(http_code) + '\r\n')
        result += 'Content type:' + content_type + '\r\n'
        if extend_headers is not None:
            for header in extend_headers:
                result += header + '\r\n'
        result += '\r\n'
        result += response

        return result

    def write_http_response(
            self,
            stream: asyncio.StreamWriter,
            response_generator,  # Iterable[str]
            http_code=200,
            content_type='text/html',
    ):
        stream.write(str('HTTP/1.1 ' + str(http_code) + ' ' +
                     HTTP_CODES.get(http_code) + '\r\n').encode('utf8'))

        headers = {
            'Content type': content_type,
            'Connection': 'close'
        }
        for (key, value) in headers.items():
            header_line = f'{key}: {value}\r\n'
            stream.write(header_line.encode('utf8'))

        stream.write('\r\n'.encode('utf8'))

        for data in response_generator():
            stream.write(data.encode('utf8'))

    async def handler(self, reader: asyncio.stream.StreamReader, writer: asyncio.StreamWriter):
        """
        Async handler function to handle new connections.

        https://docs.micropython.org/en/latest/library/asyncio.html#asyncio.Stream
        """

        ip, port = reader.get_extra_info('peername')
        print(f'Got a new connection from {ip}')

        gc.collect()

        request = (await reader.read(255)).decode('utf8')

        # print(f"{request=}")
        status = 200
        try:
            route = self.find_route(request)
            if route:
                handler = route['handler']

                response = await handler(request=request, server=self, stream=writer)
            else:
                response = '404 not found'
        except Exception as exc:  # noqa
            response = str(exc)
            status = 500

        if response:
            http_response = self.make_http_response(
                response=response, http_code=status)
            print(f'{http_response=}')

            writer.write(http_response.encode('utf8'))

        await writer.drain()

        await writer.wait_closed()
        await reader.wait_closed()

        gc.collect()

        print(f'Connection to client {ip} were closed.')

    async def start_server(self):
        print(f'start server {self._host}:{self._port}')

        await asyncio.start_server(self.handler, self._host, self._port)

        print('server started')

    def add_route(self, path, handler, method='GET'):
        """ Add new route  """
        self._routes.append(
            {'path': path, 'handler': handler, 'method': method}
        )

    def find_route(self, request):
        """ Find route """
        lines = request.split('\r\n')
        method = re.search('^([A-Z]+)', lines[0]).group(1)
        path = re.search('^[A-Z]+\\s+(/[-a-zA-Z0-9_.]*)', lines[0]).group(1)
        for route in self._routes:
            if method != route['method']:
                continue
            if path == route['path']:
                return route
            else:
                match = re.search('^' + route['path'] + '$', path)
                if match:
                    print(method, path, route['path'])
                    return route
