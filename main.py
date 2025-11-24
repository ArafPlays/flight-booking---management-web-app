from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import datetime

app=Flask(__name__)
app.secret_key = "^@^$Lrj$@$JJ223828AJEJA2828$"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

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
    duration= db.Column("duration",db.String(10), nullable=False)
    fclass = db.Column("fclass",db.String(10), nullable=False)
    price= db.Column("price",db.Integer, nullable=False)

class Passenger(db.Model):
    id=db.Column('id',db.Integer,primary_key=True)
    title = db.Column("title",db.String(5),nullable=False)
    fname = db.Column("fname",db.String(10),nullable=False)
    lname = db.Column("lname",db.String(10),nullable=False)
    nationality=db.Column("nationality",db.String(10),nullable=False)
    gender=db.Column("gender",db.String(10),nullable=False)
    email = db.Column("email",db.String(20),nullable=False)
    # relationship
    bookings = db.relationship("Booking",backref='passenger',lazy=True)
    # backref automatically creates booking.passenger

class Booking(db.Model):
    # booking id
    id=db.Column('id',db.Integer,primary_key=True)

    # store passenger and flight
    passenger_id=db.Column(db.Integer,db.ForeignKey('passenger.id'), nullable=False)
    depart_flight_num=db.Column(db.Integer,db.ForeignKey('flight.num'),nullable=False)
    # using 2 foreign key to same key will cause an error here, 
    # we need to specify
    return_flight_num=db.Column(db.Integer,db.ForeignKey('flight.num'),nullable=False) # nullable false because it has to be 0 (no return) or a flight id

    # specifying foreign keys
    depart_flight=db.relationship('Flight',foreign_keys=[depart_flight_num],backref='depart_bookings')
    return_flight=db.relationship('Flight',foreign_keys=[return_flight_num],backref='return_bookings')
    # backref automatically gives us access to flight.departure_bookings and flight.return_bookings

    # store booking preferences
    meal=db.Column('meal',db.String(10),nullable=False)
    seat=db.Column('seat',db.String(3),nullable=False)

@app.route("/",methods=['GET','POST'])
def index():
    if request.method=='GET':
        return render_template('index.html')
    elif request.method=='POST':
        # clear session first to avoid any collisions
        session.clear()
        # if submit button is clicked, save to session
        session['cityFrom'] = request.form['cityFrom']
        session['cityTo'] = request.form['cityTo']
        session['departDate'] = request.form['departDate']
        session['returnDate'] = request.form['returnDate']
        session['fclass'] = request.form['fclass']
        session['passenger_num'] = request.form['passenger_num']
        # send user to departure page with url query parameters
        return redirect(url_for('departure'))
    
@app.route("/departure")
def departure():
    # query flights database and show flights that match
    matching_flights = Flight.query.filter_by(cityFrom=session['cityFrom'],cityTo=session['cityTo'],departDate=session['departDate'],fclass=session['fclass'])
    return render_template('departure.html',matching_flights=matching_flights)

@app.route("/return-flight")
def return_flight():
    # flip cityTo and cityFrom
    cityTo = session['cityFrom'] 
    cityFrom = session['cityTo'] 
    returnDate=session['returnDate']
    fclass=session['fclass']
    # query flights database and show flights that match
    # this flight will depart on the user selected return date
    matching_flights = Flight.query.filter_by(cityFrom=cityFrom,cityTo=cityTo,departDate=returnDate,fclass=fclass)
    return render_template('departure.html',matching_flights=matching_flights)

# this function saves both selected departing and returning flight. Saves space rather than having 2 separate functions
@app.route("/save_flight/<int:num>")
def save_flight(num):
    # first figure out if it is depart or return flight
    # if session['num'] exists, departing flight has been selected, so we book return flight 
    if 'num' in session:
        session['return_num'] = num
    # if session['num'] doesn't exist, departing flight has not been selected, so we book departing flight first 
    else:
        session['num'] = num
        if session['returnDate']!="":
            # if there's a return date, take them to select return flight selection page
            return redirect(url_for('return_flight'))
    # take them to personal details page if return flight has been saved
    return redirect(url_for('personal_details'))

@app.route("/personal-details",methods=['GET','POST'])
def personal_details():
    if request.method=='GET':
        return render_template('personal-details.html')
    elif request.method=='POST':
        # if user submits, save info to session
        session['title'] = request.form['title']
        session['fname'] = request.form['fname'] 
        session['lname'] = request.form['lname'] 
        session['nationality'] = request.form['nationality'] 
        session['gender'] = request.form['gender'] 
        session['email'] = request.form['email'] 
        # redirect to next page of wizard
        return redirect(url_for("seat",chosenSeat='NA'))

@app.route("/seat")
def seat():
    chosenSeat = request.args['chosenSeat']
    return render_template('seat.html',chosenSeat=chosenSeat)

@app.route("/save-seat/<chosenSeat>")
def save_seat(chosenSeat):
    # save seat to session
    session['chosenSeat'] = chosenSeat
    
    # return f"{session['chosenSeat']}"

    # redirect to next page
    return redirect(url_for('meal'))

@app.route("/meal")
def meal():
    return render_template('meal.html')

@app.route("/meal/<preference>")
def save_meal(preference):
    # save meal to session
    session['preference'] = preference
    # redirect to next page
    return redirect(url_for('payment'))

@app.route("/payment",methods=['GET','POST'])
def payment():
    if request.method=='GET':
        # get flight info
        flight_num = session['num']
        flight = Flight.query.filter_by(num=flight_num).first()
        # get meal and seat number
        # preference = session['preference']
        # chosenSeat = session['chosenSeat']
        # passing session automatically sends all session data, no need to create variables and send individually
        return render_template('payment.html',flight=flight,session=session)
    elif request.method=='POST':
        # save to database
        # add new passenger to database
        title= session['title']
        fname = session['fname']
        lname = session['lname'] 
        nationality=session['nationality']
        gender=session['gender']
        email=session['email'] 

        # Note: When primary_key=True and the type is Integer, SQLAlchemy + the database automatically treat it as auto-increment. We don't need to pass in any passenger id
        new_passenger = Passenger(title=title,fname=fname,lname=lname,nationality=nationality,gender=gender,email=email)
        db.session.add(new_passenger)

        db.session.commit()
        
        # add new booking to database
        depart_flight_num=session['num']
        preference = session['preference']
        chosenSeat = session['chosenSeat']

        # if return date was kept empty, return flight number will be 0
        if session['returnDate'] =="":
            return_flight_num=0
        else:
            # if return date wasn't empty, customer will have already selected and saved a return flight number into session, we simply access and store it into a variable
            return_flight_num=session['return_num']

        new_booking = Booking(passenger_id=new_passenger.id,depart_flight_num=depart_flight_num,return_flight_num=return_flight_num,meal=preference,seat=chosenSeat)
        db.session.add(new_booking)
        db.session.commit()
        flash("Saved to database")
        session.clear()
        return redirect(url_for('confirmed',booking_id=new_booking.id,lname=new_passenger.lname))

@app.route("/confirmed/<int:booking_id>/<lname>")
def confirmed(booking_id,lname):
    # get the booking, flight and passenger associated with this booking id.
    booking=Booking.query.filter_by(id=booking_id).first()

    passenger_id = booking.passenger_id
    passenger = Passenger.query.filter_by(id=passenger_id).first()
    # url verification, lname needs to match booking lname in order to retrieve info
    if passenger.lname==lname:
        depart_flight_num=booking.depart_flight_num
        depart_flight = Flight.query.filter_by(num=depart_flight_num).first()
        return_flight_num=booking.return_flight_num
        return_flight = Flight.query.filter_by(num=return_flight_num).first()
        return render_template('confirmed.html',booking=booking,depart_flight=depart_flight,return_flight=return_flight,passenger=passenger)
    else:
        return f"Booking id and last name doesn't match."

# flights can be added to flights database on this page
@app.route("/admin",methods=['GET','POST'])
def admin():
    if request.method=='GET':
        # get all flights so we can show them on the page
        all_flights = Flight.query.all()
        return render_template('admin.html',all_flights=all_flights)
    elif request.method=='POST':
        cityFrom = request.form['cityFrom']
        cityTo = request.form['cityTo']
        departDate = request.form['departDate']
        arrivalDate = request.form['arrivalDate']
        departTime = request.form['departTime']
        arrivalTime = request.form['arrivalTime']
        fclass = request.form['fclass']
        duration = request.form['duration']
        price = request.form['price']
        new_flight = Flight(cityFrom=cityFrom,cityTo=cityTo,departDate=departDate,arrivalDate=arrivalDate,departTime=departTime,arrivalTime=arrivalTime,duration=duration,fclass=fclass,price=price)
        db.session.add(new_flight)
        db.session.commit()
        # refresh the page
        return redirect(url_for('admin'))

# delete a flight from admin panel
@app.route('/admin/delete/<int:num>')
def delete(num):
    flight_to_delete = Flight.query.filter_by(num=num).first()
    db.session.delete(flight_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))

# edit a flight from admin panel
@app.route('/admin/edit/<int:num>',methods=['GET','POST'])
def edit(num):
    if request.method=='GET':
        flight_to_edit = Flight.query.filter_by(num=num).first()
        return render_template('edit.html',flight_to_edit=flight_to_edit)
    elif request.method=='POST':
        flight_to_edit = Flight.query.filter_by(num=num).first()
        # edit database when user submits edit form
        flight_to_edit.cityFrom=request.form['cityFrom']
        flight_to_edit.cityTo=request.form['cityTo']
        flight_to_edit.departDate=request.form['departDate']
        flight_to_edit.arrivalDate=request.form['arrivalDate']
        flight_to_edit.departTime=request.form['departTime']
        flight_to_edit.arrivalTime=request.form['arrivalTime']
        flight_to_edit.fclass=request.form['fclass']
        flight_to_edit.duration=request.form['duration']
        flight_to_edit.price=request.form['price']
        db.session.commit()
        return redirect(url_for('admin'))

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=8000,debug=True)