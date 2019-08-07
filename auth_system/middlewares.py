from auth_system.utils import str_to_dict

class CookieOAuthMiddleware:
    """
    Put the access token of Oauth into request header,
    in order that user having access token can be authenticated
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'Authorization' not in request.META \
                and request.META.get('HTTP_COOKIE'):
            cookies = str_to_dict(request.META['HTTP_COOKIE'])
            access_token = cookies.get('access_token', None)
            if access_token:
                request.META['Authorization'] = \
                    'Bearer %s' % access_token
        response = self.get_response(request)
        return response

