from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.subscription import SubscriptionCreate
from app.services.subscription import process_upgrade 
from app.core.security import verify_token

subscription_router = APIRouter(prefix="/subscription", tags=["Subscriptions"])

@subscription_router.post("/upgrade")
async def upgrade_subscription(
    sub_data: SubscriptionCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(verify_token)
):
    new_sub = process_upgrade(session, current_user, sub_data)

    return {
        "message": f"Successfully upgraded to {sub_data.package}",
        "expires_at": new_sub.end_date,
        "subscription_id": new_sub.id
    }