import stripe
import json
from confluent_kafka import Consumer
from dotenv import dotenv_values

environ = dotenv_values()


conf = {"bootstrap.servers": "localhost:9092", "group.id": "kafka-consumer"}
stripe.api_key = environ.get("STRIPE_SECRET_KEY")

consumer = Consumer(conf)
consumer.subscribe(["create-user-on-stripe"])


def create_user(data: dict):
    stripe.Customer.create(email=data["email"], name=data["name"])
    print({"status": "success", "msg": "Created User"})


try:
    while True:
        msg = consumer.poll(1)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        data = json.loads(msg.value().decode("utf-8"))
        create_user(data)
except Exception as e:
    print({"status": "consumer-create-user-error", "message": str(e)})
finally:
    consumer.close()
