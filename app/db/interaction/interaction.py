from app.db.client.client import MySQLConnetion
from app.db.models.models import Base, User
from app.db.Exceptions import UserNotFoundException



class DbInteraction:
    def __init__(self, host, port, user, password, db_name, rebuild_db=False):
        self.mysql_connection = MySQLConnetion(
            host=host,
            user=user,
            port=port,
            password=password,
            db_name=db_name,
            rebuild_db=rebuild_db,
        )

        self.engine = self.mysql_connection.connection.engine

        if rebuild_db:
            self.create_table_users()
            self.create_table_musical_compositions()

    def create_table_users(self):
        if not self.engine.dialect.has_table(self.mysql_connection.connection, 'users'):
            Base.metadata.tables['users'].create(self.engine)
        else:
            self.mysql_connection.execute_query('DROP TABLE IF EXISTS users')
            Base.metadata.tables['users'].create(self.engine)

    def create_table_musical_compositions(self):
        if not self.engine.dialect.has_table(self.mysql_connection.connection, 'musical_compositions'):
            Base.metadata.tables['musical_compositions'].create(self.engine)
        else:
            self.mysql_connection.execute_query('DROP TABLE IF EXISTS musical_compositions')
            Base.metadata.tables['musical_compositions'].create(self.engine)

    def add_user_info(self, username, email, password):
        user = User(
            username=username,
            password=password,
            email=email,
        )
        self.mysql_connection.session.add(user)
        return self.get_user_info(username)

    def get_user_info(self, username):
        user = self.mysql_connection.session.query(User).filter_by(username=username).first()
        if user:
            self.mysql_connection.session.expire_all()
            return {"username": user.username, 'email': user.email, 'password': user.password}
        else:
            raise UserNotFoundException("User not found!")

    def edit_user_info(self, username, new_username=None, new_email=None, new_password=None):
        user = self.mysql_connection.session.query(User).filter_by(username=username).first()
        if user:
            if new_username is not None:
                user.username = new_username
            if new_email is not None:
                user.email = new_email
            if new_password is not None:
                user.password = new_password
            return self.get_user_info(username)
        else:
            raise UserNotFoundException("User not found")


if __name__  == '__main__':
    db = DbInteraction(
        host='127.0.0.1',
        port=3386,
        user='root',
        password='pass',
        db_name='some_db',
        rebuild_db=True,
    )
