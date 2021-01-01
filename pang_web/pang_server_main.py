import json
import socket
import threading
from _thread import *

from pang_web import svcs
from pang_web.pang_server_opts import parse_pang_server_ini_options, parse_pang_server_cli_options, print_options

my_lock = threading.Lock()


def thread_callback(client_sock: socket, opts: dict):
    while True:
        data_len_byte = client_sock.recv(10)
        if len(data_len_byte) != 10:
            break
        data_len_str = data_len_byte.decode()
        data_len_int = int(data_len_str)
        data_byte = client_sock.recv(data_len_int)
        if opts["debug"]:
            print(data_len_int, data_byte)
        data_dict = json.loads(data_byte)
        if "type" in data_dict:
            data_type = data_dict["type"]
            if data_type == "snapshot":
                pass
            elif data_type == "score":
                print(f"DEBUG received score message: len {data_len_int}, data_dict {data_dict}")
                # Use lock for sqlite3
                my_lock.acquire()
                row_count = svcs.add_score_to_db(data_dict['username'], data_dict["score"])
                my_lock.release()
                if row_count == 1:
                    print(f"DEBUG svcs.add_score_to_db({data_dict}) = 1 (success)")
        else:
            print(f"ERROR No 'type' attribute in the message: {data_byte}")
    print(f"DEBUG closed client socket.")
    client_sock.close()


def server_main(opts: dict):
    binding_address = "0.0.0.0"
    server_port = opts["server_port"]
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if opts["debug"]:
        print(f"DEBUG s = socket(AF_INET, SOCK_STREAM) succeeded")
    server_sock.bind((binding_address, server_port))
    if opts["debug"]:
        print(f"DEBUG s.bind('{binding_address}', {server_port}) succeeded")
    server_sock.listen(1000)
    print(f"DEBUG pang_server is running on port {server_port}")

    while True:
        # print(f"DEBUG Waiting...")
        client_sock, addr = server_sock.accept()
        client_ip = addr[0]
        client_port = addr[1]
        print(f'DEBUG New connection from {client_ip}:{client_port}')
        start_new_thread(thread_callback, (client_sock, opts))
    # I know this is unreachable.
    print(f"ERROR This code should not be hit.")
    server_sock.close()
    print("closed server socket. No more accept.")


if __name__ == '__main__':
    g_opts = {"server_port": 2345, "debug": True}
    parse_pang_server_ini_options(g_opts)
    parse_pang_server_cli_options(g_opts)
    print_options(g_opts)

    DATABASE = g_opts['db_location']
    svcs.create_tables()

    server_main(g_opts)
