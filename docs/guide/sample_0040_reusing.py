_host = 'localhost' # params prefixed by underscore are hidden
class http_connection:
    host = _host  # using the definition of _host above, instead of re-defining
    port = 80
class ftp_connetion:
    host = _host  # using the definition of _host above, instead of re-defining
    port = 21

class client:
    connection = http_connection  # config-containers (such as http_connection) can also be reused
