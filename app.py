#################################################
# import libraries
#################################################
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
# Use SQLAlchemy create_engine to connect to your sqlite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Set up Flask and landing page
#################################################
app = Flask(__name__)

# last 12 months variable
last_twelve_months = '2016-08-23'

# Homepage: List all routes that are available
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<p>Welcome to the Hawaii weather API!</p>"
        f"<p>Usage:</p>"
        f"/api/v1.0/precipitation<br/>:  returns a JSON list of percipitation data for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/stations<br/>:  returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>:  returns a JSON list of the Temperature Observations (tobs) for each station for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/start<br/>:  return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start.<br/><br/>"
        f"/api/v1.0/start/end<br/>:  return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.<br/><br/>"   
            )

# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Date 12 months ago
    p_results = dict(session.query(Measurement.date, func.avg(Measurement.prcp)).\
    filter(Measurement.date >= last_twelve_months).group_by(Measurement.date).all())

    return jsonify(p_results)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    s_results = dict(session.query(Station.station, Station.name).all())
    
    return jsonify(s_results)

#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    last_date = dt.date(2017, 8 ,23)
    year_ago = last_date - dt.timedelta(days=365)

    #Query the dates and temperature observations of the most active station for the last year of data.
    # the most active stataion name is USC00519281
    most_pop_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).all()

    pop_station_tobs = session.query(Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station=='USC00519281').all()

    lists = pd.DataFrame(pop_station_tobs).rename(columns={0:'temperature'}).temperature.tolist()

    return jsonify(lists)

@app.route("/api/v1.0/<start>")
# route example: /api/v1.0/2017-01-01


@app.route('/api/v1.0/<start>') 
def start(start):
    # route example: /api/v1.0/2017-01-01

    start = Measurement.date <= '2010-01-01'
    end = Measurement.date >= '2017-08-23'
    start = Measurement.date <= '2010-01-01'
    end = Measurement.date >= '2017-08-23'

    tobs_only = (session.query(Measurement.tobs).filter(Measurement.date.between(start, '2017-08-23')).all())
            
    tobs_df = pd.DataFrame(tobs_only).rename(columns = {0:'tobs'})
    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()

    df = [tavg,tmax,tmin]
    label = ['tavg','tmax','tmin']

    dictionary = zip(label,df)
    final_df = dict(dictionary)
    
    return jsonify(final_df)

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    start = dt.date(2010, 1 ,1)
    end = dt.date(2017, 8 ,23)
    multi_day_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    return jsonify(multi_day_temp_results)


if __name__ == '__main__':
    app.run(debug=True)