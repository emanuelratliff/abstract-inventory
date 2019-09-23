# Abstract Inventory

Abstract Inventory is a concept that was inspired by 
Miguel Grinberg's Flask App tutorial: 
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

I decided to create my own rendition of the project by
adding an administrator console, removing the blogs/posts, and create a template for an IT infrastructure to 
use a database system for tracking inventory.

I wanted to make something that could be easily
customizable to fit an IT infrastructure's needs.

## Installation

To use this inventory system, I would first use a
terminal emulator to install the necessary packages
to get it up and running:

Use the package manager called [pip](https://pip.pypa.io/en/stable/)
to install the necessary modules from the requirements.txt file

Activate your virtual environment and then run the following command:

```bash
pip install -r requirements.txt
```

I did not include the migrations folder because that needs to be initialized based on your system's configuration. 
Before running the application, please make sure that Flask-Migrate was successfully installed. Open a terminal,
and issue the following commands in the root of the project directory:

```bash
flask db init
flask db migrate
flask db upgrade
```

Once completed, navigate to the terminal and open the flask shell:

```bash
flask shell
```

Create all databases by issuing the following command:

```bash
db.create_all()
```

To run this application, navigate to root of the project directory, and use the terminal to issue the following commands:

```bash
export FLASK_APP=inventory.py
flask run
```

Initially you will be able to register into the Inventory System but you will not be able to add yourself as an admin.
However, you can add yourself as an admin via the terminal using flask shell. This will not work if no one has registered in the system:

```bash
flask shell
admin = Admin(str(User.query.filter_by(User.username == '<insert your user name here>').username), admin_username=User.query.filter_by(User.username == '<insert your username here>'))
db.session.add(admin)
db.session.commit()
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
