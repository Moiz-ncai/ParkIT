# ParkIT Platform Backend

FastAPI-based backend server for the ParkIT Platform, providing REST APIs for plaza management, parking spot monitoring, and real-time vehicle detection integration.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core configuration and utilities
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection and session management
│   │   └── auth.py          # Authentication utilities (JWT, password hashing)
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py          # User model and types
│   │   ├── plaza.py         # Plaza, ParkingArea, ParkingSpot, Camera models
│   │   ├── occupancy.py     # SpotOccupancyHistory model
│   │   └── reservation.py   # Reservation model
│   └── api/                 # API route handlers
│       ├── schemas.py       # Pydantic request/response schemas
│       ├── auth.py          # Authentication endpoints
│       ├── plazas.py        # Plaza management endpoints
│       ├── spots.py         # Parking spot management endpoints
│       └── cameras.py       # Camera management endpoints
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── run_backend.py          # Server startup script
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE parkit_platform;
CREATE USER parkit_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE parkit_platform TO parkit_user;
```

### 3. Environment Configuration

Copy the environment template and configure:

```bash
cp env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://parkit_user:your_password@localhost:5432/parkit_platform
SECRET_KEY=your-super-secret-key-here
```

### 4. Start the Server

```bash
python run_backend.py
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API**: http://localhost:8000/api/v1/
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/users` - List users (admin only)

### Plaza Management

- `POST /api/v1/plazas/` - Create plaza
- `GET /api/v1/plazas/` - List plazas
- `GET /api/v1/plazas/{id}` - Get plaza details
- `PUT /api/v1/plazas/{id}` - Update plaza
- `DELETE /api/v1/plazas/{id}` - Delete plaza
- `POST /api/v1/plazas/{id}/areas` - Create parking area
- `GET /api/v1/plazas/{id}/areas` - List parking areas

### Parking Spots

- `POST /api/v1/spots/areas/{area_id}/spots` - Create parking spot
- `GET /api/v1/spots/areas/{area_id}/spots` - List spots in area
- `GET /api/v1/spots/{spot_id}` - Get spot details
- `PUT /api/v1/spots/{spot_id}` - Update spot
- `DELETE /api/v1/spots/{spot_id}` - Delete spot
- `POST /api/v1/spots/occupancy` - Record occupancy change
- `GET /api/v1/spots/{spot_id}/occupancy` - Get occupancy history
- `GET /api/v1/spots/plaza/{plaza_id}/availability` - Get plaza availability

### Camera Management

- `POST /api/v1/cameras/plazas/{plaza_id}/cameras` - Create camera
- `GET /api/v1/cameras/plazas/{plaza_id}/cameras` - List cameras
- `GET /api/v1/cameras/{camera_id}` - Get camera details
- `PUT /api/v1/cameras/{camera_id}` - Update camera
- `DELETE /api/v1/cameras/{camera_id}` - Delete camera
- `PATCH /api/v1/cameras/{camera_id}/status` - Update camera status

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### User Types

- `admin` - Full system access
- `plaza_owner` - Manage owned plazas
- `plaza_staff` - Monitor plaza status
- `consumer` - Search and reserve parking

## 🗄️ Database Models

### Users
- User management with role-based access control
- Encrypted password storage
- Profile data support

### Plazas
- Plaza information and ownership
- Geographic coordinates
- Multiple parking areas per plaza

### Parking Areas
- Organized sections within plazas
- Floor-level support
- Area types (outdoor, covered, underground)

### Parking Spots
- Individual parking spaces
- Polygon coordinate storage for precise mapping
- Status tracking (available, occupied, reserved, maintenance)
- Vehicle type detection integration

### Cameras
- RTSP stream configuration
- Coverage area mapping
- Status monitoring

### Occupancy History
- Real-time parking status changes
- Vehicle detection confidence scores
- Historical analytics data

### Reservations
- User parking reservations
- Time-based booking system
- Status management

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/parkit_platform` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-this-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://localhost:8080` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `DEBUG` | Debug mode | `true` |

## 🧪 Testing

Run the interactive API documentation:

```bash
# Start the server
python run_backend.py

# Open browser to http://localhost:8000/docs
```

### Sample API Calls

1. **Register a plaza owner:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@plaza.com",
    "password": "secure123",
    "user_type": "plaza_owner"
  }'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@plaza.com",
    "password": "secure123"
  }'
```

3. **Create a plaza:**
```bash
curl -X POST "http://localhost:8000/api/v1/plazas/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Plaza",
    "address": "123 Main St, City, State",
    "coordinates": {"lat": 40.7128, "lng": -74.0060}
  }'
```

## 🚀 Production Deployment

### Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY run_backend.py .

EXPOSE 8000
CMD ["python", "run_backend.py"]
```

### Environment Variables for Production

- Set strong `SECRET_KEY`
- Use production database
- Set `DEBUG=false`
- Configure proper CORS origins
- Use Redis for caching

## 🔄 Integration with Detection Service

The backend is designed to integrate with the vehicle detection service:

1. **Detection service** processes camera feeds
2. **Posts occupancy updates** to `/api/v1/spots/occupancy`
3. **Real-time status** reflected in database
4. **Availability API** provides current plaza status

## 📈 Next Steps

1. **Set up PostgreSQL database**
2. **Install dependencies** and configure environment
3. **Start the backend server**
4. **Test API endpoints** using Swagger UI
5. **Integrate with vehicle detection service**
6. **Build frontend applications**

## 🤝 Contributing

1. Follow FastAPI best practices
2. Add type hints to all functions
3. Write API documentation in docstrings
4. Test endpoints using Swagger UI
5. Maintain database migrations

---

**ParkIT Platform Backend v1.0** - Built with FastAPI, SQLAlchemy, and PostgreSQL 