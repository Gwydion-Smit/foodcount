from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import requests

from .db import get_db
from .auth import login_required

BONAPI_API_KEY = "bdec218560cbe2ab59aa2737f090cbc11280bb62"

bp = Blueprint('carboncalc', __name__, url_prefix='/carboncalc')

@bp.route("/leaderboard")
@login_required
def leaderboard():
    db = get_db()
    standings = db.execute('SELECT name, carboncost, carbonsaved FROM USERS WHERE carboncost > 0 ORDER BY carboncost ASC LIMIT 10;').fetchall()
    requests.post("https://test.eaternity.ch/api/", headers = {"authorization": "Basic aDRjSzR0SDBOT2c3NUhqZkszMzlLbE9scGEzOWZKenhYdw==", "Content-Type":"application/json"})
    return render_template("carboncalc/leaderboard.html", standings=standings)

def fetch_list():
    db = get_db()
    values = db.execute(f"SELECT * FROM INGREDIENTS WHERE userid = {session.get('user_id')}").fetchall()
    return values

co2 = {
    "Butter": 12.1,
    "Margarine": 3.3,
    "Lamb": 39.2,
    "Beef": 27,
    "Cheddar Cheese": 13.5,
    "Pork": 12.1,
    "Turkey": 10.9,
    "Chicken": 6.9,
    "Lentils": 0.9,
    "White Rice": 2.7,
    "Brown Rice": 2.16
}

alternatives = {
    "Butter": "Margarine",

}

def get_avg_carbon():
    db = get_db()
    values = db.execute(f"SELECT * FROM INGREDIENTS WHERE userid = {session.get('user_id')}").fetchall()
    
    cost = 0
    quantity = 0
    for ingredient in values:
        cost += ingredient["carboncost"]
        quantity += ingredient["quantity"]
    if quantity > 0:
        avgcost = cost / quantity
    else:
        avgcost = 0
    
    return avgcost

def add_food():
    food_type = request.form['food_type']
    food_name = request.form['food_name']
    quantity = request.form['quantity']

    if food_name in co2:
        food_co2 = co2[food_name] * int(quantity)
    else:
        error = "Ingredient not implemented"
        print(error)
    user_id = session.get('user_id')

    if error == "":
        db = get_db()
    
        db.execute(
            'INSERT INTO INGREDIENTS (foodtype, foodname, quantity, carboncost, userid) VALUES (?, ?, ?, ?, ?)',
            (food_type, food_name, quantity, food_co2,  user_id)
        )

        db.execute(f'UPDATE USERS SET carboncost = {get_avg_carbon()} WHERE id = {user_id}')
        db.commit()
    return error

def use_alternative():
    db = get_db()
    user_id = session.get('user_id')

    # get selected ingredient
    
    # doesn't work with multiple items of same type!
    original_ingredient = request.form['food_name']

    original = db.execute(f"SELECT * FROM INGREDIENTS WHERE userid = {user_id} AND foodname = {original_ingredient}").fetchall()
    alternative = alternatives[original_ingredient]
    alternative_co2 = co2[alternative] * int(original["quantity"])

    

    # doesn't work with alternative being different type
    # alternative must have carbon implemented!
    db.execute(f'UPDATE INGREDIENTS SET foodname = {alternative}, carboncost = {alternative_co2} WHERE id = {user_id}')
    originalcarbon = db.execute(f"SELECT carboncost FROM USERS WHERE userid = {user_id}").fetchall()
    db.execute(f'UPDATE USERS SET carbonsaved = {original["carboncost"] - alternative_co2}, carboncost = {originalcarbon - original["carboncost"] + alternative_co2} WHERE id = {user_id}')

    db.commit()    

    # update ingredient db
    # update user db

@bp.route("/list", methods=('GET', 'POST'))
@login_required
def list():
    error = ""
    if request.method == 'POST':
        if 'food_type' in request.form:
            error = add_food()

        else:
            use_alternative()
        
        
    return render_template("carboncalc/list.html", title = "Shopping List", ingredients=fetch_list(), error=error)

@bp.route('/home')
@login_required
def home():
    return render_template('carboncalc/homepage.html', title = "Home")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM USERS WHERE id = ?', (user_id,)
        ).fetchone()