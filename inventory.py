from app import app, db
from app.models import User, Admin, Users, Monitors, Desktop, Laptop, Printer, Scanner, Toner, Other, CheckOut

# This decorator is used for testing out database models.
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Admin': Admin,
            'Users': Users, 'Monitors': Monitors, 'Desktop': Desktop,
            'Laptop': Laptop, 'Printer': Printer, 'Scanner': Scanner,
            'Toner': Toner, 'Other': Other, 'CheckOut': CheckOut}
