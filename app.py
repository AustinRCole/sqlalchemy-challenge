import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

measurements = Base.classes.measurement
stations = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"^Precipitation by date<br/>"
        f"/api/v1.0/stations<br/>"
        f"^List of stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"^Temperature readings for most active station for the last year of readings<br/>"
        f"/api/v1.0/(start date here)/(end date here)<br/>"
        f"^Enter your desired start date and end date in the above format<br/>"
        f"^^to get minimum, maximum, and average temp for a given range."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(measurements.date, measurements.prcp).all()

    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {date: prcp}
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(measurements.station).group_by(measurements.station).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_active = session.query(measurements.station,func.count(measurements.station)).group_by(measurements.station).\
    order_by(func.count(measurements.station).desc()).first()[0]

    results = session.query(measurements.tobs).filter(measurements.station == most_active).filter(measurements.date > '2016-08-23').all()

    session.close()

    all_temps = list(np.ravel(results))

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start_min = session.query(func.min(measurements.tobs)).filter(measurements.date >= start).first()[0]
    start_max = session.query(func.max(measurements.tobs)).filter(measurements.date >= start).first()[0]
    start_avg = session.query(func.avg(measurements.tobs)).filter(measurements.date >= start).first()[0]

    session.close()

    return jsonify(f"Minimum temp: {start_min}" ,f"Maximium temp: {start_max}",f"Average temp: {round(start_avg,1)}")
    
@app.route("/api/v1.0/<start>/<end>")
def select(start,end):
    session = Session(engine)

    select_min = session.query(func.min(measurements.tobs)).filter(measurements.date >= start).filter(measurements.date <= end).first()[0]
    select_max = session.query(func.max(measurements.tobs)).filter(measurements.date >= start).filter(measurements.date <= end).first()[0]
    select_avg = session.query(func.avg(measurements.tobs)).filter(measurements.date >= start).filter(measurements.date <= end).first()[0]

    session.close()

    return jsonify(f"Minimum temp: {select_min}" ,f"Maximium temp: {select_max}",f"Average temp: {round(select_avg,1)}")
        
if __name__ == '__main__':
    app.run(debug=True)