"""Telemetry data endpoints."""
import os
import json
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import SessionInfo, AttributeValue
from auth_helpers import get_current_user

from iRacingTelemetry.telemetry_parser import parse_telemetry

router = APIRouter()

@router.post("/upload")
async def upload_telemetry(
    _: dict = Depends(get_current_user),  # Protected endpoint with oauth
    telemetry_file: UploadFile = File(...),
    attributes: str = Form(""),
    db: Session = Depends(get_db)
):
    """
    Upload and parse iRacing telemetry file (.ibt).
    
    Parameters:
    - telemetry_file: The .ibt file to upload
    - attributes: JSON array of telemetry attributes to extract (default: [])
    """
    # Validate file type
    if not telemetry_file.filename.lower().endswith('.ibt'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .ibt files are allowed"
        )
    
    try:
        # Parse attributes JSON
        try:
            attributes_list = [attr.strip() for attr in attributes.split(',') if attr.strip()] if attributes else []
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid attributes format. Must be a JSON array"
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ibt') as temp_file:
            content = await telemetry_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Call telemetry parser directly
            telemetry_data = parse_telemetry(temp_file_path, attributes_list)
            
            # Check if there was an error
            if isinstance(telemetry_data, str):
                # If it's a string, it's likely an error JSON
                error_data = json.loads(telemetry_data)
                if 'error' in error_data:
                    raise HTTPException(
                        status_code=500,
                        detail=error_data['error']
                    )
            
            if isinstance(telemetry_data, dict) and 'error' in telemetry_data:
                raise HTTPException(
                    status_code=500,
                    detail=telemetry_data['error']
                )
            
            return telemetry_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{session_id}/attributes")
async def get_session_attributes(session_id: str, db: Session = Depends(get_db)):
    """Get all telemetry attributes for a session."""
    # Check if session exists
    session = db.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all attributes
    attributes = db.query(AttributeValue).filter(
        AttributeValue.session_id == session_id
    ).all()
    
    return {
        "session_id": session_id,
        "attribute_count": len(attributes),
        "attributes": [
            {
                "attribute": attr.attribute,
                "value_len": attr.value_len,
                "value_preview": attr.value[:100] + "..." if attr.value and len(attr.value) > 100 else attr.value
            }
            for attr in attributes
        ]
    }

@router.get("/{session_id}/attributes/{attribute_name}")
async def get_session_attribute(
    session_id: str,
    attribute_name: str,
    db: Session = Depends(get_db)
):
    """Get a specific telemetry attribute for a session."""
    attribute = db.query(AttributeValue).filter(
        AttributeValue.session_id == session_id,
        AttributeValue.attribute == attribute_name
    ).first()
    
    if not attribute:
        raise HTTPException(
            status_code=404,
            detail=f"Attribute '{attribute_name}' not found for session '{session_id}'"
        )
    
    return {
        "session_id": session_id,
        "attribute": attribute.attribute,
        "value": attribute.value,
        "value_len": attribute.value_len
    }
