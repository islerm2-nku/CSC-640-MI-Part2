"""Lap analysis service for telemetry data."""
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import AttributeValue

class LapService:
    """Service for analyzing lap data from telemetry."""
    
    @staticmethod
    def get_lap_indices(session_id: str, db: Session, include_incidents: bool = False) -> List[Dict]:
        """
        Get lap data for a specific session and parse lap start/end indices.
        
        Args:
            session_id: The session ID to fetch lap data for
            db: Database session
            include_incidents: Whether to check for incidents in each lap
            
        Returns:
            Array containing lap information with start and end indices for each lap
            
        Raises:
            ValueError: If session not found or data cannot be parsed
        """
        # Fetch the Lap attribute value for the session
        lap_attr = db.query(AttributeValue).filter(
            AttributeValue.session_id == session_id,
            AttributeValue.attribute == 'Lap'
        ).first()
        
        if not lap_attr:
            raise ValueError(f"No lap data found for session: {session_id}")
        
        # Parse the lap data
        try:
            lap_data = json.loads(lap_attr.value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse lap data: {str(e)}")
        
        # Process lap data to find start and end indices for each lap
        laps = LapService._parse_lap_indices(lap_data)
        
        # Add incident detection if requested
        if include_incidents:
            laps = LapService._add_incident_data(session_id, laps, db)
        
        return laps
    
    @staticmethod
    def _parse_lap_indices(lap_data: List) -> List[Dict]:
        """
        Parse lap data array to find start and end indices for each lap.
        
        Args:
            lap_data: Array of lap numbers indexed by sample position
            
        Returns:
            Array of laps with their start and end indices
        """
        if not lap_data:
            return []
        
        laps = []
        current_lap = None
        start_index = None
        
        for index, lap_number in enumerate(lap_data):
            # Skip if lap number is 0 or negative (usually warmup/cooldown)
            if lap_number <= 0:
                continue
            
            # New lap detected
            if current_lap != lap_number:
                # Save previous lap if it exists
                if current_lap is not None and start_index is not None:
                    laps.append({
                        'lap_number': current_lap,
                        'start_index': start_index,
                        'end_index': index - 1,
                        'sample_count': (index - 1) - start_index + 1
                    })
                
                # Start new lap
                current_lap = lap_number
                start_index = index
        
        # Add the last lap
        if current_lap is not None and start_index is not None:
            last_index = len(lap_data) - 1
            laps.append({
                'lap_number': current_lap,
                'start_index': start_index,
                'end_index': last_index,
                'sample_count': last_index - start_index + 1
            })
        
        return laps
    
    @staticmethod
    def _add_incident_data(session_id: str, laps: List[Dict], db: Session) -> List[Dict]:
        """
        Add incident data to laps by checking PlayerIncidents attribute.
        
        Args:
            session_id: The session ID
            laps: Array of lap data with start/end indices
            db: Database session
            
        Returns:
            Laps with added incident information
        """
        # Try to fetch PlayerIncidents attribute
        incident_attr = db.query(AttributeValue).filter(
            AttributeValue.session_id == session_id,
            AttributeValue.attribute == 'PlayerIncidents'
        ).first()
        
        # If PlayerIncidents doesn't exist, mark all laps as valid
        if not incident_attr:
            for lap in laps:
                lap['valid_lap'] = True
                lap['incidents_in_lap'] = None
            return laps
        
        # Parse the PlayerIncidents data
        try:
            incident_data = json.loads(incident_attr.value)
        except json.JSONDecodeError:
            # If we can't parse incidents, assume all laps are valid
            for lap in laps:
                lap['valid_lap'] = True
                lap['incidents_in_lap'] = None
            return laps
        
        # Check each lap for incidents
        for lap in laps:
            start_index = lap['start_index']
            end_index = lap['end_index']
            
            # Count all incidents (1 values) within the lap's frame range
            incident_count = sum(
                1 for i in range(start_index, end_index + 1)
                if i < len(incident_data) and incident_data[i] == 1
            )
            
            lap['incidents_in_lap'] = incident_count
            lap['valid_lap'] = incident_count == 0
        
        return laps
