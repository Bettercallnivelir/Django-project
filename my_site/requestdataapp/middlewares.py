import datetime

from django.http import HttpRequest
from django.utils.timezone import now


def test_middleware(get_response):
    print('Initial', test_middleware.__name__)

    def middleware(request: HttpRequest):
        print('before')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('after')
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request):
        self.requests_count += 1
        print('requests count', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses count', self.responses_count)
        return response

    def process_exception(self, request, exception):
        self.exceptions_count += 1
        print('Total:', self.exceptions_count, 'exceptions')


class ThrottlingMiddleware:
    """
    ThrottlingMiddleware, ограничивает запросы пользователя, если их частота
    превышает TIME_LIMIT

    TIME_LIMIT (int): Временной лимит по запросам (в секундах)
    """
    __TIME_LIMIT = 3

    def __init__(self, get_response):
        self.get_response = get_response
        self.count_requests = 0
        self.request_data: dict = {}

    def __call__(self, request):
        if request.META['REMOTE_ADDR'] in self.request_data:
            last_request_time = self.request_data.get(request.META['REMOTE_ADDR'])
            diff = now() - last_request_time
            if diff.seconds < ThrottlingMiddleware.__TIME_LIMIT:
                raise Exception('Частота запросов превышена!')
        else:
            self.request_data[request.META['REMOTE_ADDR']] = now()

        response = self.get_response(request)
        self.request_data[request.META['REMOTE_ADDR']] = now()

        return response
