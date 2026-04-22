# Development Guide

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (or any SQLModel supported database)
- Git
- pip or poetry

### Local Development Setup

#### 1. Clone and Setup Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd "AI Recruitment Fastapi"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
# - DATABASE_URL (PostgreSQL connection string)
# - SECRET_KEY (a secure random string, min 32 characters)
# - AWS credentials (for S3 file uploads)
# - OPENAI_API_KEY (for AI CV analysis)
```

#### 4. Initialize Database

```bash
# The database will be automatically initialized on first run
# Tables will be created based on SQLModel definitions
python -m uvicorn app.main:app --reload
```

### Running the Application

```bash
# Development mode (with auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

### Project Structure

```
app/
├── api/v1/              # API versioning support
├── config/              # Database configuration
├── core/                # Core utilities, security, settings
├── db/                  # Database session management
├── middleware/          # Middleware components
├── models/              # SQLModel database models
├── routes/              # API endpoints
├── schemas/             # Pydantic request/response models
└── services/            # Business logic layer
```

### Code Organization Principles

1. **Routes** - Handle HTTP requests/responses
2. **Schemas** - Define request/response validation
3. **Services** - Contain business logic
4. **Models** - Database models
5. **Core** - Shared utilities and configuration

### Adding New Features

#### Example: Adding a New Endpoint

1. **Create Schema** (schemas/new_feature.py):
```python
from pydantic import BaseModel, Field
from datetime import datetime

class NewFeatureCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class NewFeatureResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

2. **Create Model** (models/new_feature.py):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import uuid4

class NewFeature(SQLModel, table=True):
    __tablename__ = "new_features"
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

3. **Create Service** (services/new_feature.py):
```python
from sqlmodel import Session, select
from app.models.new_feature import NewFeature
from app.schemas.new_feature import NewFeatureCreate
from app.core.logger import get_logger

logger = get_logger(__name__)

def create_new_feature(
    session: Session,
    feature_data: NewFeatureCreate,
) -> NewFeature:
    """Create new feature"""
    try:
        new_feature = NewFeature(**feature_data.model_dump())
        session.add(new_feature)
        session.commit()
        session.refresh(new_feature)
        logger.info(f"Feature created: {new_feature.id}")
        return new_feature
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating feature: {str(e)}")
        raise
```

4. **Create Route** (routes/new_feature.py):
```python
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.new_feature import NewFeatureCreate, NewFeatureResponse
from app.services.new_feature import create_new_feature
from app.api.v1.dependencies import CurrentUser

new_feature_router = APIRouter(prefix="/features", tags=["Features"])

@new_feature_router.post(
    "/",
    response_model=NewFeatureResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feature(
    feature_data: NewFeatureCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Create a new feature"""
    feature = create_new_feature(session, feature_data)
    return feature
```

5. **Register Route** (main.py):
```python
from app.routes.new_feature import new_feature_router

app.include_router(
    new_feature_router,
    prefix=f"{API_V1_PREFIX}/features",
    tags=["Features"]
)
```

### API Conventions

#### Status Codes
- `200` - Successful GET/PUT request
- `201` - Successful POST request (resource created)
- `204` - No content response
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `409` - Conflict (resource exists)
- `500` - Server error

#### Response Format
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    "id": "123",
    "name": "Example"
  }
}
```

#### Error Response Format
```json
{
  "success": false,
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Database Migrations

For production, consider using Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new_feature table"

# Apply migration
alembic upgrade head
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Watch mode
pytest-watch
```

### Debugging

#### Enable Debug Logging
Add to main.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Use Python Debugger
```python
import pdb; pdb.set_trace()
```

#### View Application Logs
```bash
# Check app.log
tail -f logs/app.log

# Check error log
tail -f logs/errors.log
```

### Performance Optimization

1. **Database Indexing** - Add indexes to frequently queried fields
2. **Query Optimization** - Use select() with specific columns
3. **Caching** - Implement Redis caching for frequent queries
4. **Rate Limiting** - Use slowapi for rate limiting
5. **Pagination** - Always paginate list endpoints

### Security Best Practices

1. **Environment Variables** - Never commit .env file
2. **HTTPS** - Use HTTPS in production (set secure=True in cookies)
3. **CORS** - Configure specific origins in production
4. **Secrets** - Use AWS Secrets Manager or similar
5. **Input Validation** - Use Pydantic validators
6. **SQL Injection** - Use SQLModel/ORM (no raw SQL)

### Common Tasks

#### Add Logging
```python
from app.core.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")
logger.error("Error", exc_info=True)
```

#### Add Exception Handling
```python
from app.core.exceptions import NotFoundException

try:
    # code
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise NotFoundException(detail="Not found")
```

#### Get Current User
```python
from app.api.v1.dependencies import CurrentUser

def my_endpoint(current_user: CurrentUser):
    print(current_user.email)
```

### Troubleshooting

#### Database Connection Issues
```python
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:password@localhost:5432/database_name
```

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Token Expiration
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` in .env
- Token expires after configured minutes
- User needs to login again after expiration

### Contributing

1. Create a feature branch
2. Make changes following the established patterns
3. Test your changes
4. Write clear commit messages
5. Create a pull request

### Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)
