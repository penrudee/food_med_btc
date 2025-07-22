from pharmbook_app import pharmbook_init,db
import sqlalchemy as sa
import sqlalchemy.orm as so

from pharmbook_app.models import User, Food, Medicine

@pharmbook_init.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Food': Food, 'Medicine':Medicine}