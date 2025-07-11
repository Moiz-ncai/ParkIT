from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..core.database import get_db
from ..models.user import User, UserType
from ..models.plaza import Camera, Plaza
from ..api.schemas import CameraCreate, CameraResponse
from ..api.auth import get_current_user

router = APIRouter()


@router.post("/plazas/{plaza_id}/cameras", response_model=CameraResponse)
async def create_camera(
    plaza_id: UUID,
    camera_data: CameraCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new camera for a plaza."""
    # Verify plaza exists and user has permission
    plaza = db.query(Plaza).filter(Plaza.plaza_id == plaza_id).first()
    if not plaza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plaza not found"
        )
    
    # Check permissions
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this plaza"
        )
    
    # Check if camera name already exists in this plaza
    existing_camera = db.query(Camera).filter(
        Camera.plaza_id == plaza_id,
        Camera.name == camera_data.name
    ).first()
    if existing_camera:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera name already exists in this plaza"
        )
    
    db_camera = Camera(
        plaza_id=plaza_id,
        name=camera_data.name,
        rtsp_url=camera_data.rtsp_url,
        position_coordinates=camera_data.position_coordinates,
        coverage_area=camera_data.coverage_area
    )
    
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    return db_camera


@router.get("/plazas/{plaza_id}/cameras", response_model=List[CameraResponse])
async def list_cameras(
    plaza_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all cameras in a plaza."""
    # Verify plaza exists
    plaza = db.query(Plaza).filter(Plaza.plaza_id == plaza_id).first()
    if not plaza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plaza not found"
        )
    
    cameras = db.query(Camera).filter(Camera.plaza_id == plaza_id).all()
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific camera."""
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    camera_data: CameraCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a camera."""
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Check permissions
    plaza = db.query(Plaza).filter(Plaza.plaza_id == camera.plaza_id).first()
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this camera"
        )
    
    # Update camera fields
    camera.name = camera_data.name
    camera.rtsp_url = camera_data.rtsp_url
    camera.position_coordinates = camera_data.position_coordinates
    camera.coverage_area = camera_data.coverage_area
    
    db.commit()
    db.refresh(camera)
    
    return camera


@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a camera."""
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Check permissions
    plaza = db.query(Plaza).filter(Plaza.plaza_id == camera.plaza_id).first()
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this camera"
        )
    
    db.delete(camera)
    db.commit()
    
    return {"message": "Camera deleted successfully"}


@router.patch("/{camera_id}/status")
async def update_camera_status(
    camera_id: UUID,
    status: str,  # active, inactive, maintenance
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update camera status."""
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Check permissions
    plaza = db.query(Plaza).filter(Plaza.plaza_id == camera.plaza_id).first()
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this camera"
        )
    
    # Validate status
    valid_statuses = ["active", "inactive", "maintenance"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    camera.status = status
    db.commit()
    db.refresh(camera)
    
    return {"message": f"Camera status updated to {status}", "camera": camera} 