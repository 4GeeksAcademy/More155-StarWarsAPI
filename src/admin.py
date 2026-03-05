import os
from flask_admin import Admin
from models import db, User, Characters, Planets, Liked_Characters, Liked_Planets
from flask_admin.contrib.sqla import ModelView


class Liked_CharactersAdmin(ModelView):
    column_list = ('id', 'user', 'character', 'date')
    form_columns = ('user', 'character', 'date')


class Liked_PlanetsAdmin(ModelView):
    column_list = ('id', 'user', 'planet', 'date')
    form_columns = ('user', 'planet', 'date')


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(Characters, db.session))
    admin.add_view(ModelView(Planets, db.session))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(Liked_CharactersAdmin(Liked_Characters, db.session))
    admin.add_view(Liked_PlanetsAdmin(Liked_Planets, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
