import socket
import sqlite3

from flask import Flask, render_template, g
from werkzeug.utils import redirect

from pang_web import svcs
from pang_web.pang_web_opts import parse_pang_web_ini_options, parse_pang_web_cli_options, print_options

app = Flask(__name__)
g_opts = {"server_port": 80, "debug": False, "db_location": "../pang_db/pang.db"}


# DATABASE = "pang.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(g_opts['db_location'])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return redirect("/leaderboard")


@app.route('/leaderboard')
def route_leaderboard():
    result = svcs.get_top_ten()
    print(f"DEBUG Retrieved {len(result)} record(s)")
    return render_template("leaderboard.html", result=result)


if __name__ == "__main__":
    parse_pang_web_ini_options(g_opts)
    parse_pang_web_cli_options(g_opts)
    print_options(g_opts)

    DATABASE = g_opts['db_location']
    svcs.create_tables()

    binding_address = "0.0.0.0"
    app.run(host=binding_address, port=g_opts["server_port"], debug=True)
