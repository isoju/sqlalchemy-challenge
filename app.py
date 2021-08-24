from datetime import date
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#setting up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base  = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)


#saving tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#setting up flask
app = Flask(__name__)
# if __name__ == '__main__':
#       app.run(host='0.0.0.0')

#routes
@app.route("/")
def welcome():
    return (
        f"Home Page<br/>"
        f"List of all routes that are available:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (yyyy-mm-dd format)<br/>"
        f"/api/v1.0/start_date (yyyy-mm-dd format)/end_date (yyyy-mm-dd format)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-23").all()
        session.close()

        #dictionary

        p_list = []
        for x,y in results:
            p_dict = {}
            p_dict["date"] = x
            p_dict["prcp"] = y
            p_list.append(p_dict)
        return jsonify(p_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).order_by(Station.station).all()

    session.close()

    #converting to prevent dumb error when jsonifying results
    s_list = list(np.ravel(results))
    return jsonify(s_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= "2016-08-23").\
                filter(Measurement.station == "USC00519281").order_by(Measurement.date).all()
    session.close()

    t_list = []
    for x,y in results:
        t_dict = {}
        t_dict["date"] = x
        t_dict["tobs"] = y
        t_list.append(t_dict)

    return jsonify(t_list)

@app.route("/api/v1.0/<start_date>")
def start_date_only(start_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).order_by(Measurement.date).all()
    session.close()

    start_list = []
    for min, avg, max in results:
        start_dict = {}
        start_dict["Minimum Temperature"] = min
        start_dict["Average Temperature"] = avg
        start_dict["Maximum Temperature"] = max
        start_list.append(start_dict)

    return jsonify(start_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_and_end(start_date, end_date):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    end_list = []
    for min, avg, max in results:
        end_dict = {}
        end_dict["Minimum Temperature"] = min
        end_dict["Average Temperature"] = avg
        end_dict["Maximum Temperature"] = max
        end_list.append(end_dict)
    
    return jsonify(end_list)


if __name__ == '__main__':
    app.run(debug=True)