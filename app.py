from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi

import random
import helper
import bcrypt
import os
from datetime import date

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def index():
    username = session.get('username','')
    return render_template('index.html', page_title="RMD", user=username)

@app.route('/insert/', methods=['GET', 'POST'])
def insert():
    # logged in?
    if 'username' not in session:
        # flash, cannot insert recipe without being logged in
        error = ['Please log in to insert a recipe.']
        return render_template('index.html', page_title="RMD", error=error)
    else: 
        username = session.get('username')
        conn = dbi.connect()
        ingredientList = helper.get_ingredients(conn)
        tagList = ['breakfast', 'lunch', 'dinner', 'snack', 
                    'vegan', 'vegetarian', 'pescatarian', 
                    'quick meals', 'bake', 'one-pan meal', 
                    'stovetop', 'grill', 'dessert', 'gluten-free', 
                    'microwave', 'keto', 'raw', 'comfort food', 
                    'drinks', 'alcoholic', 'non-alcoholic']
        unitList = ['pinch', 'teaspoon (tsp)', 'tablespoon (tbsp)', 
                    'fluid ounce (fl oz)', 'cup (c)', 'pint (pt)', 
                    'quart (qt)', 'gallon (gal)', 'stick', 
                    'milliliter (mL)', 'liter (L)', 'gram (g)', 
                    'kilogram (kg)', 'ounce (oz)', 'pound (lb)', 
                    'whole', 'slice', 'piece']
        
        if request.method == 'GET':
            return render_template('insert.html', page_title="Insert", user=username, 
                                    ingredients=ingredientList, units=unitList, tags=tagList)
        else: 
            title = request.form['recipe-title'] 
            instructions = request.form['recipe-instructions']
            cook_time = request.form['recipe-time']
            servings = request.form['recipe-servings']
            selectedTagList = request.form.getlist('recipe-tags')
            tags = ", ".join(selectedTagList)

            try:
                image = request.files['recipe-image']
                ext = image.filename.split('.')[-1]
                filename = secure_filename('{}.{}'.format(title.replace(" ", ""), ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                image.save(pathname)
            except: 
                filename = None

            # getting the amounts of each ingredient
            amounts = {}
            i = 1
            # determine how many ingredient form fields were filled in
            while ('ingredient' + str(i)) in request.form.keys(): 
                if request.form['ingredient' + str(i)] != "":  
                    # create string variables in a dictionary for each enumerated form element
                    amounts[str(i)] = {}
                    amounts[str(i)]['ingredient'] = request.form['ingredient' + str(i)]
                    amounts[str(i)]['amount'] = request.form['amount' + str(i)]
                    amounts[str(i)]['unit'] = request.form['unit' + str(i)]
                    i += 1
                else: 
                    break

            post_date = date.today()
            last_updated_date = date.today()

            error = []
            if len(title) == 0: 
                error.append("Please enter a recipe title.")
            if len(instructions) == 0: 
                error.append("Please enter recipe instructions.")
            if len(amounts) == 0: 
                error.append("Please enter at least one ingredient.")
            if len(servings) == 0: 
                error.append("Please enter serving sizes.")
            
            # if there are no error messages
            if len(error) == 0: 
                conn = dbi.connect()
                uid = session['uid']
                try: 
                    # this query will return rid, if successful
                    rid = None
                    added = helper.insert_update_recipe(conn,title,filename,cook_time,int(servings),
                                                instructions,tags,post_date,last_updated_date,
                                                uid,amounts,rid)
                
                    # if the python/sql insert function was successful
                    if type(added) != str:
                        flash('Form submission successful.')
                        return redirect(url_for('recipe', recipe_id = added))
                    else: 
                        error.append(added)
                        return render_template('insert.html', page_title="Insert", 
                                                user=username, error=error, 
                                                ingredients=ingredientList, units=unitList, 
                                                tags=tagList)
                except: 
                    error.append("Error uploading recipe. Please try again.")
                    return render_template('insert.html', page_title="Insert", 
                                                user=username, error=error, 
                                                ingredients=ingredientList, units=unitList, 
                                                tags=tagList)
                
            # if there are error messages
            else: 
                return render_template('insert.html', page_title="Insert", user=username, 
                                        error=error, ingredients=ingredientList, 
                                        units=unitList, tags=tagList)      

@app.route('/pic/<filename>')
def pic(filename):
    if filename == None: 
        return "No image found"
    return send_from_directory(app.config['UPLOADS'],filename)

@app.route('/update/<int:rid>', methods=['GET', 'POST'])
def update(rid):
    # logged in?
    if 'username' in session:
        username = session.get('username')
        uid = session.get('uid')
        conn = dbi.connect()
        
        try:
            recipe, creator = helper.recipe_lookup(conn, rid)
            # just in case html falls through
            if uid != creator['uid']:
                flash("You are not the author of this page!")
                return redirect(url_for('recipe', recipe_id = rid))
            ingredients = helper.get_recipe_ingredients(conn, rid)

            ingredientList = helper.get_ingredients(conn)
            tagList = ['breakfast', 'lunch', 'dinner', 'snack', 
                        'vegan', 'vegetarian', 'pescatarian', 
                        'quick meals', 'bake', 'one-pan meal', 
                        'stovetop', 'grill', 'dessert', 'gluten-free', 
                        'microwave', 'keto', 'raw', 'comfort food', 
                        'drinks', 'alcoholic', 'non-alcoholic']
            unitList = ['pinch', 'teaspoon (tsp)', 'tablespoon (tbsp)', 
                        'fluid ounce (fl oz)', 'cup (c)', 'pint (pt)', 
                        'quart (qt)', 'gallon (gal)', 'stick', 
                        'milliliter (mL)', 'liter (L)', 'gram (g)', 
                        'kilogram (kg)', 'ounce (oz)', 'pound (lb)', 
                        'whole', 'slice', 'piece']
        except:
            return render_template('error.html', page_title="Error")

        # if post
        if request.method == 'POST':
            # update recipe
            title = request.form['recipe-title'] 
            instructions = request.form['recipe-instructions']
            cook_time = request.form['recipe-time']
            servings = request.form['recipe-servings']
            selectedTagList = request.form.getlist('recipe-tags')
            tags = ", ".join(selectedTagList)
            try:
                image = request.files['recipe-image']
                ext = image.filename.split('.')[-1]
                filename = secure_filename('{}.{}'.format(title.replace(" ", ""), ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                image.save(pathname)
            except: 
                filename = None
            # getting the amounts of each ingredient
            amounts = {}
            i = 1
            # determine how many ingredient form fields were filled in
            while ('ingredient' + str(i)) in request.form.keys(): 
                if request.form['ingredient' + str(i)] != "":  
                    # create string variables in a dictionary for each enumerated form element
                    amounts[str(i)] = {}
                    amounts[str(i)]['ingredient'] = request.form['ingredient' + str(i)]
                    amounts[str(i)]['amount'] = request.form['amount' + str(i)]
                    amounts[str(i)]['unit'] = request.form['unit' + str(i)]
                    i += 1
                else: 
                    break

            last_updated_date = date.today()
            error = []
            # check for duplicated title
            if not helper.check_title(conn, title, rid): 
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
                uid = session['uid']
                try: 
                    post_date=None
                    # this query will return rid, if successful
                    helper.insert_update_recipe(conn,title,filename,cook_time,int(servings),
                                                instructions,tags,post_date,last_updated_date,
                                                uid,amounts,rid)
                    flash('Form submission successful.')
                    return redirect(url_for('recipe', recipe_id = rid))
                except: 
                    return render_template('update.html', 
                                page_title="Update", 
                                error=error,
                                user=username, 
                                rid=rid, 
                                recipe=recipe,
                                ingredients=ingredients, 
                                ingredientList=ingredientList, 
                                units=unitList, 
                                tags=tagList)
            # there are error messages
            else: 
                return render_template('update.html', 
                                        page_title="Update", 
                                        error=error,
                                        user=username, 
                                        rid=rid, 
                                        recipe=recipe,
                                        ingredients=ingredients, 
                                        ingredientList=ingredientList, 
                                        units=unitList, 
                                        tags=tagList)      

        # if get
        else:
            return render_template('update.html', 
                                    page_title="Update", 
                                    user=username, 
                                    rid=rid, 
                                    recipe=recipe,
                                    ingredients=ingredients, 
                                    ingredientList=ingredientList, 
                                    units=unitList, 
                                    tags=tagList
                                    )

    else:
        # flash, cannot update recipe without being logged in
        error = ['Please log in to update a recipe.']
        return render_template('index.html', page_title="RMD", error=error)

@app.route('/delete/<int:rid>', methods=['POST'])
def delete(rid):
    # logged in?
    if 'username' in session:
        username = session.get('username')
        uid = session.get('uid')
        conn = dbi.connect()

        # delete old image
        oldimage = helper.get_recipe_image_path(conn, rid)
        if oldimage != None: 
            pathname = os.path.join(app.config['UPLOADS'],oldimage)
            if os.path.exists(pathname):
                os.remove(pathname)
            else:
                print("The file does not exist")

        # flash confirmation and prompt for button resubmission
        deleted = helper.delete_recipe(conn, rid)
        # returns -1 if deletion affected 0 rows
        if deleted == -1:
            flash("Error deleting recipe. Try again.")
        else:
            flash("Recipe {} deleted.".format(rid))

        return redirect(url_for('index', page_title="RMD"))

    else:
        # flash, cannot update recipe without being logged in
        error = ['Please log in to delete a recipe.']
        return render_template('index.html', page_title="RMD", error=error)
        

@app.route('/search/', methods=['GET', 'POST'])
def search():
    username = session.get('username')
    conn = dbi.connect()
    ingredientList = helper.get_ingredients(conn)
    if request.method == 'GET':
        return render_template('search.html', page_title="Search", 
                                user=username, ingredients=ingredientList)
    else:
        #title input
        title = request.form['recipe-title'] 
        #list of user selected ingredients
        selectedIngredients = request.form.getlist('recipe-ingredients')
        #parse selected ingredients
        selectedIngredients = selectedIngredients[0].strip(',').split(',')
        #ensure that an empty string is not considered as input
        if len(selectedIngredients) ==1:
            if selectedIngredients[0] == "":
                selectedIngredients = []

        #Search by both title and ingredients
        #set search results if title input exists
        if len(title) > 0: 
            searchResults = helper.search_titles(conn,title)
        #set search results if selected ingredient input exists
        elif len(selectedIngredients) > 0:
            searchResults = helper.search_ingredients(conn,helper.get_iid(conn,selectedIngredients))

        #set search results if both title and ingredients input exist
        if len(title) > 0 and len(selectedIngredients) > 0:
            #merging search results to use the helper search function with 
            #both title and ingredients
            title_searchResults = helper.search_titles(conn,title)
            ingredient_searchResults = helper.search_ingredients(conn,helper.get_iid(conn,selectedIngredients))
            searchResults = helper.search_title_ingredients(conn, title_searchResults,ingredient_searchResults)

        #if recipes were not found
        if len(title) == 0 and len(selectedIngredients) == 0:
            searchResults = []
        if len(searchResults) < 1:
            error = ['No recipes matched your search.']
            return render_template('search.html', page_title="Search", user=username, 
                                    error=error,ingredients=ingredientList)
        #if there are results then display them
        else:
            return render_template('search.html', page_title="Search", user=username, 
                                    ingredients=ingredientList, searchResults=searchResults)       

    error = []
    if len(title) == 0 and len(selectedIngredients) == 0:
        error.append("Please enter either a recipe title or select ingredients.")
    
    # if there are error messages
    else:
        return render_template('search.html', page_title="Search", user=username, 
                                error=error, ingredients=ingredientList)
    
    return render_template('search.html', error=error, page_title="Search")

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    conn = dbi.connect()
    username = session.get('username')
    uid = session.get('uid')
    try:
        recipe, creator = helper.recipe_lookup(conn, recipe_id)
        ingredients = helper.get_recipe_ingredients(conn, recipe_id)
    except:
        error = ['Sorry, the recipe you are looking for is not in the database.']
        return render_template('index.html', page_title="RMD", error=error)

    instructions = recipe['instructions'].split('. ')

    for instruction in instructions:
        if (instruction.strip()).isdigit() or instruction == '':
            instructions.remove(instruction)
    return render_template('recipe.html', 
                            instructions = instructions, 
                            user=username, uid=uid, recipe = recipe, 
                            filename=recipe['image_path'], page_title="Recipe",
                            creator = creator, ingredients = ingredients, 
                            recipe_id = recipe_id)

@app.route('/profile/')
def profile():
    conn = dbi.connect()
    if 'username' in session:
        username = session.get('username')
        recipes = helper.get_user_recipes(conn, username)
        # profile code
        return render_template('profile.html', user = username, recipes = recipes, page_title = "Profile")
    else:
        # flash, cannot update recipe without being logged in
        error = ['Please log in to access your profile page.']
        return render_template('index.html', page_title="RMD", error=error)
    
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
                return redirect( url_for('index', page_title="RMD"))
            hashed = bcrypt.hashpw(passwd.encode('utf-8'),
                                bcrypt.gensalt())
            stored = hashed.decode('utf-8')

            conn = dbi.connect()
            curs = dbi.cursor(conn)
            try:
                curs.execute('''INSERT INTO user(name,email,username,hashed)
                                VALUES(%s, %s, %s, %s)''',
                            [fullname, email, username, stored])
                conn.commit()

            except Exception as err:
                flash('That username is taken: {}'.format(repr(err)))
                return redirect(url_for('index', page_title="RMD"))

            curs.execute('select last_insert_id()')
            row = curs.fetchone()
            uid = row[0]
            flash('FYI, you were issued UID {}'.format(uid))
            session['username'] = username
            session['uid'] = uid
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('index', page_title="RMD", user=username) )

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
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    stored.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            if hashed2_str == stored:
                flash('successfully logged in as '+username)
                session['username'] = username
                session['uid'] = row['uid']
                session['logged_in'] = True
                session['visits'] = 1
                return redirect( url_for('index', page_title="RMD", user=username) )
            else:
                flash('login incorrect. Try again or join')
                return redirect( url_for('login', page_title="Login/Register"))

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
        return redirect( url_for('index', page_title="RMD") )

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    db_to_use = 'recipes_db' 
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
