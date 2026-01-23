import random

from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    @staticmethod
    def to_json(self):
        print(f'self={self}')
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

def get_all():
    try:
        return db.session.query(Cafe).all()
    except Exception as e:
        print(f'Error retrieving all Cafe entries:  {e}')
        return None
    finally:
        db.session.close()

def get_all_id():
    try:
        # .all() returns a list of Row tuples, e.g., [(1,), (2,), (3,)]
        id_all = db.session.query(Cafe.id).all()
        id_list = [row[0] for row in id_all]
        return id_list
    except Exception as e:
        print(f'Error retrieving cafe {id}:  {e}')
        return None
    finally:
        db.session.close()

def get_by_id(cafe_id):
    try:
        return db.session.query(Cafe).get(cafe_id)
    except Exception as e:
        print(f'Error retrieving cafe {cafe_id}:  {e}')
        return None
    finally:
        db.session.close()

def get_by_location(location):
    try:
        return db.session.query(Cafe).filter(Cafe.location == location).all()
    except Exception as e:
        print(f'Error retrieving cafe {location}:  {e}')
        return None
    finally:
        db.session.close()

def create(cafe):
    try:
        cafe_entry = Cafe(**cafe)
        db.session.add(cafe_entry)
        db.session.commit()
        return True
    except Exception as e:
        print(f'Error saving cafe {cafe}:  {e}')
        return False
    finally:
        db.session.close()

def update_coffee_price(cafe_id, updated_coffee_price):
    try:
        # cafe = db.session.query(Cafe).get(cafe_id)
        cafe = db.session.get(Cafe, cafe_id)
        if cafe:
            cafe.coffee_price = updated_coffee_price
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f'Error updating cafe with id {cafe_id}:  {e}')
        return False
    finally:
        db.session.close()

@app.route("/")
def home():
    return render_template("index.html")

"""
sample response from 2026-01-19
{
    "cafe": {
        "can_take_calls": false,
        "coffee_price": "£3.00",
        "has_sockets": true,
        "has_toilet": true,
        "has_wifi": true,
        "id": 7,
        "img_url": "https://lh3.googleusercontent.com/p/AF1QipP_NbZH7A1fIQyp5pRm1jOGwzKsDWewaxka6vDt=s0",
        "location": "Shoreditch",
        "map_url": "https://g.page/acehotellondon?share",
        "name": "Ace Hotel Shoreditch",
        "seats": "50+"
    }
}
"""
@app.route("/cafe/random", methods=['GET'])
def cafe_random():
    id_list = get_all_id()
    # return jsonify({"id_list": id_list}), 200
    random_id = random.choice(id_list)
    cafe = get_by_id(random_id)
    # return Cafe.to_json(cafe)
    return jsonify({"cafe": Cafe.to_json(cafe)}), 200

@app.route("/cafe/all", methods=['GET'])
def cafe_all():
    cafe_all_db = get_all()
    cafe_all_json = []
    for cafe in cafe_all_db:
        cafe_all_json.append(Cafe.to_json(cafe))
    return jsonify({"cafe_all": cafe_all_json}), 200

@app.route("/cafe/search", methods=['GET'])
def cafe_search():
    cafe_all_json = []
    query_location = request.args.get("location")
    print(f'query_location={query_location}')
    cafe_list = get_by_location(query_location)
    if not cafe_list:
        return jsonify({"error": {"Not Found": "Sorry, we don't have a cafe at that location."}}), 200
    for cafe in cafe_list:
        cafe_all_json.append(Cafe.to_json(cafe))
    return jsonify({"cafe_all": cafe_all_json}), 200

"""
request
{
    "can_take_calls": true, 
    "coffee_price": "$1.80", 
    "has_sockets": true, 
    "has_toilet": true, 
    "has_wifi": true, 
    "location": "Shoreditch",
    "name": "My Cafe", 
    "seats": "30+", 
    "map_url": "https://g.page/acehotellondon?share", 
    "img_url": "https://lh3.googleusercontent.com/p/AF1QipP_NbZH7A1fIQyp5pRm1jOGwzKsDWewaxka6vDt=s0"
}
response
{
    "response": {
        "success": "Successfully added the new cafe."
    }
}
return HTTP_201 indicating that a new resource was created
"""
@app.route("/cafe/add", methods=['POST'])
def cafe_add():
    # silent=True prevents the app from crashing if the JSON is malformed
    new_data = request.get_json(silent=True)
    if not new_data:
        return jsonify(error={"Bad Request": "No JSON data provided or invalid JSON format."}), 400
    if create(new_data):
        return jsonify({"response": {"success": "Successfully added the new cafe."}}), 201
    else:
        return jsonify({"response": {"error": "Could not create new cafe."}}), 500

@app.route("/cafe/update-coffee-price/<int:cafe_id>", methods=['PATCH'])
def cafe_update_coffe_price(cafe_id):
    new_price = request.args.get("new_price")
    if update_coffee_price(cafe_id, new_price):
        return jsonify({"success": "price updated."}), 200
    else:
        return jsonify({"error": {"message": f"cafe with id {cafe_id} not found."}}), 404

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record

if __name__ == '__main__':
    app.run(debug=True)
