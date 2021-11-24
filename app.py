## REMEMBER TO CHANGE THE DATABASE NAME BEFORE YOU TEST

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL) change comment
# characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random
import helper
import bcrypt

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    user = session.get('user','')
    return render_template('index.html', page_title="RMD", user=user)

@app.route('/insert/', methods=['GET', 'POST'])
def insert():
    pass

@app.route('/update/<int:rid>', methods=['GET', 'POST'])
def update(rid):
    pass

@app.route('/search/', methods=['GET', 'POST'])
def search():
    pass

@app.route('/join/', methods=["POST"])
def join():
    username = request.form.get('username')
    passwd = request.form.get('password')
    # if passwd1 != passwd2:
    #     flash('passwords do not match')
    #     return redirect( url_for('index'))
    hashed = bcrypt.hashpw(passwd.encode('utf-8'),
                           bcrypt.gensalt())
    stored = hashed.decode('utf-8')
    print(passwd, type(passwd1), hashed, stored)
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    try:
        curs.execute('''INSERT INTO user(uid,username,hashed)
                        VALUES(null,%s,%s)''',
                     [username, stored])
        conn.commit()
    except Exception as err:
        flash('That username is taken: {}'.format(repr(err)))
        return redirect(url_for('index'))
    curs.execute('select last_insert_id()')
    row = curs.fetchone()
    uid = row[0]
    flash('FYI, you were issued UID {}'.format(uid))
    session['username'] = username
    session['uid'] = uid
    session['logged_in'] = True
    session['visits'] = 1
    return redirect( url_for('user', username=username) )

@app.route('/login/', methods=["POST"])
def login():
    username = request.form.get('username')
    passwd = request.form.get('password')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid,hashed
                    FROM user
                    WHERE username = %s''',
                 [username])
    row = curs.fetchone()
    if row is None:
        # Same response as wrong password
        flash('login incorrect. Try again or join')
        return redirect( url_for('index'))
    stored = row['hashed']
    print('database has stored: {} {}'.format(stored,type(stored)))
    print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
    hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                            stored.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
    if hashed2_str == stored:
        print('they match!')
        flash('successfully logged in as '+username)
        session['username'] = username
        session['uid'] = row['uid']
        session['logged_in'] = True
        session['visits'] = 1
        return redirect( url_for('user', username=username) )
    else:
        flash('login incorrect. Try again or join')
        return redirect( url_for('index'))

@app.route('/logout/')
def logout():
    if 'username' in session:
        username = session['username']
        session.pop('username')
        session.pop('uid')
        session.pop('logged_in')
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('you are not logged in. Please login or join')
        return redirect( url_for('index') )

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    db_to_use = 'iho_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)