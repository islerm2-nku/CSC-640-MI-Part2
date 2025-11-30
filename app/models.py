"""SQLAlchemy models matching the database schema."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.mysql import MEDIUMTEXT, INTEGER as MYSQL_INTEGER

Base = declarative_base()

class SessionInfo(Base):
    """Session information table."""
    __tablename__ = "session_info"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    session_id = Column(String(36), primary_key=True)
    session_type = Column(String(100), nullable=True)
    track_name = Column(String(255), nullable=True)
    track_id = Column(Integer, nullable=True)
    track_config = Column(String(255), nullable=True)
    session_date = Column(String(50), nullable=True)
    session_time = Column(String(50), nullable=True)
    track_config_sector_info = Column(Text, nullable=True)
    
    # Relationships
    weather = relationship("Weather", back_populates="session", cascade="all, delete-orphan", uselist=False)
    drivers = relationship("Driver", back_populates="session", cascade="all, delete-orphan")
    attributes = relationship("AttributeValue", back_populates="session", cascade="all, delete-orphan")

class Weather(Base):
    """Weather information table."""
    __tablename__ = "weather"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    session_id = Column(String(36), ForeignKey('session_info.session_id', ondelete='CASCADE'), primary_key=True)
    track_air_temp = Column(String(50), nullable=True)
    track_surface_temp = Column(String(50), nullable=True)
    track_precipitation = Column(String(50), nullable=True)
    track_fog_level = Column(String(50), nullable=True)
    track_wind_speed = Column(String(50), nullable=True)
    track_wind_direction = Column(String(50), nullable=True)
    
    # Relationship
    session = relationship("SessionInfo", back_populates="weather")

class Driver(Base):
    """Driver information table with composite primary key."""
    __tablename__ = "driver"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "driver_user_id"),
        {"mysql_engine": "InnoDB"},
    )
    
    session_id = Column(String(36), ForeignKey('session_info.session_id', ondelete='CASCADE'), nullable=False)
    driver_user_id = Column(Integer, nullable=False)
    driver_name = Column(String(255), nullable=True)
    car_number = Column(String(10), nullable=True)
    car_name = Column(String(255), nullable=True)
    car_class_id = Column(Integer, nullable=True)
    driver_rating = Column(Integer, nullable=True)
    
    # Relationship
    session = relationship("SessionInfo", back_populates="drivers")

class AttributeValue(Base):
    """Attribute values table with composite primary key."""
    __tablename__ = "attribute_values"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "attribute"),
        {"mysql_engine": "InnoDB"},
    )
    
    session_id = Column(String(36), ForeignKey('session_info.session_id', ondelete='CASCADE'), nullable=False)
    attribute = Column(String(255), nullable=False)
    value = Column(MEDIUMTEXT, nullable=True)
    value_len = Column(MYSQL_INTEGER(unsigned=True), nullable=False)
    
    # Relationship
    session = relationship("SessionInfo", back_populates="attributes")
