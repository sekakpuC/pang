def parse_pang_client_ini_options(opts: dict = None):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('pang_client.ini')

    if opts is None:
        opts = {}

    t = config.get('pang_server', 'server_host', fallback=None)
    if t is not None:
        opts['server_host'] = t

    t = config.getint('pang_server', 'server_port', fallback=None)
    if t is not None:
        opts['server_port'] = t

    t = config.get('pang_client', 'play_mode', fallback=None)
    if t is not None:
        opts['play_mode'] = t

    t = config.getboolean('pang_client', 'online', fallback=None)
    if t is not None:
        opts['online'] = t

    t = config.getboolean('pang_client', 'debug', fallback=None)
    if t is not None:
        opts['debug'] = t

    return opts


def parse_pang_client_cli_options(opts: dict = None):
    import argparse
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=29, width=100)
    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument('--server_host', action='store', default=None, help='server host')
    parser.add_argument('--server_port', action='store', default=None, type=int, help='server port')
    parser.add_argument('--play_mode', action='store', default=None, help="'new' or 'replay'")
    parser.add_argument('--online', action='store', default=None, help="'true' or 'false'")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-d', dest='debug', action='store_true', default=None, help="debug mode")
    args = parser.parse_args()
    if opts is None:
        opts = {}
    if args.server_host:
        opts['server_host'] = args.server_host
    if args.server_port:
        opts['server_port'] = args.server_port
    if args.play_mode:
        opts['play_mode'] = args.play_mode
    if args.online:
        opts['online'] = args.online.lower() in ['true', 'yes', 'on']
    if args.debug:
        opts['debug'] = args.debug
    return opts


def print_options(opts: dict):
    print(f"DEBUG --server_host = {opts['server_host']}")
    print(f"DEBUG --server_port = {opts['server_port']}")
    print(f"DEBUG --play_mode = {opts['play_mode']}")
    print(f"DEBUG --online = {opts['online']}")
    print(f"DEBUG -d = {opts['debug']}")


if __name__ == '__main__':
    opts = {
        "server_host": 'localhost',
        "server_port": 2345,
        "play_mode": 'new',
        "online": True,
        "debug": False
    }
    parse_pang_client_ini_options(opts)
    parse_pang_client_cli_options(opts)
    print_options(opts)
