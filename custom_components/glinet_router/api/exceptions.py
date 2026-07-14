class APIClientError(Exception):
    pass


class NonZeroResponse(APIClientError):
    pass


class AuthenticationError(NonZeroResponse):
    pass


class TokenError(AuthenticationError):
    pass


class UnsuccessfulRequest(APIClientError):
    pass
