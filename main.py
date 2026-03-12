from app import PyFramework
from middleware import Middleware

app = PyFramework()


@app.router("/home/{name}")
def home(request, response, name):
    response.text = f"Hello {name}"


@app.router("/books/")
class Books:

    def get(self, request, response):
        response.text = "Getting boooks\n"

    def post(self, request, response):
        response.text = "Created a book\n   "

class LoggingMiddleware(Middleware):

    def process_request(self, request):
        print("hi")

    def process_response(self, request, response):
        print("Bye")
    
app.add_middleware(LoggingMiddleware)