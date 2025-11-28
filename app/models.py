from app import db
from flask_login import UserMixin


# convention class naming is uppercase. However, sqlite stores table name in lowercase
# in this case, table name is flight.
class Flight(db.Model):
    # Note: When primary_key=True and the type is Integer, SQLAlchemy + the database automatically treat it as auto-increment. We don't need to pass in any num.
    num = db.Column("num",db.Integer, primary_key=True)
    cityFrom = db.Column("cityFrom",db.String(10), nullable=False)
    cityTo = db.Column("cityTo",db.String(10), nullable=False)
    departDate=db.Column("departDate",db.String(10), nullable=False)
    arrivalDate=db.Column("arrivalDate",db.String(10), nullable=False)
    departTime = db.Column("departTime",db.String(10), nullable=False)
    arrivalTime= db.Column("arrivalTime",db.String(10), nullable=False)
    # db.Interval is good for storing difference between dates or time. DateTime() is better for specific dates.
    duration= db.Column("duration",db.Interval, nullable=False)
    fclass = db.Column("fclass",db.String(10), nullable=False)
    price= db.Column("price",db.Integer, nullable=False)

# note: many to many relationships require an association table. Each pssenger can have multiple bookings and each booking can have multiple passengers.
booking_passenger=db.Table('booking_passenger',
    db.Column('booking_id',db.Integer,db.ForeignKey('booking.id')),
    db.Column('passenger_id',db.Integer,db.ForeignKey('passenger.id'))
)

class Passenger(db.Model):
    id=db.Column('id',db.Integer,primary_key=True)
    title = db.Column("title",db.String(5),nullable=False)
    fname = db.Column("fname",db.String(10),nullable=False)
    lname = db.Column("lname",db.String(10),nullable=False)
    nationality=db.Column("nationality",db.String(10),nullable=False)
    gender=db.Column("gender",db.String(10),nullable=False)

    # due to backref, both passenger.bookings and booking.passengers have been created.
    # association table is used for many to many relationship
    # because of backref, we can access xbooking.passengers and get a list of all the passengers on xbooking.
    booking = db.relationship('Booking',secondary=booking_passenger,backref='passengers')
    
class Booking(db.Model):
    # booking id
    id=db.Column('id',db.Integer,primary_key=True)

    # store passenger and flight
    # not needed anymore because we have backref on passenger table
    # passenger_id=db.Column(db.Integer,db.ForeignKey('passenger.id'), nullable=False)

    depart_flight_num=db.Column(db.Integer,db.ForeignKey('flight.num'),nullable=False)
    # using 2 foreign key to same key will cause an error here, 
    # we need to specify
    return_flight_num=db.Column(db.Integer,db.ForeignKey('flight.num'),nullable=True) # nullable True because it can be None when there's no return flight

    # store booking preferences
    meal=db.Column('meal',db.String(10),nullable=False)
    seat=db.Column('seat',db.String(3),nullable=False)
    email=db.Column('email',db.String(15),nullable=False)
    phone=db.Column('phone',db.String(15),nullable=False)
    # booking reference (used for verification before viewing and managing and viewing bookings)
    ref = db.Column('ref',db.Integer,nullable=False)

# UserMixin is a helper class provided by Flask-Login that gives your user model all the methods and properties Flask-Login expects.
# it provides properties like is_authenticated
class Admin(db.Model,UserMixin):
    id = db.Column('id',db.Integer,primary_key=True)
    username = db.Column('username',db.String(10),nullable=False,unique=True)
    # bcrypt character is 60 characters
    hash=db.Column('hash',db.String(60),nullable=False)