from pang_web import pang_web_main, db_api


def add_score_to_db(username: str, score: str):
    with pang_web_main.app.app_context():
        conn = pang_web_main.get_db()
        row_count = db_api.dbapi_add_score(conn, username, score)
        if row_count == 1:
            print(f"DEBUG Added score ({username}, {score}) to DB")
            conn.commit()
        else:
            print(f"DEBUG Failed to add score ({username}, {score}) to DB")
        return row_count
    return 0


def get_top_ten():
    result = []
    with pang_web_main.app.app_context():
        conn = pang_web_main.get_db()
        rows = db_api.dbapi_get_top10(conn)
        for row in rows:
            a = {"username": row["username"], "score": row["score"]}
            result.append(a)
    return result


def create_tables():
    with pang_web_main.app.app_context():
        conn = pang_web_main.get_db()
        sql = f"create table if not exists score (username text, score int)"
        conn.execute(sql)
        print("Created table 'score' successfully.")
