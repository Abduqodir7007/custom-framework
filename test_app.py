import pytest
from middleware import Middleware
from conftest import app, test_client
from app import PyFramework


class TestApp:
    def test_route_registration(self, app: PyFramework):

        @app.router("/home/")
        def home(request, response):
            response.text = "Hello from home"

    def test_duplicate_route_registration(self, app: PyFramework):

        @app.router("/home/")
        def home(request, response):
            response.text = "Hello from home"

        with pytest.raises(Exception):

            @app.router("/home/")
            def home2(request, response):
                response.text = "Hello from home"

    def test_client(self, app: PyFramework, test_client):

        @app.router("/home/")
        def home(request, response):
            response.text = "Hello from home"

        res = test_client.get("http://testserver/home/")

        assert res.text == "Hello from home"

    def test_parametized_routing(self, app: PyFramework, test_client):

        @app.router("/home/{name}/")
        def home(request, response, name):
            response.text = f"Hello {name}"

        res = test_client.get("http://testserver/home/john/")

        assert res.text == "Hello john"

    def test_wrong_routes(self, test_client):

        res = test_client.get("http://testserver/home/")

        assert res.text == "Not found"
        assert res.status_code == 404

    def test_class_based_get_routing(self, app, test_client):

        @app.router("/book/")
        class Book:

            def get(self, request, response):
                response.text = "Getting books"

        res1 = test_client.get("http://testserver/book/")
        res2 = test_client.post("http://testserver/book/")

        assert res1.text == "Getting books"
        assert res2.text == "METHOD NOT ALLOWED"
        assert res2.status_code == 405

    def test_django_like_routing(self, app, test_client):

        def book(request, response):
            response.text = "Hello from book"

        app.add_router("/book/", book)
        res = test_client.get("http://testserver/book/")

        assert res.text == "Hello from book"

    def test_custom_exception_handler(self, app: PyFramework, test_client):

        def on_exception(request, response, exp_class):
            response.text = "Something went wrong"

        app.add_exception_handler(on_exception)

        @app.router("/exception/")
        def exception(request, response):
            raise AttributeError("some exception")

        res = test_client.get("http://testserver/exception/")

        assert res.text == "Something went wrong"

    def test_custom_exception_handler_witj_class_based_router(
        self, app: PyFramework, test_client
    ):

        def on_exception(request, response, exception):
            response.text = "Exception from class"

        app.add_exception_handler(on_exception)

        @app.router("/book/")
        class Book:

            def get(self, request, response):
                raise AttributeError("Error")

        res = test_client.get("http://testserver/book/")

        assert res.text == "Exception from class"

    def test_middleware_methods_are_called(self, app: PyFramework, test_client):
        is_process_request_called = False
        is_process_response_called = False

        class SimpleMiddleware(Middleware):
            def __init__(self, app):
                super().__init__(app)

            def process_request(self, request):

                nonlocal is_process_request_called
                is_process_request_called = True

            def process_response(self, request, response):
                nonlocal is_process_response_called
                is_process_response_called = True

        app.add_middleware(SimpleMiddleware)
        @app.router("/home/")
        def home(request, response):
            response.text = "Hello from middleware"

        res = test_client.get("http://testserver/home/")

        assert is_process_response_called is True
        assert is_process_request_called is True
