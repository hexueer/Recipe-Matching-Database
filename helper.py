import cs304dbi as dbi

# insert recipe

# update recipe

# search recipe

# delete recipe

# test functions here
if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('iho_db')
    conn = dbi.connect()