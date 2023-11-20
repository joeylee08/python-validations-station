from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime, timedelta

db = SQLAlchemy()


class Station(db.Model, SerializerMixin):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80))

    # def __repr__(self):
    #     return f"<Station {self.name}>"
    
    platforms = db.relationship('Platform', back_populates='station')
    
    @validates('name')
    def validate_name(self, _, value):
        if Station.query.filter_by(name=value).first():
            raise ValueError("That name already exists.")
        elif len(value) < 3:
            raise ValueError("Name must be at least 3 characters.")            
        else:
            return value


class Platform(db.Model, SerializerMixin):
    __tablename__ = "platforms"

    id = db.Column(db.Integer, primary_key=True)
    platform_num = db.Column(db.Integer)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"))

    # def __repr__(self):
    #     return f"<Platform {self.name}>"
    
    station = db.relationship('Station', back_populates='platforms')
    assignments = db.relationship('Assignment', back_populates='platform')

    trains = association_proxy('assignments', 'train')
    
    @validates('platform_num')
    def validate_platform(self, _, value):
        if not isinstance(value, int):
            raise ValueError("Platform number must be an integer.")
        elif not 1 <= value <= 20:
            raise ValueError("Platform number must be between 1 and 20.")
        elif Platform.query.filter_by(id=value).first():
            raise ValueError("Platform number already exists.")
        else:
            return value


class Train(db.Model, SerializerMixin):
    __tablename__ = "trains"

    id = db.Column(db.Integer, primary_key=True)
    train_num = db.Column(db.String)
    service_type = db.Column(db.String)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)

    assignments = db.relationship('Assignment', back_populates='train')

    platforms = association_proxy('assignments', 'platform')

    # def __repr__(self):
    #     return f"<Train {self.name}>"
    
    @validates('origin')
    def validate_origin(self, _, value):
        if not isinstance(value, str) and not 3 <= len(value) < 24:
            raise ValueError('Origin must be a string between 3 and 24 characters.')
        else:
            return value
    
    @validates('destination')
    def validate_destination(self, _, value):
        if not isinstance(value, str) and not 3 <= len(value) < 24:
            raise ValueError('Destination must be a string between 3 and 24 characters.')
        else:
            return value

    @validates('service_type')
    def validate_service_type(self, _, value):
        service_types = ['express', 'local']
        if value not in service_types:
            raise ValueError("Service type must be either express or local.")
        else:
            return value


class Assignment(db.Model, SerializerMixin):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    arrival_time = db.Column(db.DateTime, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"))
    platform_id = db.Column(db.Integer, db.ForeignKey("platforms.id"))

    train = db.relationship('Train', back_populates='assignments')
    platform = db.relationship('Platform', back_populates='assignments')

    @validates('departure_time')
    def validate_departure_time(self, _, value):
        arrives = self.arrival_time
        departs = value
        diff_in_mins = (departs - arrives).seconds / 60
        if arrives > departs:
            raise ValueError('Train must depart after arrival time.')
        elif diff_in_mins > 20:
            raise ValueError('Train must not stay at the station for more than 20 minutes.')
        else:
            return value
        
    # def __repr__(self):
    #     return f"<Assignment Train No: {self.train.train_num} Platform: {self.platform.platform_num}>"
