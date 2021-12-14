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

def insert_recipe(conn,title,imagepath,cook_time,servings,instructions,tags,post_date,last_updated_date,uid,amounts): 
    '''inserts a recipe into the recipes table in my personal
       database using given params. 
    ''' 
    curs = dbi.dict_cursor(conn)
    # try:
    # insert the recipe into recipe
    curs.execute('''
        insert into recipe(title,image_path,cook_time,servings,instructions,tag,post_date,last_updated_date,uid)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                [title,imagepath,cook_time,servings,instructions,tags,post_date,last_updated_date,uid]) 
    conn.commit()
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
    # except: 
    #     curs.close()
    #     error = "Error uploading recipe."
    #     return error

def check_title(conn, title): 
    '''selects titles from recipe like given title parameter
       returns True if no matches found, false if another 
       recipe already exists. 
    ''' 
    curs = dbi.dict_cursor(conn)
    try:
        curs.execute('''
            select title from recipe
            where title = %s''', 
                    [title]) 
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
        return (["Recipe does not exist"], "Error", "Error")

    curs.execute('''select user.name from user 
                    join recipe using (uid)
                    where recipe.rid = %s''', [rid])
    user_name = curs.fetchone()
    #get ingredients with name, amount and measurement_unit
    return (recipe, user_name)

def search_ingredients(conn,ingredients):
    '''Searches by ingredients: finds if user search input 
       matches recipes in recipe database using given params. 
    ''' 
    curs = dbi.dict_cursor(conn)
    placeholders = 'iid = %s or ' * (len(ingredients)-1)
    curs.execute('''select distinct uses.rid, recipe.title
                    from uses inner join recipe using (rid)
                    where ''' + placeholders + '''iid = %s
                    '''
                    ,ingredients)
    return curs.fetchall()

def search_titles(conn,title):
    '''Searches by title: returns data of recipes with a 
       title similar to the provided query, as a dictionary.
    '''
    curs = dbi.dict_cursor(conn)
    #make sure that the title is more than 1 letter because otherwise all recipe titles with that letter is returned
    if len(title) == 1:
        return []
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
    titles_formatted = []
    for i in titles:
        i = "%" + i['title'] + "%"
        titles_formatted.append(i)
    ingredients_formatted = []
    for i in ingredients:
        i = i['title']
        ingredients_formatted.append(i)
    keys = titles_formatted +ingredients_formatted
    placeholders = 'title = %s or ' * (len(keys)-1)
    curs.execute('''select distinct uses.rid, recipe.title
                    from uses inner join recipe using (rid)
                    where ''' + placeholders + '''title = %s
                    '''
                    ,keys)
    return curs.fetchall()
    
def get_recipe_ingredients(conn, rid): 
    '''Returns all ingredient ids and names.
    ''' 
    curs = dbi.dict_cursor(conn)
    curs.execute('''select uses.rid, ingredient.name, uses.amount, uses.measurement_unit 
                    from uses 
                    inner join ingredient using (iid) 
                    where rid = %s''', 
                    [rid])
    return curs.fetchall()
    

# update recipe


# delete recipe

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
    dbi.use('ac5_db')
    conn = dbi.connect()