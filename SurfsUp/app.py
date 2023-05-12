# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Save dates as variables for use in routes
latest_date = dt.date(2017, 8, 23)
year_ago = latest_date - dt.timedelta(days=365)

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Create home page route
@app.route("/")
def welcome():
    """List all available routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2015-08-15<br/>"
        f"/api/v1.0/2015-08-15/2017-08-23"
    )


# Create precipitation page to pull measurements from the last 12 months and put into dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Use query from climate_starter.py file"""
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > year_ago).all()
    session.close()

    """Enter information into dictionary/list""" 
    results = []
    for date, prcp in precipitation:
        results_dict = {}
        results_dict["date"] = date
        results_dict["prcp"] = prcp
        results.append(results_dict)
    
    return jsonify(results)


# Create stations page to pull list of station names
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    session.close()
    names = list(np.ravel(stations))

    return jsonify(names)


# Create tobs page to show temperatures from last 12 months for most active station
@app.route("/api/v1.0/tobs")
def tobs():

    """Use query from climate_starter.py file"""
    sel = [Measurement.station, func.count(Measurement.station)]
    station_counts = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active = station_counts[0][0]
    most_active_info = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= year_ago).all()
    session.close()

    """Enter information into dictionary/list"""
    tobs_results = []
    for date, tobs in most_active_info:
        tobs_results_dict = {}
        tobs_results_dict["date"] = date
        tobs_results_dict["tobs"] = tobs
        tobs_results.append(tobs_results_dict)
    
    return jsonify(tobs_results)


# Create pages to show min, max, and avg temps based on user-input start date
@app.route("/api/v1.0/<start>")
def tobs_start(start):

    sel = [Measurement.date,
           func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    session.close()

    """Enter information into dictionary/list"""
    date_results = []
    for date, min, max, avg in results:
            date_results_dict = {}
            date_results_dict["date"] = date
            date_results_dict["min"] = min
            date_results_dict["max"] = max
            date_results_dict["avg"] = avg
            date_results.append(date_results_dict)
    
    if date_results:
        return jsonify(date_results)
    
    # Include error message if date isn't included in dataset or is in incorrect format
    else:
        return jsonify({"error": f"Dates not found or not in correct format of YYYY-MM-DD"}), 404


# Create pages to show min, max, and avg temps based on user-input start and end date
@app.route("/api/v1.0/<start>/<end>")
def tobs_end(start, end):

    sel = [Measurement.date,
           func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    session.close()

    """Enter information into dictionary/list"""
    date_results = []
    for date, min, max, avg in results:

            date_results_dict = {}
            date_results_dict["date"] = date
            date_results_dict["min"] = min
            date_results_dict["max"] = max
            date_results_dict["avg"] = avg
            date_results.append(date_results_dict)
    
    if date_results:
        return jsonify(date_results)
    
    # Include error message if date isn't included in dataset or is in incorrect format
    else:
        return jsonify({"error": f"Dates not found or not in correct format of YYYY-MM-DD"}), 404

if __name__ == "__main__":
    app.run(debug=True)