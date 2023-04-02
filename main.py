from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    def __init__(self, id, name, map_url, img_url, location, seats, has_toilet, has_wifi, has_sockets, can_take_calls, coffee_price):
        self.id=id
        self.name=name
        self.map_url=map_url
        self.img_url=img_url
        self.location=location
        self.seats=seats
        self.has_toilet=has_toilet
        self.has_wifi=has_wifi
        self.has_sockets=has_sockets
        self.can_take_calls=can_take_calls
        self.coffee_price=coffee_price

    def get_random_cafe(self):
        all_cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(all_cafes)
        return random_cafe
    def to_dict(self):
        dictionary = {}

        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)

        return dictionary

@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())
@app.route("/all", methods=["GET"])
def get_all_cafe():
    cafes=db.session.query(Cafe).all()
    cafe_list=[]
    for cafe in cafes:
        new_cafe=cafe.to_dict()
        cafe_list.append(new_cafe)
    return jsonify(cafe=cafe_list)
@app.route("/search", methods=["GET"])
def search_a_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})

## HTTP POST - Create Record
@app.route("/add", methods=["POST"])

def post_new_cafe():
    new_cafe = Cafe(
        id=request.form.get("id"),
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_cafe_price(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        cafe.coffee_price=request.form.get("new_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully update the price."})
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that id."})
## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE", "GET"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if api_key=="TopSecretAPIKey":
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully delete the cafe."}),200
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that id."}),404
    else:
        return jsonify(error={"Error": "Sorry, that's not allowed, make sure you have the correct api-key."}),403


if __name__ == '__main__':
    app.run(debug=True)
