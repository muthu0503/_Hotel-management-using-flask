from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
#from flask import session, redirect, url_for

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel.db'  # SQLite database (use another URI for other DBs)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Room model
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Room {self.room_type} - {self.price}>'

# Define the Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    check_in = db.Column(db.String(50), nullable=False)
    check_out = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pending")

    room = db.relationship('Room', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.guest_name} - {self.room.room_type}>'



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


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin_dash')
def admin_dashboard():
    rooms = Room.query.all()
    bookings = Booking.query.all()
    return render_template('admin_dashboard.html', rooms=rooms, bookings=bookings)

# Add Room Route (Admin)
@app.route('/admin/add-room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':

        photo = request.form['photo']
        price = float(request.form['price'])
        room_type = request.form['room_type']
        id = request.form['id']

        new_room = Room(id=id, photo=photo, price=price, room_type=room_type)
        db.session.add(new_room)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_room.html')

# Delete Room Route (Admin)
@app.route('/admin/delete-room/<int:room_id>', methods=['GET', 'POST'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Confirm Booking (Admin)
@app.route('/admin/confirm-booking/<int:booking_id>', methods=['GET', 'POST'])
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'Confirmed'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Cancel Booking (Admin)
@app.route('/admin/cancel-booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'Cancelled'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Guest Registration (Booking Room)
@app.route('/guest/registration', methods=['GET', 'POST'])
def guest_registration():
    if request.method == 'POST':
        guest_name = request.form.get('guest_name')
        guest_email = request.form.get('guest_email')
        guest_phone = request.form.get('guest_phone')
        room_id = request.form.get('room_id')  # This is the room selected by the user
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')

        # Fetch the room from the database to get the correct price
        room = Room.query.get(room_id)

        if not room:
            return "Selected room not found", 404

        price = room.price  # Get the price from the selected room

        # Create the new booking
        new_booking = Booking(
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            room_id=room_id,
            price=price,  # Use the price of the selected room
            check_in=check_in,
            check_out=check_out
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('guest_dashboard'))

    rooms = Room.query.all()  # Fetch all rooms to display in the form
    return render_template('guest_registration.html', rooms=rooms)

# Guest Dashboard Route
@app.route('/guest')
def guest_dashboard():
    bookings = Booking.query.all()
    return render_template('guest_dashboard.html', bookings=bookings)



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/room")
def room():
    return render_template("room.html")


@app.route("/service")
def service():
    return render_template("services.html")

@app.route("/dining")
def dining():
    return render_template("dining.html")


@app.route("/events")
def events():
    return render_template("events.html")


# Delete Booking Route (Admin)
@app.route('/admin/delete-booking/<int:booking_id>', methods=['GET', 'POST'])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))



@app.route('/logout')
def logout():
    # Here, you can clear the session or any other authentication details.
    session.clear()  # Clear the session (if you're using session-based login)

    # Redirect to the home page
    return redirect(url_for('index'))


# Run the Flask App
if __name__ == '__main__':

    with app.app_context():
       db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
