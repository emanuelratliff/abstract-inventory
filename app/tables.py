from flask_table import Table, Col, LinkCol, DatetimeCol, ButtonCol

# flask_table that corresponds to the Users class and is joined by the following classes
# in model.py: Monitors, Desktop, Laptop, Printer, Scanner.

# The Edit attribute in the Results class allows a user to edit the respective table.
# It uses a url arguments in a dictionary type to match employee ids.
class Results(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed', 'table-hover']
    id = Col('Id', show=False)
    employee_id = Col('Employee Code')
    username = Col('Username')
    first_name = Col('First Name')
    last_name = Col('Last Name')
    email = Col('Email')
    room_number = Col('Room Number')
    edit = LinkCol('View/Edit', 'edit', url_kwargs=dict(id='employee_id'))
    delete = ButtonCol('Delete', 'delete_users', url_kwargs=dict(id='employee_id'))

class Inventory(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed', 'table-hover']
    id = Col('Id', show=False)
    other_item_name = Col('Item Name')
    other_serial_number = Col('Item Serial Number')
    other_asset_tag = Col('Item Asset Tag')
    edit = LinkCol('Edit', 'edit_inventory', url_kwargs=dict(other_item_name='other_item_name'))
    delete = ButtonCol('Delete', 'delete_inventory', url_kwargs=dict(other_item_name='other_item_name'))

class Checkout(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed', 'table-hover']
    id = Col('Id', show=False)
    checkout_timestamp = DatetimeCol('Checkout Time',  datetime_format="YYYY-MM-dd")
    checkout_username = Col('Username')
    checkout_item_name = Col('Item')
    checkout_serial_number = Col('Serial Number')
    checkout_asset_tag = Col('Asset Tag')
    check_in = ButtonCol('Check in', 'delete_record', url_kwargs=dict(item='checkout_asset_tag'))

class TonerInventory(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed', 'table-hover']
    id = Col('Id', show=False)
    toner_model = Col('Printer Model')
    toner_cartridge = Col('Cartridge Type')
    toner_color = Col('Color')
    toner_quantity = Col('Quantity')
    edit = LinkCol('Edit', 'edit_toner', url_kwargs=dict(cartridge='toner_cartridge'))
    delete = ButtonCol('Delete', 'delete_toner', url_kwargs=dict(cartridge='toner_cartridge'))
   
