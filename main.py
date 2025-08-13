from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hoteldb1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the Room model
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    min_guests = db.Column(db.Integer, nullable=False)
    max_adults = db.Column(db.Integer, nullable=False)
    max_children = db.Column(db.Integer, nullable=False)
    total_of_this_type = db.Column(db.Integer, nullable=False)
    room_description = db.Column(db.Text, nullable=False)
    room_image = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Room {self.name}>'
# Define the Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)  # Add email column
    phone = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, cancelled



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


# Route to display room details
@app.route('/room_details')
def room_details():
    rooms = Room.query.filter_by(status='available').all()
    return render_template('room_details.html', rooms=rooms)



@app.route("/booking")
def booking():
    return render_template("booking.html")



@app.route("/create_rooms")
def create_rooms():
    return render_template("create_rooms.html")



# Route to process the booking form submission
@app.route('/process-booking/<int:room_id>', methods=['POST'])
def process_booking(room_id):
    room = Room.query.get_or_404(room_id)

    if room.status == 'booked':
        return redirect(url_for('room_details'))  # Room is already booked, redirect back to room details

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        email = request.form['email']
        phone = request.form['phone']
        room_type = room.room_type
        checkin_date_str = request.form['checkin_date']
        checkout_date_str = request.form['checkout_date']
        payment_method = request.form['payment_method']

        # Convert string to date object
        checkin_date = datetime.strptime(checkin_date_str, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout_date_str, '%Y-%m-%d').date()

        # Save the booking to the database
        booking = Booking(customer_name=customer_name, email=email, phone=phone, room_type=room_type,
                          checkin_date=checkin_date, checkout_date=checkout_date, payment_method=payment_method)
        db.session.add(booking)

        # Update the room status to booked
        room.status = 'booked'
        db.session.commit()

        # Redirect to payment confirmation page (you can modify this)
        return redirect(url_for('payment', booking_id=booking.id))

    return render_template('booking.html', room=room)


# Route to handle the payment
@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if request.method == 'POST':
        # Simulate payment and change booking status
        booking.status = 'confirmed'  # Update status to confirmed after successful payment
        db.session.commit()
        return redirect(url_for('booking_confirmation', booking_id=booking.id))

    return render_template('payment.html', booking=booking)


# Route to display booking confirmation
@app.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking_confirmation.html', booking=booking)


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

@app.route('/admin/view_booking/<int:booking_id>', methods=['GET'])
def view_booking(booking_id):
    booking = Booking.query.get(booking_id)
    return render_template('view_booking.html', booking=booking)

@app.route('/admin/update_booking_status/<int:booking_id>', methods=['GET', 'POST'])
def update_booking_status(booking_id):
    booking = Booking.query.get(booking_id)
    if request.method == 'POST':
        status = request.form['status']
        booking.status = status
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('update_booking_status.html', booking=booking)

# Create all database tables



# Create all database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
