from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm,\
    EditProfileForm, AdminUserForm, ImportUserForm, EditImportForm, SearchUserForm, \
    InventoryForm, CheckOutForm, TonerForm
from app.models import User, Admin, Users, Monitors, Desktop, Laptop, \
    Printer, Scanner, Toner, Other, CheckOut
from app.tables import Results, Inventory, Checkout, TonerInventory
from sqlalchemy import or_
import os
import logging
from logging.handlers import RotatingFileHandler
from app.email import send_password_reset_email

# This snippet of code allows logging of commits within the following functions:
# manage_users, import_user, edit.
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/commit.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


# Each time a user is logged into the inventory system, this function
# logs the time of login in a variable.
@ app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Loads the homepage
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home')

# Login page with LoginForm class that validates if user is in the system.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Logout function.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register in the system with RegistrationForm class
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Request to get a password
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

# Reset password function
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# Used to locate current user in system by checking against username.
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# The function is used to edit the current user profile.
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

# The Admin Console is used to give registered users the ability to delete, add, and remove
# users from the database. This function will also expand on other abilities such as
# deleting records in the database also.
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def manage_users():
    if Admin.query.filter_by(user=current_user.username).first():
        form = AdminUserForm(request.form)
        form.select_field.choices = [(u.id, u.username) for u in User.query.all()]
        target = request.form.get('select_field')
        option = request.form.get('radio_field')
        if form.validate_on_submit() and option == 'option1':
            if isinstance(Admin.query.filter_by(id=target).first(), Admin):
                flash('{} is already an Administrator'.format(User.query.get(target).username))
                return redirect(url_for('manage_users'))

            else:
                admin = Admin(str(User.query.get(target).username),
                              admin_username=User.query.get(target))
                db.session.add(admin)
                db.session.commit()
                app.logger.info('[Committed by user]: ' + str(current_user.username) + ' ' + str(admin.user) + ' created')
                flash('You added {} as an administrator'.format(admin.user))
                return redirect(url_for('manage_users'))

        if form.validate_on_submit() and option == 'option2':
            if Admin.query.filter_by(id=target).first().user == current_user.username:
                flash('You cannot remove yourself')
                return redirect(url_for('manage_users'))

            else:
                admin = Admin.query.filter_by(user=current_user.username).first()
                deleted = Admin.query.filter_by(user=User.query.get(target).username).first()
                admin.delete_admin(deleted)
                app.logger.info('[Committed by user]: ' + str(current_user.username) + ' ' + str(deleted.user) + ' removed from Administrator group')
                flash('{} was removed as an admin'.format(deleted.user))
                return redirect(url_for('manage_users'))

        if form.validate_on_submit() and option == 'option3':
            if User.query.filter_by(id=target).first().username == current_user.username:
                flash('You cannot delete yourself')
                return redirect(url_for('manage_users'))

            else:
                admin = Admin.query.filter_by(user=current_user.username).first()
                deleted = User.query.filter_by(username=User.query.get(target).username).first()
                admin.delete_user(deleted)
                app.logger.info('[Committed by user]: ' + str(current_user.username) + ' ' + str(deleted.username) + ' was deleted from application')
                flash('{} was deleted'.format(deleted.username))
                return redirect(url_for('manage_users'))
    else:
        flash('Sorry you are not admin!')
        return redirect(url_for('index'))
    return render_template('admin.html', title='Admin Console', form=form)

# Imports users into inventory system by using the ImportUserForm.
@app.route('/import_user', methods=['GET', 'POST'])
@login_required
def import_user():
    if current_user.is_authenticated:
        form = ImportUserForm()
        if form.validate_on_submit():
            users = Users(employee_id=form.employee_id.data, username=form.username.data,
                         first_name=form.first_name.data, last_name=form.last_name.data,
                         email=form.email.data, room_number=form.room_number.data)
            monitor1 = Monitors(monitor_serial_number=form.monitor_serial_number1.data,
                                monitor_asset_tag=form.monitor_asset_tag1.data,
                                monitor_id=users)
            monitor2 = Monitors(monitor_serial_number=form.monitor_serial_number2.data,
                                monitor_asset_tag=form.monitor_asset_tag2.data,
                                monitor_id=users)
            desktop = Desktop(desktop_name=form.desktop_name.data,
                                desktop_serial_number=form.desktop_serial_number.data,
                                desktop_asset_tag=form.desktop_asset_tag.data,
                                desktop_id=users)
            laptop = Laptop(laptop_name=form.laptop_name.data,
                                laptop_serial_number=form.laptop_serial_number.data,
                                laptop_asset_tag=form.laptop_asset_tag.data,
                                laptop_id=users)
            printer = Printer(printer_model=form.printer_model.data,
                              printer_serial_number=form.printer_serial_number.data,
                              printer_asset_tag=form.printer_asset_tag.data,
                              printer_id=users)
            scanner = Scanner(scanner_model=form.scanner_model.data,
                              scanner_serial_number=form.scanner_serial_number.data,
                              scanner_asset_tag=form.scanner_asset_tag.data,
                              scanner_id=users)
            db.session.add(users)
            db.session.add(monitor1)
            db.session.add(monitor2)
            db.session.add(desktop)
            db.session.add(laptop)
            db.session.add(printer)
            db.session.add(scanner)
            db.session.commit()
            app.logger.info('[Committed by user]: ' + str(current_user.username) + ' User created: ' + ' [Employee ID]: ' + str(users.employee_id) + ' ' +
                            '[Username]: ' + str(users.username) + ' ' +
                            '[First Name]: ' + str(users.first_name) + ' ' +
                            '[Last Name]: ' + str(users.last_name) + ' ' +
                            '[Email]: ' + str(users.email) + ' ' +
                            '[Room Number]: ' + str(users.room_number) + ' ' +
                            '[Monitor 1 Serial Number]: ' + str(monitor1.monitor_serial_number) + ' ' +
                            '[Monitor 1 Asset Tag]: ' + str(monitor1.monitor_asset_tag) + ' ' +
                            '[Monitor 2 Serial Number]: ' + str(monitor2.monitor_serial_number) + ' ' +
                            '[Monitor 2 Asset Tag]: ' + str(monitor2.monitor_asset_tag) + ' ' +
                            '[Desktop Name]: ' + str(desktop.desktop_name) + ' ' +
                            '[Desktop Serial Number]: ' + str(desktop.desktop_serial_number) + ' ' +
                            '[Desktop Asset Tag]: ' + str(desktop.desktop_asset_tag) + ' ' +
                            '[Laptop Name]: ' + str(laptop.laptop_name) + ' ' +
                            '[Laptop Serial Number]: ' + str(laptop.laptop_serial_number) + ' ' +
                            '[Laptop Asset Tag]: ' + str(laptop.laptop_asset_tag) + ' ' +
                            '[Printer Model]: ' + str(printer.printer_model) + ' ' +
                            '[Printer Serial Number]: ' + str(printer.printer_serial_number) + ' ' +
                            '[Printer Asset Tag]: ' + str(printer.printer_asset_tag) + ' ' +
                            '[Scanner Model]: ' + str(scanner.scanner_model) + ' ' +
                            '[Scanner Serial Number]: ' + str(scanner.scanner_serial_number) + ' ' +
                            '[Scanner Asset Tag]: ' + str(scanner.scanner_asset_tag))
            flash('User submitted!')
            return redirect(url_for('import_user'))
    return render_template('import_user.html', title='Import Users', form=form)

# Creates a query of users and each item that assigned to their name. More functionality will
# be added to the search function to query by username.
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_results():
    form = SearchUserForm()
    target = form.search.data
    search = db.session.query(Users.employee_id, Users.username, Users.first_name,
                                Users.last_name, Users.email, Users.room_number)\
                                .filter(or_(Users.username == target, Users.first_name == target,
                                        Users.last_name == target, Users.email == target,
                                        Users.room_number == target))

    if form.validate_on_submit() and search:
        table = Results(search, border=True)
        return render_template('search.html', table=table, title='Search', search=search,
                               form=form, target=target)
    else:
        page = request.args.get('page', 1, type=int)
        results = db.session.query(Users.employee_id, Users.username, Users.first_name,
                       Users.last_name, Users.email, Users.room_number).order_by(Users.first_name).paginate(page, app.config['RESULTS_PER_PAGE'], False)

        table = Results(results.items, border=True)
        next_url = url_for('search_results', page=results.next_num) if results.has_next else None
        prev_url = url_for('search_results', page=results.prev_num) if results.has_prev else None
        return render_template('search.html', table=table, title='Search', next_url=next_url, prev_url=prev_url, results=results, form=form)

# The item/<int:id> argument is necessary for the edit link in the Results table to link it back
# to the user in question. The parameters are in dictionary format.
@app.route('/item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
        form = EditImportForm()
        form.username.data = Users.query.filter_by(employee_id=id).first().username
        form.first_name.data = Users.query.filter_by(employee_id=id).first().first_name
        form.last_name.data = Users.query.filter_by(employee_id=id).first().last_name
        form.email.data = Users.query.filter_by(employee_id=id).first().email
        form.room_number.data = Users.query.filter_by(employee_id=id).first().room_number
        form.monitor_serial_number1.data = Monitors.query.filter_by(monitor_reference_id=id).all()[0].monitor_serial_number
        form.monitor_asset_tag1.data = Monitors.query.filter_by(monitor_reference_id=id).all()[0].monitor_asset_tag
        form.monitor_serial_number2.data = Monitors.query.filter_by(monitor_reference_id=id).all()[1].monitor_serial_number
        form.monitor_asset_tag2.data = Monitors.query.filter_by(monitor_reference_id=id).all()[1].monitor_asset_tag
        form.desktop_name.data = Desktop.query.filter_by(desktop_reference_id=id).first().desktop_name
        form.desktop_serial_number.data = Desktop.query.filter_by(desktop_reference_id=id).first().desktop_serial_number
        form.desktop_asset_tag.data = Desktop.query.filter_by(desktop_reference_id=id).first().desktop_asset_tag
        form.laptop_name.data = Laptop.query.filter_by(laptop_reference_id=id).first().laptop_name
        form.laptop_serial_number.data = Laptop.query.filter_by(laptop_reference_id=id).first().laptop_serial_number
        form.laptop_asset_tag.data = Laptop.query.filter_by(laptop_reference_id=id).first().laptop_asset_tag
        form.printer_model.data = Printer.query.filter_by(printer_reference_id=id).first().printer_model
        form.printer_serial_number.data = Printer.query.filter_by(printer_reference_id=id).first().printer_serial_number
        form.printer_asset_tag.data = Printer.query.filter_by(printer_reference_id=id).first().printer_asset_tag
        form.scanner_model.data = Scanner.query.filter_by(scanner_reference_id=id).first().scanner_model
        form.scanner_serial_number.data = Scanner.query.filter_by(scanner_reference_id=id).first().scanner_serial_number
        form.scanner_asset_tag.data = Scanner.query.filter_by(scanner_reference_id=id).first().scanner_asset_tag

        if form.validate_on_submit():
            form = EditImportForm()
            users = Users.query.filter_by(employee_id=id).first()
            monitor = Monitors.query.filter_by(monitor_reference_id=id).all()
            desktop = Desktop.query.filter_by(desktop_reference_id=id).first()
            laptop = Laptop.query.filter_by(laptop_reference_id=id).first()
            printer = Printer.query.filter_by(printer_reference_id=id).first()
            scanner = Scanner.query.filter_by(scanner_reference_id=id).first()
            users.username = form.username.data
            users.first_name = form.first_name.data
            users.last_name = form.last_name.data
            users.email = form.email.data
            users.room_number = form.room_number.data
            monitor[0].monitor_serial_number = form.monitor_serial_number1.data
            monitor[0].monitor_asset_tag = form.monitor_asset_tag1.data
            monitor[1].monitor_serial_number = form.monitor_serial_number2.data
            monitor[1].monitor_asset_tag = form.monitor_asset_tag2.data
            desktop.desktop_name = form.desktop_name.data
            desktop.desktop_serial_number = form.desktop_serial_number.data
            desktop.desktop_asset_tag = form.desktop_asset_tag.data
            laptop.laptop_name = form.laptop_name.data
            laptop.laptop_serial_number = form.laptop_serial_number.data
            laptop.laptop_asset_tag = form.laptop_asset_tag.data
            printer.printer_model = form.printer_model.data
            printer.printer_serial_number = form.printer_serial_number.data
            printer.printer_asset_tag = form.printer_asset_tag.data
            scanner.scanner_model = form.scanner_model.data
            scanner.scanner_serial_number = form.scanner_serial_number.data
            scanner.scanner_asset_tag = form.scanner_asset_tag.data
            db.session.commit()
            app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' + '[Employee ID]: ' +
                            '[Username]: ' + str(users.username) + ' ' +
                            '[First Name]: ' + str(users.first_name) + ' ' +
                            '[Last Name]: ' + str(users.last_name) + ' ' +
                            '[Email]: ' + str(users.email) + ' ' +
                            '[Room Number]: ' + str(users.room_number) + ' ' +
                            '[Monitor 1 Serial Number]: ' + str(monitor[0].monitor_serial_number) + ' ' +
                            '[Monitor 1 Asset Tag]: ' + str(monitor[0].monitor_asset_tag) + ' ' +
                            '[Monitor 2 Serial Number]: ' + str(monitor[1].monitor_serial_number) + ' ' +
                            '[Monitor 2 Asset Tag]: ' + str(monitor[1].monitor_asset_tag) + ' ' +
                            '[Desktop Name]: ' + str(desktop.desktop_name) + ' ' +
                            '[Desktop Serial Number]: ' + str(desktop.desktop_serial_number) + ' ' +
                            '[Desktop Asset Tag]: ' + str(desktop.desktop_asset_tag) + ' ' +
                            '[Laptop Name]: ' + str(laptop.laptop_name) + ' ' +
                            '[Laptop Serial Number]: ' + str(laptop.laptop_serial_number) + ' ' +
                            '[Laptop Asset Tag]: ' + str(laptop.laptop_asset_tag) + ' ' +
                            '[Printer Model]: ' + str(printer.printer_model) + ' ' +
                            '[Printer Serial Number]: ' + str(printer.printer_serial_number) + ' ' +
                            '[Printer Asset Tag]: ' + str(printer.printer_asset_tag) + ' ' +
                            '[Scanner Model]: ' + str(scanner.scanner_model) + ' ' +
                            '[Scanner Serial Number]: ' + str(scanner.scanner_serial_number) + ' ' +
                            '[Scanner Asset Tag]: ' + str(scanner.scanner_asset_tag))
            db.session.commit()
            flash('User updated!')
            return redirect(url_for('search_results'))
        return render_template('edit_import.html', title='Edit User', form=form)

# This allows anyone in the Admin class to delete users in the inventory system
@app.route('/delete_users/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_users(id):
    if isinstance(Admin.query.filter_by(user=current_user.username).first(), Admin):
        admin = Admin.query.filter_by(user=current_user.username).first()
        deleted = Users.query.filter_by(employee_id=id).first()
        admin.delete_users(deleted)
        app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' +
                        '[Username]: ' + str(deleted.username) + ' was deleted')
        db.session.commit()
        flash('Record Deleted!')
        return redirect(url_for('search_results'))
    else:
        flash('You are not an admin!')
        return redirect(url_for('search_results'))

# This function allows you to add an item to the inventory database
@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.is_authenticated:
        form = InventoryForm()
        if form.validate_on_submit():
            inventory = Other(other_item_name=form.other_item_name.data,
                              other_serial_number=form.other_serial_number.data,
                         other_asset_tag=form.other_asset_tag.data)
            db.session.add(inventory)
            db.session.commit()
            app.logger.info(
                '[Committed by user]: ' + str(current_user.username) + ' Changed to: ' + '[Item Name]: ' + str(
                    inventory.other_item_name) + ' ' +
                '[Item Serial Number]: ' + str(inventory.other_serial_number) + ' ' +
                '[Item Asset Tag]: ' + str(inventory.other_asset_tag))
            flash('{} added to inventory'.format(inventory.other_item_name))
            return redirect(url_for('add_item'))
    return render_template('add_item.html', title='Add Item', form=form)

# Allows you to search items in the database
@app.route('/search_inventory', methods=['GET', 'POST'])
@login_required
def search_inventory():
    page = request.args.get('page', 1, type=int)
    results = db.session.query(Other.others_id, Other.other_item_name, Other.other_serial_number,
                               Other.other_asset_tag)\
        .order_by(Other.other_item_name).paginate(page, app.config['RESULTS_PER_PAGE'], False)

    table = Inventory(results.items, border=True)
    next_url = url_for('search_inventory', page=results.next_num) if results.has_next else None
    prev_url = url_for('search_inventory', page=results.prev_num) if results.has_prev else None

    return render_template('search_inventory.html', table=table, title='Search Inventory',
                           next_url=next_url, prev_url=prev_url, results=results)


# Allows you to edit items in the inventory database. When you click on the Edit link,
# It renders an Edit Form to allow you to edit the specific item.
@app.route('/edit_inventory/<int:ids>', methods=['GET', 'POST'])
@login_required
def edit_inventory(ids):
    record = Other.query.filter_by(others_id=ids).first()
    if record:
        form = InventoryForm(formdata=request.form, obj=record)
        if form.validate_on_submit():
            inventory = Other.query.filter_by(others_id=ids).first()
            inventory.other_item_name = form.other_item_name.data
            inventory.other_serial_number = form.other_serial_number.data
            inventory.other_asset_tag = form.other_asset_tag.data
            db.session.commit()
            app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' + '[Item Name]: ' + str(inventory.other_item_name) + ' ' +
                            '[Item Serial Number]: ' + str(inventory.other_serial_number) + ' ' +
                            '[Item Asset Tag]: ' + str(inventory.other_asset_tag))
            flash('Inventory record updated!')
            return redirect(url_for('search_inventory'))
        return render_template('edit_inventory.html', title='Edit Item', form=form, record=record)

# Use this function to delete a specific item in your database.
@app.route('/delete_inventory/<int:ids>', methods=['GET', 'POST'])
@login_required
def delete_inventory(ids):
    if isinstance(Admin.query.filter_by(user=current_user.username).first(), Admin):
        admin = Admin.query.filter_by(user=current_user.username).first()
        deleted = Other.query.filter_by(others_id=ids).first()
        admin.delete_item(deleted)
        app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' +
                        '[Item]: ' + str(deleted.other_item_name) + ' was deleted')
        db.session.commit()
        flash('Record Deleted!')
        return redirect(url_for('search_inventory'))
    else:
        flash('You are not an admin!')
        return redirect(url_for('search_inventory'))

# Allows you to checkout items from your inventory to users
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.is_authenticated:
        form = CheckOutForm(request.form)
        form.select_field.choices = [(u.employee_id, u.last_name + ',' + u.first_name) for u in Users.query.order_by(Users.last_name).all()]
        target = request.form.get('select_field')
        target1 = form.checkout_asset_tag.data
        item = Other.query.filter_by(other_asset_tag=target1).first()
        timestamp = datetime.utcnow()
        if form.validate_on_submit():
            if isinstance(CheckOut.query.filter_by(checkout_asset_tag=target1).first(), CheckOut):
                flash('This item is already checked out')
                return redirect(url_for('checkout'))

            elif isinstance(Other.query.filter_by(other_asset_tag=target1).first(), Other):
                checked_out = CheckOut(checkout_timestamp=timestamp,
                                       checkout_username=Users.query.filter_by(employee_id=target).first().username,
                                       checkout_item_name=item.other_item_name,
                                       checkout_serial_number=item.other_serial_number,
                                       checkout_asset_tag=item.other_asset_tag)
                db.session.add(checked_out)
                db.session.commit()
                app.logger.info('[Committed by user]: ' + str(current_user.username) +
                ' [Item]: ' + str(checked_out.checkout_item_name) +
                ' was checked out to: ' + str(checked_out.checkout_username) +
                ' on: ' + str(checked_out.checkout_timestamp))
                flash('Check out successful!')
                return redirect(url_for('checkout'))
            else:
                flash('This item is not in the inventory system!')
                return redirect(url_for('checkout'))

    return render_template('checkout.html', title='Check Out', form=form, item=item)

# Search items that are checked out to users
@app.route('/search_checkout', methods=['GET', 'POST'])
@login_required
def search_checkout():
    page = request.args.get('page', 1, type=int)
    results = db.session.query(CheckOut.checkout_timestamp,
                               CheckOut.checkout_username,
                               CheckOut.checkout_item_name,
                               CheckOut.checkout_serial_number,
                               CheckOut.checkout_asset_tag)\
        .order_by(CheckOut.checkout_username).paginate(page, app.config['RESULTS_PER_PAGE'], False)
    table = Checkout(results.items, border=True)
    next_url = url_for('search_checkout', page=results.next_num) if results.has_next else None
    prev_url = url_for('search_checkout', page=results.prev_num) if results.has_prev else None

    return render_template('search_checkout.html', table=table, title='Search Checkout',
                           next_url=next_url, prev_url=prev_url, results=results)


# This function allows you to check in an item
@app.route('/checkout/<string:item>', methods=['GET', 'POST'])
@login_required
def delete_record(item):
    checkout_timestamp = datetime.utcnow()
    checkout_user = CheckOut.query.filter_by(checkout_asset_tag=item).first()
    app.logger.info('[Committed by user]: ' + str(current_user.username) +
                    ' was checked in for: ' + '[Username]: ' + checkout_user.checkout_username +
                    ' on: ' + str(checkout_timestamp))
    CheckOut.query.filter_by(checkout_asset_tag=item).delete()
    db.session.commit()
    flash('Check in successful!')
    return redirect(url_for('search_checkout'))

# Allows you to add a printer toner to the inventory system
@app.route('/add_toner', methods=['GET', 'POST'])
@login_required
def add_toner():
    if current_user.is_authenticated:
        form = TonerForm()
        if form.validate_on_submit():
            inventory = Toner(toner_model=form.toner_model.data,
                            toner_cartridge=form.toner_cartridge.data,
                            toner_color=form.toner_color.data,
                              toner_quantity=form.toner_quantity.data)
            db.session.add(inventory)
            db.session.commit()
            app.logger.info(
                '[Committed by user]: ' + str(current_user.username) + ' Changed to: ' + '[Toner Model]: ' + str(
                    inventory.toner_model) + ' ' +
                '[Toner Cartridge]: ' + str(inventory.toner_cartridge) + ' ' +
                '[Toner Color]: ' + str(inventory.toner_color) + ' ' +
                '[Toner Quantity]: ' + str(inventory.toner_quantity))
            flash('{} added to inventory'.format(inventory.toner_cartridge))
            return redirect(url_for('add_toner'))
    return render_template('toner.html', title='Import Toner', form=form)

# This allows you to search for a specific toner in the inventory system
@app.route('/search_toner', methods=['GET', 'POST'])
@login_required
def search_toner():
    page = request.args.get('page', 1, type=int)
    results = db.session.query(Toner.toner_id,
                               Toner.toner_model,
                               Toner.toner_cartridge,
                               Toner.toner_color,
                               Toner.toner_quantity)\
        .order_by(Toner.toner_model).paginate(page, app.config['RESULTS_PER_PAGE'], False)

    table = TonerInventory(results.items, border=True)
    next_url = url_for('search_toner', page=results.next_num) if results.has_next else None
    prev_url = url_for('search_toner', page=results.prev_num) if results.has_prev else None

    return render_template('search_toner.html', table=table, title='Search Toner',
                           next_url=next_url, prev_url=prev_url, results=results)

# Allows you to edit a toner item
@app.route('/edit_toner/<int:ids>', methods=['GET', 'POST'])
@login_required
def edit_toner(cartridge):
    record = Toner.query.filter_by(toner_id=ids).first()

    if record:
        form = TonerForm(formdata=request.form, obj=record)


        if form.validate_on_submit():
            toner = Toner.query.filter_by(toner_ids=ids).first()
            toner.toner_model = form.toner_model.data
            toner.toner_cartridge = form.toner_cartridge.data
            toner.toner_color = form.toner_color.data
            toner.toner_quantity = form.toner_quantity.data
            db.session.commit()
            app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' + '[Toner Model]: ' + str(toner.toner_model) + ' ' +
                            '[Toner Cartridge]: ' + str(toner.toner_cartridge) + ' ' +
                            '[Toner Color]: ' + str(toner.toner_color) + ' ' +
                            '[Toner Quantity]: ' + str(toner.toner_quantity))
            flash('Toner record updated!')
            return redirect(url_for('search_toner'))
        return render_template('edit_toner.html', title='Edit Toner', form=form, record=record)

# Delete a toner from the database
@app.route('/delete_toner/<int:ids>', methods=['GET', 'POST'])
@login_required
def delete_toner(ids):
    if isinstance(Admin.query.filter_by(user=current_user.username).first(), Admin):
        admin = Admin.query.filter_by(user=current_user.username).first()
        deleted = Toner.query.filter_by(toner_id=ids).first()
        admin.delete_toners(deleted)
        app.logger.info('[Committed by user]: ' + str(current_user.username) + ' Changed to: ' +
                        '[Toner Cartridge]: ' + str(deleted.toner_cartridge) + ' was deleted')
        db.session.commit()
        flash('Record Deleted!')
        return redirect(url_for('search_toner'))
    else:
        flash('You are not an admin!')
        return redirect(url_for('search_toner'))
