"""Custom middleware for the project."""

import logging

logger = logging.getLogger('core')


class RequestLoggingMiddleware:
    """Log each incoming request method and path for observability."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)

        logger.info('REQUEST %s %s from %s', request.method, request.path, self._client_ip(request))
        response = self.get_response(request)
        logger.info('RESPONSE %s %s -> %s', request.method, request.path, response.status_code)
        return response

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
