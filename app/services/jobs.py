# from sqlmodel import Session, select
# from app.models.job import Job, JobCreate
# from app.models.auth import User

# def create_new_job(job_data: JobCreate, session: Session, current_user: User):
#     db_job = Job(**job_data.model_dump(), user_id=current_user.id)
#     session.add(db_job)
#     session.commit()
#     session.refresh(db_job)
#     return db_job

# def get_all_jobs(session: Session):
#     return session.exec(select(Job)).all()


    