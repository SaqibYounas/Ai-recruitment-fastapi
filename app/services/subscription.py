"""
Subscription Services
"""
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional

from app.models.subscription import Subscription
from app.models.user import Company, User
from app.schemas.subscription import SubscriptionCreate
from app.core.logger import get_logger
from app.core.exceptions import NotFoundException

logger = get_logger(__name__)


def process_subscription_upgrade(
    session: Session,
    user_id: str,
    sub_data: SubscriptionCreate,
) -> Subscription:
    """
    Process subscription upgrade for user's company
    
    Args:
        session: Database session
        user_id: User ID
        sub_data: Subscription data
        
    Returns:
        Created subscription object
        
    Raises:
        NotFoundException: If company not found for user
    """
    # Get user
    user = session.get(User, user_id)
    if not user or not user.company_id:
        logger.error(f"Company not found for user {user_id}")
        raise NotFoundException(detail="Company not found for this user")
    
    try:
        # Deactivate old subscriptions
        statement = (
            select(Subscription)
            .where(Subscription.company_id == user.company_id)
            .where(Subscription.is_active == True)
        )
        old_subs = session.exec(statement).all()
        
        for old_sub in old_subs:
            old_sub.is_active = False
            session.add(old_sub)
            logger.info(f"Deactivated subscription {old_sub.id}")
        
        # Create new subscription
        new_sub = Subscription(
            company_id=user.company_id,
            package=sub_data.package,
            amount_paid=sub_data.amount_paid,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
        )
        
        session.add(new_sub)
        
        # Update company package
        company = session.get(Company, user.company_id)
        if company:
            company.package = sub_data.package
            session.add(company)
            logger.info(f"Updated company {company.id} package to {sub_data.package}")
        
        session.commit()
        session.refresh(new_sub)
        
        logger.info(f"Subscription upgraded: {new_sub.id} to {sub_data.package}")
        return new_sub
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing subscription upgrade: {str(e)}")
        raise


def get_active_subscription(
    session: Session,
    company_id: str,
) -> Optional[Subscription]:
    """
    Get active subscription for company
    
    Args:
        session: Database session
        company_id: Company ID
        
    Returns:
        Active subscription or None
    """
    statement = (
        select(Subscription)
        .where(Subscription.company_id == company_id)
        .where(Subscription.is_active == True)
        .order_by(Subscription.end_date.desc())
    )
    
    subscription = session.exec(statement).first()
    return subscription


def check_subscription_validity(
    session: Session,
    company_id: str,
) -> tuple[bool, Optional[Subscription]]:
    """
    Check if company has valid subscription
    
    Args:
        session: Database session
        company_id: Company ID
        
    Returns:
        Tuple of (is_valid, subscription)
    """
    subscription = get_active_subscription(session, company_id)
    
    if not subscription:
        return False, None
    
    if subscription.end_date < datetime.utcnow():
        logger.warning(f"Subscription {subscription.id} has expired")
        subscription.is_active = False
        session.add(subscription)
        session.commit()
        return False, None
    
    return True, subscription
