"""
Subscription Routes
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.services.subscription import (
    process_subscription_upgrade,
    get_active_subscription,
    check_subscription_validity,
)
from app.api.v1.dependencies import CurrentUser
from app.core.logger import get_logger

logger = get_logger(__name__)

subscription_router = APIRouter(tags=["Subscriptions"])


@subscription_router.post(
    "/upgrade",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upgrade subscription",
    description="Upgrade company subscription to a higher tier"
)
def upgrade_subscription(
    sub_data: SubscriptionCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Upgrade company subscription"""
    new_sub = process_subscription_upgrade(session, current_user.id, sub_data)
    
    logger.info(f"Subscription upgraded for user {current_user.id} to {sub_data.package}")
    
    return SubscriptionResponse.model_validate(new_sub)


@subscription_router.get(
    "/current",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current subscription",
    description="Get current active subscription for user's company"
)
def get_current_subscription(
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Get current active subscription"""
    if not current_user.company_id:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(detail="User's company not found")
    
    subscription = get_active_subscription(session, current_user.company_id)
    
    if not subscription:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(detail="No active subscription found")
    
    logger.info(f"Retrieved subscription for user {current_user.id}")
    return SubscriptionResponse.model_validate(subscription)


@subscription_router.get(
    "/check",
    status_code=status.HTTP_200_OK,
    summary="Check subscription validity",
    description="Check if company has a valid subscription"
)
def check_subscription(
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Check if subscription is valid"""
    if not current_user.company_id:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(detail="User's company not found")
    
    is_valid, subscription = check_subscription_validity(session, current_user.company_id)
    
    logger.info(
        f"Checked subscription validity for user {current_user.id}: {is_valid}"
    )
    
    return {
        "is_valid": is_valid,
        "subscription": SubscriptionResponse.model_validate(subscription) if subscription else None,
    }
