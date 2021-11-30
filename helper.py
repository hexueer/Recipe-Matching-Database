import cs304dbi as dbi

# get uid by username
def getUID(conn, username):
    '''Takes a username and returns the matching uid in the USER table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid
                    FROM user
                    WHERE username = %s''',
                    [username])
    return curs.fetchone()['uid']

# insert recipe
def insert_recipe(conn,title,instructions,tags,post_date,last_updated_date,uid,amounts): 
    '''inserts a recipe into the recipes table in my personal
       database using given params. 
    ''' 
    curs = dbi.dict_cursor(conn)
    try:
        curs.execute('''
            insert into recipe(title,instructions,tag,post_date,last_updated_date,uid)
            values (%s, %s, %s, %s, %s, %s)''', 
                    [title,instructions,tags,post_date,last_updated_date,uid]) 
        conn.commit()
        curs.execute('''
            select rid from recipe 
            order by rid desc''')
        rid = curs.fetchone()

        for a in amounts:
            curs = dbi.dict_cursor(conn)
            curs.execute('''
                insert into uses(rid, iid, amount, measurement_unit)
                values (%s, %s, %s, %s)''', 
                        [rid['rid'], amounts[a]['ingredient'], amounts[a]['amount'], amounts[a]['unit']]) 
            conn.commit()
        curs.close()
        return "success"
    except: 
        curs.close()
        error = "Error uploading recipe."
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

# update recipe

# search recipe

# delete recipe

# ensure valid login
def validate_login(conn, username):
    '''Takes a dbi connection and a username and checks if that username exists in the USER table, returns the matching row'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid,hashed
                    FROM user
                    WHERE username = %s''',
                    [username])
    return curs.fetchone()

# test functions here
if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('iho_db')
    conn = dbi.connect()