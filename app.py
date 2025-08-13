from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(100), nullable=False, unique=True)
    room_type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), default='available')  # available, booked, etc.

    def __repr__(self):
        return f'<Room {self.room_number}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(100), default='pending')  # pending, confirmed, cancelled

    room = db.relationship('Room', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.customer_name} - {self.room_id}>'

# Create all database tables
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    # Hotel information
    hotel_info = {
        'name': 'Sunrise Hotel',
        'address': '123 Beach Road, Paradise City',
        'location': 'Paradise City, Ocean View',
        'email': 'contact@sunrisehotel.com',
        'phone': '+1234567890',
        'social_media': {
            'facebook': 'https://www.facebook.com/sunrisehotel',
            'twitter': 'https://twitter.com/sunrisehotel',
            'instagram': 'https://www.instagram.com/sunrisehotel'
        }
    }
    return render_template('index.html', hotel_info=hotel_info)


@app.route("/service")
def service():
    return render_template("services.html")

@app.route("/dining")
def dining():
    return render_template("dining.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/room")
def room():
    return render_template("room.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

# Admin Routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    rooms = Room.query.all()
    bookings = Booking.query.all()
    return render_template('admin_dashboard.html', rooms=rooms, bookings=bookings)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/room_details")
def room_details():
    return render_template("room_details.html")



@app.route('/admin/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']
        room = Room(room_number=room_number, room_type=room_type, price=price)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_room.html')

@app.route('/admin/delete_room/<int:room_id>', methods=['GET'])
def delete_room(room_id):
    room = Room.query.get(room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Customer Routes
@app.route('/customer', methods=['GET'])
def customer_view_rooms():
    rooms = Room.query.filter_by(status='available').all()
    return render_template('customer_rooms.html', rooms=rooms)

@app.route('/book_room/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    room = Room.query.get(room_id)
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        booking = Booking(
            customer_name=customer_name,
            room_id=room.id,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )
        room.status = 'booked'  # Update room status
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('payment', booking_id=booking.id))
    return render_template('book_room.html', room=room)

@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get(booking_id)
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        booking.payment_status = 'paid'
        db.session.commit()
        return redirect(url_for('customer_dashboard', booking_id=booking.id))
    return render_template('payment.html', booking=booking)

@app.route('/customer/dashboard')
def customer_dashboard():
    bookings = Booking.query.all()
    return render_template('customer_dashboard.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
