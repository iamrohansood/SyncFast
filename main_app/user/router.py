import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dotenv import dotenv_values
from ..database import get_db
from . import schemas, crud

environ = dotenv_values()


router = APIRouter()
stripe.api_key = environ.get('STRIPE_SECRET_KEY')
ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET')


@router.get("/", response_model=list[schemas.User])
def get_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * 10
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/get_user_by_email", response_model=schemas.User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)


@router.put("/{user_id}")
def update_user(user_id: str, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email.lower() != db_user.email.lower():
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    return crud.update_user(id=user_id, user=user)


@router.post("/webhook", include_in_schema=False, status_code=200)
async def webhook(request: Request, db: Session = Depends(get_db)):
    event = None
    sig_header = request.headers['stripe-signature']
    body = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            body, sig_header, ENDPOINT_SECRET
        )
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

    # Handle the event
    if event['type'] == 'customer.created':
        user = event['data']['object']
        return crud.create_user_webhook(user, db)
    elif event['type'] == 'customer.updated':
        user = event['data']['object']
        return crud.update_user_webhook(user, db)
    else:
        print('Unhandled event type {}'.format(event['type']))
        return {"msg": "Unhandled event type"}
