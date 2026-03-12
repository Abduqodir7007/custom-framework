import inspect
import requests
import wsgiadapter
from parse import parse
from webob import Request, Response
from middleware import Middleware


class PyFramework:
    def __init__(self) -> None:
        self.routes = dict()
        self.exception_handler = None
        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        # status = "200 CREATED"

        # response_header = [("Content-type", "text/plain")]
        # start_response(status, response_header)
        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def add_exception_handler(self, handler):
        self.exception_handler = handler

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request)

        if inspect.isclass(handler):

            handler_method = getattr(handler(), request.method.lower(), None)

            if handler_method is None:
                response.status_code = 405
                response.text = "METHOD NOT ALLOWED"
                return response

            try:
                handler_method(request, response, **kwargs)
            except Exception as e:
                if self.exception_handler is not None:
                    self.exception_handler(request, response, e)
                else:
                    raise e
        elif inspect.isfunction(handler):
            try:
                handler(request, response, **kwargs)
            except Exception as e:
                if self.exception_handler is not None:
                    self.exception_handler(request, response, e)
                else:
                    raise e

        else:
            self.default_response(response)

        return response

    def find_handler(self, request):
        for path, handler in self.routes.items():
            result = parse(path, request.path)
            if result is not None:
                return handler, result.named

        return None, None

    def add_middleware(self, middleware_class):
        self.middleware.add(middleware_class)

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found"

    def router(self, path):
        assert path not in self.routes, f"Path {path} already exists"

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def add_router(self, path, handler):
        assert path not in self.routes, f"Path {path} already exists"
        self.routes[path] = handler

    def test_session(self):
        session = requests.Session()
        session.mount("http://testserver", wsgiadapter.WSGIAdapter(self))
        return session
