from flask import Flask, render_template, redirect, url_for, g, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


# add decorators to secure routes

# fires after ever route change and request is made to close db connection
@app.teardown_appcontext
def close_db(error):
    print('teardown fired')
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# check user function for login and registration
def check_user(db, name):
    reg_user_cur = db.execute('select name from users where name = ?', [name])
    return reg_user_cur.fetchone()


# check if user is logged in
def get_current_user():
    user_result = None
    # g.admin = None
    # g.expert = None
    # if there is a logged in user in session
    # set user var and connect to db to get user data
    # populate user_result with data if so
    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cur = db.execute('select id, name, password, expert, admin '
                              'from users where name = ?', [user])

        user_result = user_cur.fetchone()
        # g.admin = user_result['admin']
        # g.expert = user_result['expert']

    # print(g.admin)
    # print(g.expert)

    return user_result


# ALL ACCESS PAGE
@app.route('/')
def home():
    user = get_current_user()
    db = get_db()
    # get question text, and id,
    # as well as asker names and expert names
    # by joining tables twice on different conditions
    # you can grab the specific data you need
    # Create an as alias for the join i.e. as askers
    # then select the data you want from that reference askers,name
    # but give that reference a variable by assigning it as well.
    # askers.name as askers_name

    questions_cur = db.execute('select questions.question_text, '
                               'questions.id as question_id, '
                               'askers.name as asker_name, '
                               'experts.name as expert_name '
                               'from questions '
                               'join users as askers '
                               'on askers.id = questions.asked_by_id '
                               'join users as experts '
                               'on experts.id = questions.expert_id '
                               'where answer_text not null')

    questions = questions_cur.fetchall()

    return render_template('home.html', user=user, questions=questions)


#
#
# Question
# Asked by: Herbert
# Answered by: Anthony

# ALL ACCESS PAGE
@app.route('/register', methods=['POST', 'GET'])
def register():
    # check if user logged in
    user = get_current_user()

    if request.method == 'POST':
        # make db connection
        db = get_db()

        # retrieve form data
        name = request.form['name']
        password = request.form['password']

        if check_user(db, name):
            return render_template('register.html', user=user, error="User already exists")
        else:
            # hash password with hash function and provide format sha256
            hashed_password = generate_password_hash(password, method='sha256')

            # save new user to db
            db.execute('insert into users (name, password, expert, admin) '
                       'values (?, ?, ?, ?)', [name, hashed_password, '0', '0'])
            db.commit()
            session['user'] = name

        return redirect(url_for('home'))

    return render_template('register.html', user=user)


# ALL ACCESS PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    error = None

    if request.method == 'POST':
        db = get_db()

        # retrieve form data
        name = request.form['name']
        password = request.form['password']

        # query db with user name
        user_cur = db.execute('select id, name, password '
                              'from users where name = ?', [name])
        user_result = user_cur.fetchone()

        # if username is incorrect it will return with user incorrent return
        if user_result:
            # if pass doesn't match it will say so'
            if check_password_hash(user_result['password'], password):
                session['user'] = user_result['name']
                return redirect(url_for('home'))
            else:
                error = 'Password is incorrect'
        else:
            error = 'Username is incorrect'

    return render_template('login.html', user=user, error=error)


# ANSWER TO QUESTION FROM HOME PAGE ALL ACCESS
@app.route('/question/<question_id>')
def question(question_id):
    # check if login
    user = get_current_user()

    db = get_db()
    question_cur = db.execute('select question_text, answer_text, '
                              'asker.name as asker_name, '
                              'expert.name as expert_name '
                              'from questions '
                              'inner join users as asker '
                              'on asker.id = questions.asked_by_id '
                              'inner join users as expert '
                              'on expert.id = questions.expert_id '
                              'where questions.id = ?', [question_id])

    question = question_cur.fetchone()
    return render_template('question.html', user=user, question=question)


# <h1>What?</h1>
#         <p>This is the answer.</p>
#         <p><a class="btn btn-primary btn-lg">Asked By: Herbert</a></p>
#         <p><a class="btn btn-primary btn-lg">Answered By: Anthony</a></p>


# ANSWER QUESTIONS PAGE NEED TO BE EXPERT AND LOGGED IN
@app.route('/answer/<question_id>', methods=['POST', 'GET'])
def answer(question_id):
    # check if login
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('no_access'))

    db = get_db()

    if request.method == 'POST':
        answer = request.form['answer'].strip()
        # return f"answer: {answer} id: {question_id}"

        db.execute('update questions set answer_text = ? where id = ?', [answer, question_id])
        db.commit()
        return redirect(url_for('unanswered'))

    question_cur = db.execute('select id, question_text, answer_text '
                              'from questions '
                              'where id = ?', [question_id])
    question = question_cur.fetchone()

    return render_template('answer.html', question=question, user=user)


# ASK A QUESTION NEED TO BE LOGGED IN
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    # check if login
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    # connect to db and fetch all experts
    db = get_db()
    user_cur = db.execute('select * from users where expert = 1')
    experts = user_cur.fetchall()

    # if post get inputs from form and save question, expert and user to db
    # then return them to the home screen
    if request.method == 'POST':
        question = request.form['question']
        expert_id = request.form['expert_id']

        db.execute('insert into questions (question_text, asked_by_id, expert_id) '
                   'values (?,?,?)', [question, user['id'], expert_id])
        db.commit()
        return redirect(url_for('home'))

    # render template passing in user and experts list
    return render_template('ask.html', experts=experts, user=user)


# UNANSWERED QUESTIONS TO BE ANSWERED BY EXPERT, LOGIN AND EXPERT REQUIRED
@app.route('/unanswered', methods=['GET', 'POST'])
def unanswered():
    # check if login need to pass user to template
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('no_access'))

    user_id = user['id']

    db = get_db()
    question_cur = db.execute('select questions.id, question_text, expert_id, users.name as name '
                              'from questions '
                              'inner join users '
                              'on asked_by_id = users.id '
                              'where questions.answer_text is null '
                              'and expert_id = ?', [user_id])
    question_data = question_cur.fetchall()

    return render_template('unanswered.html', user=user, questions=question_data)


# USERS ABILITY TO PROMOTE USERS TO EXPERT AND ADMIN / ADMIN AND LOGIN REQUIRED
@app.route('/users')
def users():
    # check if login

    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('no_access'))

    # fetch all users
    db = get_db()
    users_cur = db.execute('select id, name, expert, admin from users')
    all_users = users_cur.fetchall()

    # pass users to users template
    return render_template('users.html', user=user, all_users=all_users)


# ALL ACCESS NO LOGIN REQUIRED
@app.route('/logout')
def logout():
    # clear session to logout
    # session.pop('user', None) also works
    session['user'] = ''

    return redirect(url_for('.home'))


# ADMIN AND LOGIN REQUIRED
# Promote route elevates users to experts handles logic db update only
# not a visible page called from /users page
@app.route('/users/<user_id>', methods=['POST', 'GET'])
def promote(user_id):
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('no_access'))

    # fetch user info
    db = get_db()
    user_cur = db.execute('select * from users where id = ?', [user_id])
    user = user_cur.fetchone()

    # toggle expert status
    if user['expert'] == 1:
        db.execute('update users set expert = 0 where id = ?', [user_id])
        db.commit()
    else:
        db.execute('update users set expert = 1 where id = ?', [user_id])
        db.commit()

    # reload users with updated values
    return redirect(url_for('users'))


@app.route('/no_access')
def no_access():
    user = get_current_user()

    return render_template('noaccess.html', user=user)


@app.errorhandler(404)
def page_not_found(e):
    user = get_current_user()

    # note that we set the 404 status explicitly
    return render_template('404.html', user=user), 404


if __name__ == '__main__':
    app.run(debug=True)
