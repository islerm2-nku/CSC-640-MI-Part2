"""Session management endpoints."""
import json
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import SessionInfo, Weather, Driver, AttributeValue
from auth_helpers import get_current_user
from services.lap_service import LapService

router = APIRouter()

@router.get("/")
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions."""
    sessions = db.query(SessionInfo).all()
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "session_type": s.session_type,
                "track_name": s.track_name,
                "track_config": s.track_config,
                "session_date": s.session_date,
                "session_time": s.session_time
            }
            for s in sessions
        ]
    }

@router.get("/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get detailed session information."""
    session = db.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get related data
    weather = db.query(Weather).filter(Weather.session_id == session_id).first()
    drivers = db.query(Driver).filter(Driver.session_id == session_id).all()
    
    return {
        "session": {
            "session_id": session.session_id,
            "session_type": session.session_type,
            "track_name": session.track_name,
            "track_id": session.track_id,
            "track_config": session.track_config,
            "session_date": session.session_date,
            "session_time": session.session_time,
            "track_config_sector_info": session.track_config_sector_info
        },
        "weather": {
            "track_air_temp": weather.track_air_temp,
            "track_surface_temp": weather.track_surface_temp,
            "track_precipitation": weather.track_precipitation,
            "track_fog_level": weather.track_fog_level,
            "track_wind_speed": weather.track_wind_speed,
            "track_wind_direction": weather.track_wind_direction
        } if weather else None,
        "drivers": [
            {
                "driver_user_id": d.driver_user_id,
                "driver_name": d.driver_name,
                "car_number": d.car_number,
                "car_name": d.car_name,
                "car_class_id": d.car_class_id,
                "driver_rating": d.driver_rating
            }
            for d in drivers
        ]
    }

@router.get("/{session_id}/laps")
async def get_session_lap_count(session_id: str, db: Session = Depends(get_db)):
    """Get lap count and lap data for a session with optional incident detection."""
    try:
        # Include incident detection in lap data
        laps = LapService.get_lap_indices(session_id, db, include_incidents=True)
        
        # Count valid laps (no incidents)
        valid_lap_count = sum(1 for lap in laps if lap.get('valid_lap', True))
        
        return {
            "session_id": session_id,
            "lap_count": len(laps),
            "valid_lap_count": valid_lap_count,
            "invalid_lap_count": len(laps) - valid_lap_count,
            "laps": laps
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/laps/{lap_number}")
async def get_lap_attribute_data(
    session_id: str,
    lap_number: int,
    attribute: str = Query(..., description="Attribute name to retrieve"),
    db: Session = Depends(get_db)
):
    """Get telemetry data for a specific attribute in a specific lap."""
    try:
        # Get lap data
        laps = LapService.get_lap_indices(session_id, db)
        
        # Find the specific lap
        lap_data = next((lap for lap in laps if lap['lap_number'] == lap_number), None)
        
        if not lap_data:
            raise HTTPException(status_code=404, detail=f"Lap {lap_number} not found in session")
        
        # Fetch the attribute value
        attr_value = db.query(AttributeValue).filter(
            AttributeValue.session_id == session_id,
            AttributeValue.attribute == attribute
        ).first()
        
        if not attr_value:
            raise HTTPException(status_code=404, detail=f"Attribute '{attribute}' not found for this session")
        
        # Parse the attribute data
        try:
            attribute_data = json.loads(attr_value.value)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse attribute data: {str(e)}")
        
        # Extract data for the specific lap range
        start_index = lap_data['start_index']
        end_index = lap_data['end_index']
        
        lap_attribute_data = {
            str(i): attribute_data[i] if i < len(attribute_data) else None
            for i in range(start_index, end_index + 1)
        }
        
        return {
            "session_id": session_id,
            "lap_number": lap_number,
            "attribute": attribute,
            "start_index": start_index,
            "end_index": end_index,
            "sample_count": lap_data['sample_count'],
            "data": lap_attribute_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/laps/{lap_number}/averages")
async def get_lap_attribute_averages(
    session_id: str,
    lap_number: int,
    attribute: List[str] = Query(..., description="Attribute names to calculate averages for"),
    db: Session = Depends(get_db)
):
    """Get average, min, and max values for specified attributes in a specific lap."""
    try:
        # Get lap data
        laps = LapService.get_lap_indices(session_id, db)
        
        # Find the specific lap
        lap_data = next((lap for lap in laps if lap['lap_number'] == lap_number), None)
        
        if not lap_data:
            raise HTTPException(status_code=404, detail=f"Lap {lap_number} not found in session")
        
        start_index = lap_data['start_index']
        end_index = lap_data['end_index']
        
        # Fetch all requested attributes and calculate averages
        attributes_averages = {}
        for attr_name in attribute:
            attr_value = db.query(AttributeValue).filter(
                AttributeValue.session_id == session_id,
                AttributeValue.attribute == attr_name
            ).first()
            
            if not attr_value:
                attributes_averages[attr_name] = None
                continue
            
            # Parse the attribute data
            try:
                parsed_data = json.loads(attr_value.value)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse attribute '{attr_name}': {str(e)}")
            
            # Calculate statistics for this lap's frame range
            values = [
                parsed_data[i] for i in range(start_index, end_index + 1)
                if i < len(parsed_data) and isinstance(parsed_data[i], (int, float))
            ]
            
            # Calculate statistics
            if values:
                attributes_averages[attr_name] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "sample_count": len(values)
                }
            else:
                attributes_averages[attr_name] = {
                    "average": None,
                    "min": None,
                    "max": None,
                    "sample_count": 0
                }
        
        return {
            "session_id": session_id,
            "lap_number": lap_number,
            "start_index": start_index,
            "end_index": end_index,
            "lap_sample_count": lap_data['sample_count'],
            "attributes": attributes_averages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}/laps/{lap_number}")
async def delete_lap_attribute_data(
    session_id: str,
    lap_number: int,
    current_user: dict = Depends(get_current_user),
    attribute: Optional[List[str]] = Query(None, description="Specific attributes to delete (default: all)"),
    db: Session = Depends(get_db)
):
    """Delete telemetry data for a specific lap. Requires authentication."""
    try:
        # Get lap data
        laps = LapService.get_lap_indices(session_id, db)
        
        # Find the specific lap
        lap_data = next((lap for lap in laps if lap['lap_number'] == lap_number), None)
        
        if not lap_data:
            raise HTTPException(status_code=404, detail=f"Lap {lap_number} not found in session")
        
        start_index = lap_data['start_index']
        end_index = lap_data['end_index']
        
        # Determine which attributes to delete
        if attribute:
            attributes_to_delete = attribute
        else:
            # Get all attributes for this session
            all_attrs = db.query(AttributeValue.attribute).filter(
                AttributeValue.session_id == session_id
            ).distinct().all()
            attributes_to_delete = [attr[0] for attr in all_attrs]
        
        # Delete data for each attribute in the lap range
        deleted_count = 0
        for attr_name in attributes_to_delete:
            attr_value = db.query(AttributeValue).filter(
                AttributeValue.session_id == session_id,
                AttributeValue.attribute == attr_name
            ).first()
            
            if not attr_value:
                continue
            
            # Parse the attribute data
            try:
                attribute_data = json.loads(attr_value.value)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse attribute '{attr_name}': {str(e)}")
            
            # Remove data for indices in the lap range
            original_length = len(attribute_data)
            attribute_data = [
                val for i, val in enumerate(attribute_data)
                if i < start_index or i > end_index
            ]
            deleted_count += original_length - len(attribute_data)
            
            # Update the attribute with modified data
            new_value = json.dumps(attribute_data)
            attr_value.value = new_value
            attr_value.value_len = len(attribute_data)
        
        db.commit()
        
        return {
            "session_id": session_id,
            "lap_number": lap_number,
            "attributes_deleted": attributes_to_delete,
            "start_index": start_index,
            "end_index": end_index,
            "data_points_deleted": deleted_count,
            "message": f"Successfully deleted attribute data for lap {lap_number}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a session (and all related data via CASCADE)."""
    session = db.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": f"Session {session_id} deleted successfully"}
