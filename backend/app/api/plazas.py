from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..core.database import get_db
from ..models.user import User, UserType
from ..models.plaza import Plaza, ParkingArea
from ..api.schemas import (
    PlazaCreate, PlazaResponse, PlazaWithDetails,
    ParkingAreaCreate, ParkingAreaResponse, ParkingAreaWithSpots
)
from ..api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PlazaResponse)
async def create_plaza(
    plaza_data: PlazaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new plaza (plaza owners and admins only)."""
    if current_user.user_type not in [UserType.PLAZA_OWNER, UserType.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create plaza"
        )
    
    db_plaza = Plaza(
        name=plaza_data.name,
        address=plaza_data.address,
        coordinates=plaza_data.coordinates,
        owner_id=current_user.user_id
    )
    
    db.add(db_plaza)
    db.commit()
    db.refresh(db_plaza)
    
    return db_plaza


@router.get("/", response_model=List[PlazaResponse])
async def list_plazas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List plazas based on user type."""
    if current_user.user_type == UserType.ADMIN:
        # Admins can see all plazas
        plazas = db.query(Plaza).all()
    elif current_user.user_type == UserType.PLAZA_OWNER:
        # Plaza owners can see only their plazas
        plazas = db.query(Plaza).filter(Plaza.owner_id == current_user.user_id).all()
    else:
        # Consumers can see all plazas (for finding parking)
        plazas = db.query(Plaza).all()
    
    return plazas


@router.get("/{plaza_id}", response_model=PlazaWithDetails)
async def get_plaza(
    plaza_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get plaza details with parking areas and cameras."""
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
            detail="Not enough permissions to view this plaza"
        )
    
    return plaza


@router.put("/{plaza_id}", response_model=PlazaResponse)
async def update_plaza(
    plaza_id: UUID,
    plaza_data: PlazaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update plaza information."""
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
            detail="Not enough permissions to update this plaza"
        )
    
    plaza.name = plaza_data.name
    plaza.address = plaza_data.address
    plaza.coordinates = plaza_data.coordinates
    
    db.commit()
    db.refresh(plaza)
    
    return plaza


@router.delete("/{plaza_id}")
async def delete_plaza(
    plaza_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a plaza."""
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
            detail="Not enough permissions to delete this plaza"
        )
    
    db.delete(plaza)
    db.commit()
    
    return {"message": "Plaza deleted successfully"}


# Parking Areas endpoints
@router.post("/{plaza_id}/areas", response_model=ParkingAreaResponse)
async def create_parking_area(
    plaza_id: UUID,
    area_data: ParkingAreaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a parking area within a plaza."""
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
    
    db_area = ParkingArea(
        plaza_id=plaza_id,
        name=area_data.name,
        floor_level=area_data.floor_level,
        area_type=area_data.area_type
    )
    
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    
    return db_area


@router.get("/{plaza_id}/areas", response_model=List[ParkingAreaWithSpots])
async def list_parking_areas(
    plaza_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List parking areas in a plaza with their spots."""
    plaza = db.query(Plaza).filter(Plaza.plaza_id == plaza_id).first()
    if not plaza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plaza not found"
        )
    
    areas = db.query(ParkingArea).filter(ParkingArea.plaza_id == plaza_id).all()
    return areas 