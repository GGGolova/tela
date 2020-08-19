from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify,
                   session,
                   make_response)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)
import httplib2
import requests
import json

app = Flask(__name__)

app_db_path = 'sqlite:////vagrant/catalog/app.db'
client_secret_path = '/vagrant/catalog/client_secret.json'

engine = create_engine(app_db_path, connect_args={'check_same_thread': False})

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

CLIENT_ID = json.loads(
    open(client_secret_path, 'r').read())['web']['client_id']

cat_All = "All"


@app.route("/")
@app.route("/<category_name>/<int:category_id>")
@app.route("/<category_name>/<int:category_id>/<int:item_id>")
def base(category_name=cat_All,
         category_id="0",
         item_id="0",
         name="Item name",
         description="Select item to display description."):
    '''
    Method: Displays Web Application.

    Keyword arguments:
        <category_name> (string): provides string version of category
        <int:category_id> (integer) : provides numeric version of category
        <int:item_id> (integer) : provides numeric version of item
    '''
    categories = db_session.query(Category).order_by(asc(Category.name))
    all_items_badge = db_session.query(Item).order_by(asc(Item.name)).count()
    if category_name == cat_All:
        items = db_session.query(Item).order_by(asc(Item.name))
    else:
        category = db_session.query(Category).filter_by(
                   name=category_name).one_or_none()
        if category:
            items = db_session.query(Item).filter_by(
                    category_id=category.id).all()
    if item_id != "0":
        item = db_session.query(Item).filter_by(id=item_id).one_or_none()
        if item:
            name = item.name
            description = item.description
    return render_template('webApp.html',
                           CLIENT_ID=CLIENT_ID,
                           categories=categories,
                           items=items,
                           category_name=category_name,
                           name=name,
                           description=description,
                           all_items_badge=all_items_badge)


@app.route("/<category_name>/item/new", methods=['POST'])
def add_new_item(category_name):
    '''
    Method: Creates New Item.

    Keyword arguments:
        <category_name> (string): provides displayed category name
        newItemName (string): provides new item name
        newItemCategory (string): provides new item category
        newItemDescription (string): provides new item description
    '''
    if session['logged_in']:
        name = request.form['newItemName']
        category = db_session.query(Category).filter_by(name=request.form[
            'newItemCategory']).one_or_none()
        if category:
            category.inventory += 1
            description = request.form['newItemDescription']
            new_item = Item(name=name,
                            category_id=category.id,
                            description=description,
                            user_id=session.get('user_id'))
            db_session.add(new_item)
            db_session.commit()
            flash("Item has been added.")
            return redirect(url_for('base',
                                    category_name=category_name,
                                    category_id=category.id))
        else:
            flash("New Item category not found.")
            return redirect(url_for('base'))
    else:
        flash("You're not logged in.")
        return redirect(url_for('base'))


@app.route("/<category_name>/item/edit/<int:item_id>", methods=['POST'])
def edit_item(category_name, item_id):
    '''
    Method: Updates selected item.

    Keyword arguments:
        <category_name> (string): provides displayed category name
        <int:item_id> (integer): provedes updated item id
        editItemName (string): provides items' new name
        editItemCategory (string): provides items new category
        editItemDescription (string): provides items' new description
    '''
    if session['logged_in']:
        category = db_session.query(Category).filter_by(
                   name=request.form['editItemCategory']).one_or_none()
        item = db_session.query(Item).filter_by(id=item_id).one_or_none()
        if category and item:
            category_id = item.category_id
            category_old = db_session.query(Category).filter_by(
                           id=category_id).one_or_none()
            category.inventory += 1
            category_old.inventory -= 1
            item.name = request.form['editItemName']
            item.category_id = category.id
            item.description = request.form['editItemDescription']
            db_session.commit()
            flash("Item has been edited.")
            return redirect(url_for('base',
                                    category_name=category_name,
                                    category_id=category_id))
        else:
            flash("System error.")
            return redirect(url_for('base'))
    else:
        flash("You're not logged in.")
        return redirect(url_for('base'))


@app.route("/<category_name>/item/delete/<int:item_id>", methods=['POST'])
def delete_item(category_name, item_id):
    '''
    Method: Deletes selected item.

    Keyword arguments:
        <category_name> (string): provides displayed category name
        <int:item_id> (integer): provedes seleted item id
    '''
    if session['logged_in']:
        delete_item = db_session.query(Item).filter_by(
                      id=item_id).one_or_none()
        category_id = delete_item.category_id
        category = db_session.query(Category).filter_by(
                   id=category_id).one_or_none()
        if delete_item and category:
            category.inventory -= 1
            db_session.delete(delete_item)
            db_session.commit()
            flash("Item has been deleted.")
            return redirect(url_for('base',
                                    category_name=category_name,
                                    category_id=category_id))
        else:
            flash("System error.")
            return redirect(url_for('base'))
    else:
        flash("You're not logged in.")
        return redirect(url_for('base'))


@app.route('/Category/JSON')
def category_JSON():
    '''Method: Displays all categories in JSON format.'''
    categories = db_session.query(Category).order_by(asc(Category.name))
    return jsonify(All_Categories=[c.serialize for c in categories])


@app.route('/Item/JSON')
def item_JSON():
    '''Method: Displays all items in JSON format.'''
    items = db_session.query(Item).order_by(asc(Item.name))
    return jsonify(All_Items=[i.serialize for i in items])


@app.route('/item/<int:item_id>/JSON')
def item_id_JSON(item_id):
    '''
    Method: Displays arbitrary item in JSON format.

    Keyword arguments:
        <int:item_id> (integer): provedes requested item id
    '''
    item = db_session.query(Item).filter_by(id=item_id).one_or_none()
    category = db_session.query(Category).filter_by(
                id=item.category_id).one_or_none()
    if item:
        if category:
            return jsonify(category=category.name, item=[item.serialize])
        else:
            return jsonify(category="none", item=[item.serialize])
    else:
        return jsonify('item does not exist.')


@app.route("/logout", methods=['POST'])
def logout():
    if session['logged_in']:
        '''Method: Logs user out and clears' session data.'''
        session.pop('logged_in', None)
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('email', None)
        session.pop('picture', None)
        flash("You have successfully logged out.")
        return "app.wsgi logout"
    else:
        flash("You're not logged in.")
        return redirect(url_for('base'))


@app.route('/oauth/<provider>', methods=['POST'])
def login(provider):
    if provider == 'google':
        '''
        Method: Google login procedure via AJAX.

        Request comes from AJAX with one time authorization code via
        request.get_json(). Credentials than retrived with step2_exchenge which
        allows to retrieve user data.

        Keyword arguments:
            one time authorization code (json): user/google authorization
                to access user data and login to application
        '''
        oneTime_auth_code = request.get_json()
        try:
            oauth_flow = flow_from_clientsecrets(client_secret_path, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(oneTime_auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps(
                'Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)
        data = answer.json()
        name = data['name']
        picture = data['picture']
        email = data['email']
        user = db_session.query(User).filter_by(email=email).first()
        if not user:
            user = User(name=name, picture=picture, email=email)
            db_session.add(user)
            db_session.commit()
        session['logged_in'] = True
        session['user_id'] = user.id
        session['username'] = user.name
        session['email'] = user.email
        session['picture'] = user.picture
        flash("You have successfully logged in.")
        return session['username']
    else:
        return 'Unrecognized Provider'


if __name__ == '__main__':
    '''
    Method: Initiates python web server application accessible on
            localhost:8080.
    '''
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
