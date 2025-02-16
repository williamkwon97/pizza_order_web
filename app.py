from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pizza_user:asdf@localhost/pizza_order_db'
app.config['SECRET_KEY'] = 'asodkglasdjga12r1!$##j'
db = SQLAlchemy(app)

# Models
class Topping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    toppings = db.relationship('Topping', secondary='pizza_topping', backref='pizzas')

pizza_topping = db.Table('pizza_topping',
    db.Column('pizza_id', db.Integer, db.ForeignKey('pizza.id'), primary_key=True),
    db.Column('topping_id', db.Integer, db.ForeignKey('topping.id'), primary_key=True)
)

# Forms
class ToppingForm(FlaskForm):
    name = StringField('Topping Name', validators=[DataRequired()])
    submit = SubmitField('Add Topping')

class PizzaForm(FlaskForm):
    name = StringField('Pizza Name', validators=[DataRequired()])
    toppings = SelectMultipleField('Toppings', coerce=int)
    submit = SubmitField('Create Pizza')

# Routes
@app.route('/')
def index():
    pizzas = Pizza.query.all()
    return render_template('index.html', pizzas=pizzas)

@app.route('/toppings', methods=['GET', 'POST'])
def manage_toppings():
    form = ToppingForm()
    if form.validate_on_submit():
        if Topping.query.filter_by(name=form.name.data).first():
            flash('Topping already exists!', 'danger')
        else:
            new_topping = Topping(name=form.name.data)
            db.session.add(new_topping)
            db.session.commit()
            flash('Topping added successfully!', 'success')
        return redirect(url_for('manage_toppings'))
    toppings = Topping.query.all()
    return render_template('toppings.html', form=form, toppings=toppings)

@app.route('/pizzas', methods=['GET', 'POST'])
def manage_pizzas():
    form = PizzaForm()
    form.toppings.choices = [(t.id, t.name) for t in Topping.query.all()]
    if form.validate_on_submit():
        if Pizza.query.filter_by(name=form.name.data).first():
            flash('Pizza already exists!', 'danger')
        else:
            new_pizza = Pizza(name=form.name.data)
            new_pizza.toppings = Topping.query.filter(Topping.id.in_(form.toppings.data)).all()
            db.session.add(new_pizza)
            db.session.commit()
            flash('Pizza added successfully!', 'success')
        return redirect(url_for('manage_pizzas'))
    pizzas = Pizza.query.all()
    return render_template('pizzas.html', form=form, pizzas=pizzas)

@app.route('/delete_pizza/<int:pizza_id>', methods=['POST'])
def delete_pizza(pizza_id):
    pizza = Pizza.query.get_or_404(pizza_id)
    db.session.delete(pizza)
    db.session.commit()
    flash('Pizza deleted successfully!', 'success')
    return redirect(url_for('manage_pizzas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
