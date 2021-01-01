def parse_pang_server_ini_options(opts: dict = None):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('pang_server.ini')

    t = config.getint('pang_server', 'server_port', fallback=None)
    if t is not None:
        opts['server_port'] = t

    t = config.getboolean('pang_server', 'debug', fallback=None)
    if t is not None:
        opts['debug'] = t

    t = config.get('pang_db', 'location', fallback=None)
    if t is not None:
        opts['db_location'] = t

    return opts


def parse_pang_server_cli_options(opts: dict = None):
    import argparse
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=29, width=100)
    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument('--server_port', action='store', default=None, type=int, help='server port')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-d', dest='debug', action='store_true', default=False, help="debug mode")
    args = parser.parse_args()

    if opts is None:
        opts = {}

    if args.server_port:
        opts['server_port'] = args.server_port

    if args.debug:
        opts['debug'] = args.debug

    return opts


def print_options(opts: dict):
    print(f"DEBUG pang_server.ini [db] location = {opts['db_location']}")
    print(f"DEBUG --server_port = {opts['server_port']}")
    print(f"DEBUG -d = {opts['debug']}")


if __name__ == '__main__':
    opts = {
        "server_port": 2345,
        "debug": False,
        "db_location": "../pang_db/pang.db"
    }
    parse_pang_server_ini_options(opts)
    parse_pang_server_cli_options(opts)
    print_options(opts)
