
#################################################
# SQL Setup
#################################################
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify

import datetime as dt

app = Flask(__name__)



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


stations_list = [
    {"superhero": "Aquaman", "real_name": "Arthur Curry"},
    {"superhero": "Batman", "real_name": "Bruce Wayne"},
    {"superhero": "Cyborg", "real_name": "Victor Stone"},
    {"superhero": "Flash", "real_name": "Barry Allen"},
    {"superhero": "Green Lantern", "real_name": "Hal Jordan"},
    {"superhero": "Superman", "real_name": "Clark Kent"},
    {"superhero": "Wonder Woman", "real_name": "Princess Diana"}
]


#################################################
# Flask Routes
#################################################

#Home page.
@app.route("/")
def home():

    #List all routes that are available.
    print(f"Server received request for 'Home' page...")

    return (
        f"Choose from the following routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


#/api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
#Returns the JSON representation of your precipitation dictionary.

    print(f"Server received a request for precipitation data...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    ## It doesn't say so in the instructions clearly for me, but due to how slow this is running, 
    ## I believe this route is supposed to return just the past year of precipitation data

    # Calculate the date 1 year ago from the last data point in the database
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Parse the date dictionary's string into a datetime object so we can manipulate it
    most_recent_dt = dt.datetime.strptime(most_recent.date, '%Y-%m-%d')
    year_ago_dt = most_recent_dt - dt.timedelta(days=365)
    year_ago_date = year_ago_dt.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    all_measurements = []
    for row in results:
        measurement_dict = {}
        measurement_dict[row.date] = row.prcp

        # Append the dictionary to an ongoing list of dictionaries
        all_measurements.append(measurement_dict)
    
    return jsonify(all_measurements)


#/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
#Returns a JSON list of stations from the dataset.

    print(f"Server received a request for weather station data...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station).all()

    session.close()

   # Create a dictionary from the results data and append to a list of all_stations
    all_stations = []
    for row in results:
        station_dict = {}
        station_dict["id"] = row.id
        station_dict["station"] = row.station
        station_dict["name"] = row.name
        station_dict["latitude"] = row.latitude
        station_dict["longitude"] = row.longitude
        station_dict["elevation"] = row.elevation

        # Append the dictionary to an ongoing list of dictionaries
        all_stations.append(station_dict)

    return jsonify(all_stations)



#/api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
#Return a JSON list of temperature observations (TOBS) for the previous year.

    print(f"Server received a request for temperature observation data...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # First, determine the date 1 year ago from the last data point in the database
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Parse the date dictionary's string into a datetime object so we can manipulate it
    most_recent_dt = dt.datetime.strptime(most_recent.date, '%Y-%m-%d')
    year_ago_dt = most_recent_dt - dt.timedelta(days=365)
    year_ago_date = year_ago_dt.strftime('%Y-%m-%d')

    # Second, determine the most active station in the past year
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    #Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(Measurement.tobs, Measurement.station, Measurement.date).filter(Measurement.station == most_active_station.station).filter(Measurement.date >= year_ago_date).all()

    session.close()

    # Convert the query results to a dictionary
    all_observations = []
    for row in results:
        measurement_dict = {}
        measurement_dict["date"] = row.date
        measurement_dict["tobs"] = row.tobs
        measurement_dict["station"] = row.station

        # Append the dictionary to an ongoing list of dictionaries
        all_observations.append(measurement_dict)
    
    return jsonify(all_observations)



#/api/v1.0/yyyy-mm-dd
@app.route("/api/v1.0/<start>")
def start(start):
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date

    print(f"Server received a request for temperature summary data from start date: {start}...")

    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    todays_date = dt.datetime.date(dt.datetime.now())
    results = start_end(start, todays_date)

    # results should already be jsonified from the start_end funtion
    return results


#/api/v1.0/yyyy-mm-dd/yyyy-mm-dd
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end date range.

    print(f"Server received a request for temperature summary data from start date: {start} to end date: {end}...")

    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


    return "Hello World!"




if __name__ == "__main__":
    app.run(debug=True)