from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.subscription import Subscription
from app.models.user import Company
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate

def process_upgrade(session: Session, user_id: str, sub_data: SubscriptionCreate):
    user = session.get(User, user_id)
    if not user or not user.company_id:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    statement = (
        select(Subscription)
        .where(Subscription.company_id == user.company_id)
        .where(Subscription.is_active == True)
    )
    old_subs = session.exec(statement).all()
    for old in old_subs:
        old.is_active = False
        session.add(old)

    new_sub = Subscription(
        company_id=user.company_id,
        package=sub_data.package,
        amount_paid=sub_data.amount_paid,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )

    session.add(new_sub)
    company = session.get(Company, user.company_id)
    if company:
        company.package = sub_data.package
        session.add(company)

    session.commit()
    session.refresh(new_sub)
    
    return new_sub