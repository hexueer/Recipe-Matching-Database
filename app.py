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
from datetime import date

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
    username = session.get('username','')
    return render_template('index.html', page_title="RMD", user=username)

@app.route('/insert/', methods=['GET', 'POST'])
def insert():
    # logged in?
    if 'username' in session:
        username = session.get('username')
        conn = dbi.connect()
        ingredientList = helper.get_ingredients(conn)
        tagList = ['breakfast', 'lunch', 'dinner', 'snack', 'vegan', 'vegetarian', 'pescatarian', 'quick meals', 'bake', 'one-pan meal', 'stovetop', 'grill', 'dessert', 'gluten-free', 'microwave', 'keto', 'raw', 'comfort food', 'drinks', 'alcoholic', 'non-alcoholic']
        unitList = ['pinch', 'teaspoon (tsp)', 'tablespoon (tbsp)', 'fluid ounce (fl oz)', 'cup (c)', 'pint (pt)', 'quart (qt)', 'gallon (gal)', 'stick', 'milliliter (mL)', 'liter (L)', 'gram (g)', 'kilogram (kg)', 'ounce (oz)', 'pound (lb)', 'whole', 'slice', 'piece']
        
        if request.method == 'GET':
            return render_template('insert.html', page_title="Insert", user=username, ingredients=ingredientList, units=unitList, tags=tagList)
        else: 
            title = request.form['recipe-title'] 
            instructions = request.form['recipe-instructions']
            selectedTagList = request.form.getlist('recipe-tags')
            tags = ""
            for i in range(len(selectedTagList)): 
                tags += selectedTagList[i]
                if i < len(selectedTagList)-1: 
                    tags += ","

            amounts = {}
            for i in range(1, 6): 
                i = str(i)
                if request.form['ingredient' + i] != "": 
                    amounts[i] = {}
                    amounts[i]['ingredient'] = request.form['ingredient' + i]
                    amounts[i]['amount'] = request.form['amount' + i]
                    amounts[i]['unit'] = request.form['unit' + i]

            post_date = date.today()
            last_updated_date = date.today()

            error = []
            # check for duplicated title
            if not helper.check_title(conn, title): 
                error.append("Sorry, this recipe title already exists. Please choose another.")
            if len(title) == 0: 
                error.append("Please enter a recipe title.")
            if len(instructions) == 0: 
                error.append("Please enter recipe instructions.")
            if len(amounts) == 0: 
                error.append("Please enter at least one ingredient.")
            
            # if there are no error messages
            if len(error) == 0: 
                conn = dbi.connect()
                uid = helper.getUID(conn, username)
                added = helper.insert_recipe(conn,title,instructions,tags,post_date,last_updated_date,uid,amounts)
                # if the python/sql insert function was successful, thus returning a string 'success'
                if added == "success":
                    flash('Form submission successful.')
                    recipe = helper.get_recipe(conn, title)
                    #rid = helper.recipe_lookup(conn, recipe['rid'])
                    return redirect(url_for('recipe', recipe_id = recipe['rid']))
                    # return redirect(url_for('update', rid=tt))
                else: #probably a duplicate error
                    error.append(added)
                    return render_template('insert.html', page_title="Insert", user=username, error=error, ingredients=ingredientList, units=unitList, tags=tagList)
            # if there are error messages
            else: 
                return render_template('insert.html', page_title="Insert", user=username, error=error, ingredients=ingredientList, units=unitList, tags=tagList) 
    else:
        # flash, cannot insert recipe without being logged in
        error = ['Please log in to insert a recipe.']
        return render_template('index.html', error=error)

@app.route('/update/<int:rid>', methods=['GET', 'POST'])
def update(rid):
    # logged in?
    if 'username' in session:
        username = session.get('username')
        # update code
    else:
        # flash, cannot update recipe without being logged in
        error = ['Please log in to update a recipe.']
        return render_template('index.html', error=error)

@app.route('/search/', methods=['GET', 'POST'])
def search():
    username = session.get('username')
    conn = dbi.connect()
    #the get_ingredients function uses conn which means we need to be 
    #connected to the database by being logged in in order to access 
    #the ingredients, which is why a user must be logged in to search for
    #a recipe versus what we initially planned
    ingredientList = helper.get_ingredients(conn)
    if request.method == 'GET':
        return render_template('search.html', page_title="Search", user=username, ingredients=ingredientList)
    else: 
        title = request.form['recipe-title'] 
        #list of user selected ingredients
        selectedIngredients = request.form.getlist('recipe-ingredients')

        error = []
        if len(title) == 0 and len(selectedIngredients) == 0: 
            error.append("Please enter either a recipe title or select ingredients.")
        
        # if there are no error messages
        if len(error) == 0: 
            conn = dbi.connect()
            #we cannot store any user's searches because they do not have their personal databases
            searchResults = helper.searching(conn,title,selectedIngredients)
            #if recipes were not found
            if len(searchResults) < 1:
                error = ['No recipes matched your search.']
                return render_template('search.html', page_title="Search", user=username, error=error)
                # return redirect(url_for('update', oldtt=tt))
            #if there are results then display them
            else:
                results = 1
                return render_template('search.html', page_title="Search", user=username, error=error, ingredients=ingredientList, results=results,searchResults=searchResults)

        # if there are error messages
        else: 
            return render_template('search.html', page_title="Search", user=username, error=error, ingredients=ingredientList)
        
    return render_template('search.html')

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    conn = dbi.connect()
    username = session.get('username') if 'username' in session else None

    try:
        recipe, creator = helper.recipe_lookup(conn, recipe_id)
        ingredients = helper.get_recipe_ingredients(conn, recipe_id)
        print(ingredients)
    except:
        return render_template('error.html')
    # tags = recipe.tag.split(",")
    return render_template('recipe.html', page_title="Recipe", user=username, recipe = recipe, creator = creator, ingredients = ingredients)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # render login/register page first
    if request.method == 'GET':
        return render_template('login.html', page_title="Login/Register")

    else:
        # if first-time user
        if request.form['submit'] == 'register':
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            username = request.form.get('username')
            passwd = request.form.get('password')
            passwd2 = request.form.get('password2')
            if passwd != passwd2:
                flash('passwords do not match')
                return redirect( url_for('index'))
            hashed = bcrypt.hashpw(passwd.encode('utf-8'),
                                bcrypt.gensalt())
            stored = hashed.decode('utf-8')
            # print(passwd, type(passwd), hashed, stored)

            conn = dbi.connect()
            curs = dbi.cursor(conn)
            try:
                curs.execute('''INSERT INTO user(name,email,username,hashed)
                                VALUES(%s, %s, %s, %s)''',
                            [fullname, email, username, stored])
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
            return redirect( url_for('index', page_title="RMD", user=username) )
            # return redirect( url_for('user', username=username) )

        # else login
        else:
            username = request.form.get('username')
            passwd = request.form.get('password')

            conn = dbi.connect()
            row = helper.validate_login(conn, username)
            if row is None:
                # Same response as wrong password
                flash('login incorrect. Try again or join')
                return redirect( url_for('login'))
            stored = row['hashed']
            # print('database has stored: {} {}'.format(stored,type(stored)))
            # print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    stored.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            # print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
            if hashed2_str == stored:
                # print('they match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['uid'] = row['uid']
                session['logged_in'] = True
                session['visits'] = 1
                return redirect( url_for('index', page_title="RMD", user=username) )
                # return redirect( url_for('user', username=username) )
            else:
                flash('login incorrect. Try again or join')
                return redirect( url_for('login'))

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
    db_to_use = 'ac5_db' 
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