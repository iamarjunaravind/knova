class NoIndexRobotsMiddleware:
    """
    Prevents Google, Bing, and all web search engines / crawlers from indexing,
    archiving, or showing this website in search results.
    The website remains completely accessible to anyone visiting via direct link.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Robots-Tag'] = 'noindex, nofollow, noarchive, nosnippet, noimageindex'
        return response
