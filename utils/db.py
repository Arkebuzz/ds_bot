import sqlite3

from config import PATH_DB as PATH


def create_db(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS games(
           name TEXT PRIMARY KEY, 
           user_id INTEGER,
           message_id TEXT,
           dir_name TEXT,
           version TEXT,
           genre TEXT,
           type TEXT,
           sys_requirements TEXT,
           description TEXT,
           num_downloads INTEGER,
           score REAL,
           user_voted TEXT);
           ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
           user_id INTEGER PRIMARY KEY,
           num_added INTEGER,
           num_downloads INTEGER,
           num_votes INTEGER);
           ''')
        conn.commit()


def check_game(name, d_name, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM games WHERE name = ?', (name,))
        name = cur.fetchall()
        cur.execute('SELECT * FROM games WHERE dir_name = ?', (d_name,))
        d_name = cur.fetchall()

        if len(name):
            return name
        if len(d_name):
            return d_name[0][0]
        return False


def add_reaction(mes, user_id, react, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute(
            f'SELECT user_voted, score FROM games WHERE message_id LIKE "%{mes}%" AND user_voted NOT LIKE "%{user_id}%"'
        )

        res = cur.fetchall()

        if res:
            users, score = res[0]
            users = users.split()
            len_users = len(users)

            cur.execute(f'UPDATE games SET score = ?, user_voted = ? WHERE message_id LIKE "%{mes}%"',
                        ((len_users * score + react) / (len_users + 1), ' '.join(users + [str(user_id)])))

            return True
        return False


def del_reaction(mes, user_id, react, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute(
            f'SELECT user_voted, score FROM games WHERE message_id LIKE "%{mes}%" AND user_voted LIKE "%{user_id}%"')
        res = cur.fetchall()

        if res:
            users, score = res[0]
            users = users.split()
            len_users = len(users)
            del users[users.index(str(user_id))]

            cur.execute(f'UPDATE games SET score = ?, user_voted = ? WHERE message_id LIKE "%{mes}%"',
                        ((len_users * score - react) / ((len_users - 1) if len_users > 1 else 1),
                         ' '.join(users)))

            return True
        return False


def new_game(name, user_id, mes_id, d_name, version, genre, gtype, sys, description, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_added FROM users WHERE user_id = ?', (user_id,))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (user_id, 1, 0, 0))
        else:
            cur.execute('UPDATE users SET num_added = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute(
            'INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0.0, "");',
            (name, user_id, mes_id, d_name, version, genre, gtype, sys, description))

        conn.commit()


def search_game(name=None, genre=None, gtype=None, path=PATH):
    """
    Поиск игр по названию, типу или жанру, если параметры не переданы, выводит все игры.
    :param name:
    :param genre:
    :param gtype:
    :param path:
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        if name is not None:
            cur.execute(f'SELECT * FROM games WHERE name LIKE "%{name}%"')
            res = cur.fetchall()

        elif genre is not None:
            res = set()
            for i in genre:
                cur.execute(f'SELECT * FROM games WHERE genre LIKE "%{i}%"')
                for j in cur.fetchall():
                    res.add(j)

        elif gtype is not None:
            res = set()
            for i in gtype:
                cur.execute(f'SELECT * FROM games WHERE type LIKE "%{i}%"')
                for j in cur.fetchall():
                    res.add(j)

        else:
            cur.execute('SELECT * FROM games')
            res = cur.fetchall()

        return list(res)


def new_download(game_n, user_id, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads FROM users WHERE user_id = ?', (user_id,))
        res = cur.fetchall()
        cur.execute('UPDATE users SET num_downloads = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute('SELECT num_downloads FROM games WHERE name = ?', (game_n,))
        res = cur.fetchall()
        cur.execute('UPDATE games SET num_downloads = ? WHERE name = ?;', (res[0][0] + 1, game_n))

        conn.commit()


def top_games(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT name, num_downloads, score FROM games')
        res = cur.fetchall()

        return sorted(res, reverse=True)[:5]


def top_users(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM users')
        res = cur.fetchall()

        return sorted(res, reverse=True, key=key4users)[:5]


def key4users(a):
    return a[1] * 3 + a[2] + a[3] * 2


def test(p=r'C:\Users\Arkebuzz\Documents\Python\ds_bot\media\game.db'):
    with sqlite3.connect(p) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM games')
        res = cur.fetchall()

        print(res)


if __name__ == '__main__':
    test()
