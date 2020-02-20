import sys

if sys.version_info.major == 2:
    # Python2
    from httplib import HTTPConnection
    from xmlrpclib import SafeTransport, Transport, ProtocolError
else:
    # Python3
    from http.client import HTTPConnection
    from xmlrpc.client import SafeTransport, Transport, ProtocolError


class CookieTransport(SafeTransport):
    """
    Overides request add cookies from previous request.
    """

    def __init__(self):
        Transport.__init__(self)
        self.cookie = None

    def make_connection(self, host):
        h = HTTPConnection(host)
        return h

    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request
        h = self.make_connection(host)

        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)

        if self.cookie is not None:
            h.putheader("Cookie", self.cookie)

        self.send_content(h, request_body)
        errcode, errmsg, headers = h.getreply()

        self.cookie = headers.getheader('set-cookie') or self.cookie

        if errcode != 200:
            raise ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
            )

        # do not print the response body
        self.verbose = False

        return self.parse_response(h.getfile())
