import cs304dbi as dbi

# insert recipe

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