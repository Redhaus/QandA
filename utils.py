from werkzeug.security import check_password_hash


def user_is_valid_user(username, db):
    # query db with user name
    user_cur = db.execute('select id, name, password '
                          'from users where name = ?', [username])
    if user_cur:
        user = user_cur.fetchone()
        return user
    else:
        return False

# def check_password(user, password):
#     return check_password_hash(user['password'], password)