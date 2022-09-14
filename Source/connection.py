import psycopg2
#from config import config


class Postgre:
    conn = None

    @staticmethod
    def connect():
        """ Connect to the PostgreSQL database server """
        if Postgre.conn is None:
            conn = None
            try:
                # read connection parameters
                params = {'host': 'localhost', 'database' : 'dvdrental', 'user' : 'postgres', 'password' : 'sys'} #config()

                # connect to the PostgreSQL server
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)

                # create a cursor
                cur = conn.cursor()

                # execute a statement
                print('PostgreSQL database version:')
                cur.execute('SELECT version()')

                # display the PostgreSQL database server version
                db_version = cur.fetchone()
                print(db_version)

                # close the communication with the PostgreSQL
                cur.close()

                Postgre.conn = conn
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

        return Postgre.conn

    @staticmethod
    def close_connection():
        if Postgre.conn is not None:
            Postgre.conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    convar = Postgre.connect()
    print(convar)
    curr = convar.cursor()
    curr.execute(
        """SELECT * FROM film"""
    )
    res = curr.fetchall()
    curr.close()