import cs304dbi as dbi

def getUID(conn, username):
    '''Takes a username and returns the matching uid in 
       the USER table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid
                    FROM user
                    WHERE username = %s''',
                    [username])
    return curs.fetchone()['uid']

def insert_update_recipe(conn,title,imagepath,cook_time,servings,instructions,tags,post_date,last_updated_date,uid,amounts,rid): 
    '''inserts a recipe into the recipes table
       using given params. 
       if the recipe already exists, we then only update 
       a row with new values (may be equivalent) for each 
       attribute in the Recipe table for a specific rid, 
       will ignore imagepath if none'''
    try:
        curs = dbi.dict_cursor(conn)

        # if we are inserting instead of updating
        if rid == None: 
            try: 
                curs.execute('''insert into recipe(title,image_path,cook_time,
                                                servings,instructions,tag,
                                                post_date,last_updated_date,uid)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                                [title,imagepath,cook_time,servings,instructions,tags,post_date,last_updated_date,uid]) 
                conn.commit()

                try: 
                    curs.execute('select last_insert_id()')
                    rid = curs.fetchone()
                    # insert the amounts into uses
                    for a in amounts:
                        curs = dbi.dict_cursor(conn)
                        curs.execute('''
                            insert into uses(rid, iid, amount, measurement_unit)
                            values (%s, %s, %s, %s)''', 
                                    [rid['last_insert_id()'], amounts[a]['ingredient'], amounts[a]['amount'], amounts[a]['unit']]) 
                        conn.commit()
                    curs.close()
                    return rid['last_insert_id()']
                except:
                    curs.close()
                    error = "Error inserting recipe. Please try again."
                    return error
            except: 
                # the title column is unique, so there was an attempted duplicated title
                curs.close()
                error = "Sorry, that title already exists. Please try another."
                return error            
        else: 
            # if we are updating instead of inserting (rid is populated)
            try: 
                if imagepath == None or '.' not in imagepath:
                    oldimage = None
                    curs.execute('''update recipe set
                                    title = %s, 
                                    cook_time = %s, 
                                    servings = %s, 
                                    instructions = %s, 
                                    tag = %s, 
                                    last_updated_date = %s
                                    where rid = %s''',
                                    [title,cook_time,servings,instructions,tags,last_updated_date,rid])
                else:
                    curs.execute('''update recipe set
                                    title = %s, 
                                    image_path = %s, 
                                    cook_time = %s, 
                                    servings = %s, 
                                    instructions = %s, 
                                    tag = %s, 
                                    last_updated_date = %s
                                    where rid = %s''',
                                    [title,imagepath,cook_time,servings,instructions,tags,last_updated_date,rid])
                conn.commit()

                # delete all previous ingredient entries
                curs.execute('''delete from uses where rid = %s''',
                                [rid])
                conn.commit()

                # insert the amounts into uses
                for a in amounts:
                    curs = dbi.dict_cursor(conn)
                    curs.execute('''
                        insert into uses(rid, iid, amount, measurement_unit)
                        values (%s, %s, %s, %s)''', 
                                [rid, amounts[a]['ingredient'], amounts[a]['amount'], amounts[a]['unit']]) 
                    conn.commit()
                curs.close()

                return rid
            except: 
                curs.close()
                error = "Error updating recipe entry. Please try again."
                return error
    except: 
        curs.close()
        error = "Error uploading recipe."
        return error


def check_title(conn, title, rid=None): 
    '''selects titles from recipe like given title parameter
       returns True if no matches found, false if another 
       recipe already exists. 
    ''' 
    curs = dbi.dict_cursor(conn)
    try:
        if rid == None:
            curs.execute('''
                select title from recipe
                where title = %s''', 
                        [title]) 
        else:
            curs.execute('''
                select title from recipe
                where title = %s and rid <> %s''', 
                        [title, rid]) 
        titles = curs.fetchall()
        return len(titles) == 0
    except: 
        curs.close()
        error = "Error checking for duplicate recipes."
        return error

def get_ingredients(conn): 
    '''Returns all ingredient ids and names.
    ''' 
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * 
        from ingredient
        order by name''')
    return curs.fetchall()

def recipe_lookup(conn, rid):
    '''Returns recipe data from given rid parameter.
    ''' 
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from recipe 
                    where rid = %s''', [rid])
    recipe = curs.fetchone()

    # if recipe does not exist
    if recipe is None: 
        return ("Recipe does not exist")

    curs.execute('''select user.name, user.uid from user 
                    join recipe using (uid)
                    where recipe.rid = %s''', [rid])
    user = curs.fetchone()
    #get ingredients with name, amount and measurement_unit
    return (recipe, user)

def get_iid(conn, ingredients):
    '''Takes one or more ingredient names and returns the matching iids in 
       the ingredient table. We use fetchall() here in case users
       enter more than one ingredient.'''
    curs = dbi.dict_cursor(conn)
    placeholders = 'name = %s or ' * (len(ingredients)-1)
    curs.execute('''SELECT iid
                    FROM ingredient
                    WHERE '''+ placeholders + '''name = %s
                    ''',
                    ingredients)
    return curs.fetchall()

def search_ingredients(conn,ingredients):
    '''Searches by ingredients: finds if user search input 
       matches recipes in recipe database using given params. 
    ''' 
    curs = dbi.dict_cursor(conn)
    placeholders = 'iid = %s or ' * (len(ingredients)-1)
    all_ingredients = [i['iid'] for i in ingredients]

    curs.execute('''select distinct uses.rid, recipe.image_path, recipe.title
                    from uses inner join recipe using (rid)
                    where ''' + placeholders + '''iid = %s
                    '''
                    ,all_ingredients)
    return curs.fetchall()

def search_titles(conn,title):
    '''Searches by title: returns data of recipes with a 
       title similar to the provided query, as a dictionary.
    '''
    curs = dbi.dict_cursor(conn)
    title = "%" + title + "%"
    curs.execute('''
        select * 
        from recipe
        where title like %s''',
                 [title])
    return curs.fetchall()

def search_title_ingredients(conn,titles,ingredients):
    '''Searches and returns data of recipes with given titles and ingredients'''
    curs = dbi.dict_cursor(conn)
    # strip the list of titles of punctuations, etc. 
    titles_formatted = [i['title'].strip() for i in titles]
    # build the list of ingredients 
    ingredients_formatted = [i['title'] for i in ingredients]

    # select distinct titles and ingredients from sql table to search
    keys = titles_formatted + ingredients_formatted
    placeholders = 'title = %s or ' * (len(keys)-1)
    curs.execute('''select distinct uses.rid, recipe.title, recipe.image_path
                    from uses inner join recipe using (rid)
                    where ''' + placeholders + '''title = %s
                    '''
                    ,keys)
    return curs.fetchall()
    
def get_recipe_ingredients(conn, rid): 
    '''Returns all ingredient ids and names.
    ''' 
    curs = dbi.dict_cursor(conn)
    curs.execute('''select uses.rid, uses.iid, ingredient.name, uses.amount, uses.measurement_unit 
                    from uses 
                    inner join ingredient using (iid) 
                    where rid = %s''', 
                    [rid])
    return curs.fetchall()

# get recipes from username
def get_user_recipes(conn, username):
    '''Returns all the recipes from the given username'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct recipe.rid, recipe.image_path, recipe.title
                    from recipe inner join user using (uid) 
                    where username = %s''', [username])
    return curs.fetchall()

def get_recipe_image_path(conn, rid):
    '''Gets image_path from recipe table given rid.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select image_path 
                    from recipe 
                    where rid = %s''',
                    [rid])
    return curs.fetchone()['image_path']

# delete recipe
def delete_recipe(conn, rid):
    '''Deletes a recipe from the Recipe table given a specific rid value
        and deletes associated rows from the uses table as well.
    '''
    curs = dbi.dict_cursor(conn)
    # delete all previous ingredient entries
    curs.execute('''delete from uses where rid = %s''',
                    [rid])
    conn.commit()
    # delete recipe entry
    curs.execute('''delete from recipe where rid = %s''',
                    [rid])
    conn.commit()
    
    # gets num of affected rows by PREVIOUS STATEMENT
    # we determine whether the deletion was successful in app.py
    # depending on the number of rows that were affected
    curs.execute('''SELECT ROW_COUNT()''')
    return curs.fetchone()['ROW_COUNT()']

def validate_login(conn, username):
    '''Ensures valid login - takes a dbi connection and a 
       username and checks if that username exists in the 
       USER table, returns the matching row'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid,hashed
                    FROM user
                    WHERE username = %s''',
                    [username])
    return curs.fetchone()

# test functions here
if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('recipes_db')
    conn = dbi.connect()