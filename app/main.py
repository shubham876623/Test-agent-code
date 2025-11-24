"""
FastAPI Main Application
AI Accounting Platform Backend
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.config import settings
from app.database import get_db, init_db
from app.models.user import User
from app.schemas.auth import (
    SignupRequest, LoginRequest, TokenResponse, 
    UserResponse, MessageResponse
)
from app.utils.security import (
    verify_password, get_password_hash, 
    create_access_token, create_refresh_token,
    verify_token
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered B2B accounting platform with QuickBooks integration",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# ============================================
# DEPENDENCIES
# ============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Usage in endpoints:
        current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )


# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User email address (must be unique)
    - **password**: Password (min 8 chars, must contain digit and uppercase)
    - **full_name**: User's full name
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        role="user"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"user_id": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"user_id": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT access token and refresh token
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token({"user_id": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"user_id": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Authorization header with Bearer token
    """
    return current_user


@app.post("/api/auth/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by deleting the token. This endpoint is for logging the action.
    """
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )


# ============================================
# STARTUP/SHUTDOWN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📝 Environment: {settings.APP_ENV}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")
    
    # Initialize database (creates tables if they don't exist)
    # Comment this out in production - use Alembic migrations instead
    if settings.DEBUG:
        try:
            init_db()
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Shutting down application")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
