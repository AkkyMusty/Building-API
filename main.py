import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

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

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
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

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():

    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafe = result.scalars().all()
    random_cafe = random.choice(all_cafe)
    return jsonify(cafe=random_cafe.to_dict())

    # return jsonify(cafe={"id": random_cafe.id,
    #                      "name": random_cafe.name,
    #                      "map_url": random_cafe.map_url,
    #                      "img_url": random_cafe.img_url,
    #                      "location": random_cafe.location,
    #                      "amenities": {
    #                          "seats": random_cafe.seats,
    #                          "has_toilet": random_cafe.has_toilet,
    #                          "has_wifi": random_cafe.has_wifi,
    #                          "has_sockets": random_cafe.has_sockets,
    #                          "can_take_calls": random_cafe.can_take_calls,
    #                          "coffee_price": random_cafe.coffee_price }
    #                      })

@app.route("/all")
def all():
    all_cafe = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafe ])

@app.route("/search")
def search():
    loc = request.args.get('loc')
    cafe_loc = db.session.execute(db.select(Cafe).where(Cafe.location==loc)).scalars().all()
    if cafe_loc:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafe_loc])
    else:
        return jsonify(error={"NotFound": "We don't have a cafe at that location"}), 404
# HTTP POST - Create
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
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

    return jsonify(response={"success": "successfully added new cafes"})

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def patch(cafe_id):
    cafe_patch = db.get_or_404(Cafe, cafe_id)
    if cafe_patch:
        new_price = request.args.get("new_price")
        cafe_patch.coffee_price = new_price
        db.session.commit()
        return jsonify({"success": "Successfully updated the price"})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id is not found"}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    key = request.args.get("api-key")
    if key == "TopSecretAPIKey":
        cafe_delete = db.get_or_404(Cafe, cafe_id)
        if cafe_delete:
            db.session.delete(cafe_delete)
            db.session.commit()
            return jsonify({"success": "Cafe is deleted"})
        else:
            return jsonify(error={"Not Found": "Sorry. A cafe with that ID is not found in the database"})
    else:
        return jsonify({"error": "Sorry That's not allowed. Make sure you have the correct API"})



if __name__ == '__main__':
    app.run(debug=True)
