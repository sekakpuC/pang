from sqlite3 import Connection


def dbapi_get_top10(conn: Connection):
    sql = f"""
    select username, score
    from score
    order by score desc
    limit 10
    """
    cursor = conn.execute(sql)
    return cursor.fetchall()


def dbapi_add_score(conn: Connection, username: str, score: int):
    sql = f"""
    insert into score(username, score)
    values('{username}', {score})
    """
    cursor = conn.execute(sql)
    return cursor.rowcount
