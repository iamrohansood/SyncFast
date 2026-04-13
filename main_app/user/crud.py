from sqlalchemy.orm import Session
import json
from confluent_kafka import Producer
from . import models, schemas


producer_conf = {"bootstrap.servers": "localhost:9092", "client.id": "fastapi-kafka-api"}

producer = Producer(producer_conf)


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(user: schemas.UserCreate):
    produce_create_user(dict(user))
    return "User created"


def update_user(id, user: schemas.UserCreate):
    data = dict(user)
    data["id"] = id
    produce_update_user(data)
    return "User updated"


# Handle stripe webhooks
def create_user_webhook(data: dict, db: Session):
    db_user = models.User(id=data["id"], email=data["email"], name=data["name"])
    db.add(db_user)
    db.commit()
    return


def update_user_webhook(data: dict, db: Session):
    db_user = db.query(models.User).filter(models.User.id == data["id"]).first()
    db_user.email = data["email"]
    db_user.name = data["name"]
    db.commit()
    return


# Helper function
def produce_create_user(data: dict):
    try:
        data = json.dumps(data).encode("utf-8")
        producer.produce("create-user-on-stripe", value=data)
        producer.flush()
        print({"status": "success", "create-user": data})
    except Exception as e:
        print({"status": "error", "message": str(e)})


def produce_update_user(data: dict):
    try:
        data = json.dumps(data).encode("utf-8")
        producer.produce("update-user-on-stripe", value=data)
        producer.flush()
        print({"status": "success", "update-user": data})
    except Exception as e:
        print({"status": "error", "message": str(e)})
