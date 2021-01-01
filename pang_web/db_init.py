import sqlite3

from pang_web.pang_web_opts import parse_pang_web_ini_options, parse_pang_web_cli_options


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def create_table(conn):
    sql = f"create table if not exists score (username text, score int)"
    conn.execute(sql)


if __name__ == '__main__':
    opts = {
        "server_port": 80,
        "debug": False,
        "db_location": "../pang_db/pang.db"
    }
    parse_pang_web_ini_options(opts)
    parse_pang_web_cli_options(opts)

    conn = create_connection(r"pang.db")
    create_table(conn)
    conn.close()
