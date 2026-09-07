from celery_app import celery_app
import time

@celery_app.task
def notify_item_created(item_id: int, item_name: str):
    time.sleep(10)
    print(f"Notification: item {item_id} {item_name} was created")
