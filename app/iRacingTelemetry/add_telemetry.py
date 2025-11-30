import json
import uuid
import mysql.connector
import os

def get_db_connection():
    """Create and return a MySQL database connection."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_DATABASE', 'app'),
        user=os.getenv('DB_USER', 'appuser'),
        password=os.getenv('DB_PASSWORD', 'apppass')
    )
def add_telemetry(telemetry_json):
    """Parse telemetry data from the given .ibt file and return as JSON."""
    session_id = str(uuid.uuid4())
    session_info = get_session_info(session_id, telemetry_json)
    weather_info = get_weather_info(session_id, telemetry_json)
    driver_info = get_driver_info(session_id, telemetry_json)
    attribute_data = get_attribute_data(session_id, telemetry_json.get("telemetry", {}))

    # Insert data into database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert session_info
        cursor.execute("""
            INSERT INTO session_info 
            (session_id, session_type, track_name, track_id, track_config, 
             session_date, session_time, track_config_sector_info)
            VALUES (%(session_id)s, %(session_type)s, %(track_name)s, %(track_id)s, 
                    %(track_config)s, %(session_date)s, %(session_time)s, 
                    %(track_config_secttor_info)s)
        """, session_info)
        
        # Insert weather
        cursor.execute("""
            INSERT INTO weather 
            (session_id, track_air_temp, track_surface_temp, track_precipitation, 
             track_fog_level, track_wind_speed, track_wind_direction)
            VALUES (%(session_id)s, %(track_air_temp)s, %(track_surface_temp)s, 
                    %(track_precipitation)s, %(track_fog_level)s, %(track_wind_speed)s, 
                    %(track_wind_direction)s)
        """, weather_info)
        
        # Insert driver
        for driver in driver_info:
            cursor.execute("""
                INSERT INTO driver 
                (session_id, driver_user_id, driver_name, car_number, car_name, 
                car_class_id, driver_rating)
                VALUES (%(session_id)s, %(driver_user_id)s, %(driver_name)s, %(car_number)s, 
                        %(car_name)s, %(car_class_id)s, %(driver_rating)s)
            """, driver)

         # Insert attribute values (multiple records)
        if attribute_data:
            insert_sql = """
                INSERT INTO attribute_values (session_id, attribute, value, value_len)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE value = VALUES(value), value_len = VALUES(value_len)
            """
            rows = [
                (rec["session_id"], rec["attribute_name"], rec["value"], rec["value_len"])
                for rec in attribute_data
            ]
            cursor.executemany(insert_sql, rows)
        
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return {
        "session_info": session_info,
        "weather_info": weather_info,
        "driver_info": driver_info
    }

def get_session_info(session_id, telemetry_json):
    return {
        "session_id": session_id,
        "session_type": telemetry_json["session_info"]["SessionInfo"]["Sessions"][0]["SessionType"],
        "track_name": telemetry_json["session_info"]["WeekendInfo"]["TrackDisplayName"],
        "track_id": telemetry_json["session_info"]["WeekendInfo"]["TrackID"],
        "track_config": telemetry_json["session_info"]["WeekendInfo"]["TrackConfigName"],
        "session_date": telemetry_json["session_info"]["WeekendInfo"]["WeekendOptions"]["Date"],
        "session_time": telemetry_json["session_info"]["WeekendInfo"]["WeekendOptions"]["TimeOfDay"],
        "track_config_secttor_info": json.dumps(telemetry_json["session_info"]["SplitTimeInfo"]["Sectors"])
    }
def get_weather_info(session_id, telemetry_json):
    return {
        "session_id": session_id,
        "track_air_temp": telemetry_json["session_info"]["WeekendInfo"]["TrackAirTemp"],
        "track_surface_temp": telemetry_json["session_info"]["WeekendInfo"]["TrackAirTemp"],
        "track_precipitation": telemetry_json["session_info"]["WeekendInfo"]["TrackPrecipitation"],
        "track_fog_level": telemetry_json["session_info"]["WeekendInfo"]["TrackFogLevel"],
        "track_wind_speed": telemetry_json["session_info"]["WeekendInfo"]["WeekendOptions"]["WindSpeed"],
        "track_wind_direction": telemetry_json["session_info"]["WeekendInfo"]["WeekendOptions"]["WindDirection"]  
    }
def get_driver_info(session_id, telemetry_json):
    drivers = []
    driverList = telemetry_json["session_info"]["DriverInfo"]["Drivers"]
    for driver in driverList:
        drivers.append({
            "session_id": session_id,
            "driver_user_id": driver["UserID"],
            "driver_name": driver["UserName"],
            "car_number": driver["CarNumber"],
            "car_name": driver["CarScreenName"],
            "car_class_id": driver["CarClassID"],
            "driver_rating": driver["IRating"],
        })
    return drivers

def get_attribute_data(session_id, telemetry_data):
    records = []
    for attribute, values in telemetry_data.items():
        records.append({
            "session_id": session_id,
            "attribute_name": attribute,
            "value": json.dumps(values),
            "value_len": len(values)
        })
    return records