# configure a xmlrpclib server object for BSCW
# R. Ruland
#---------------------------------------------------------------------------
# All code contained herein is covered by the Copyright as distributed
# in the BSCW_COPYRIGHT file in the main directory of the distribution
# of the BSCW server.
#---------------------------------------------------------------------------

def XMLRPC_Server(uri, user_passwd=None, encoding=None, 
                    verbose=0, allow_none=0, use_datetime=0): 
    import urllib, xmlrpclib, ssl
    if user_passwd: 
        uri_type = urllib.splittype(uri)[0] 
        if uri_type == "https": 
            BaseTransport = xmlrpclib.SafeTransport
        else: 
            BaseTransport = xmlrpclib.Transport 
        class AuthorizedTransport(BaseTransport): 
            def __init__(self, use_datetime=0, user_passwd=''): 
                import base64, string 
                BaseTransport.__init__(self, use_datetime=use_datetime, context=ssl._create_unverified_context()) 
                self.auth = string.strip(base64.encodestring(user_passwd)) 
            def send_host(self, connection, host): 
                BaseTransport.send_host(self, connection, host) 
                if self.auth: 
                    connection.putheader('Authorization', 
                        'Basic %s'%self.auth) 
        ServerTransport = AuthorizedTransport(use_datetime, user_passwd) 
    else: 
        ServerTransport = None 
    return xmlrpclib.Server(uri, ServerTransport, 
        encoding=encoding, verbose=verbose, allow_none=allow_none) 
        
