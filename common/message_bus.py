import json

from azure.servicebus import ServiceBusClient, ServiceBusMessage

from common.config import SB_LISTEN_CONNECTION_STRING, SB_QUEUE_NAME, SB_SEND_CONNECTION_STRING


def publish_message(body: dict) -> None:
    """Send a JSON message to the Service Bus queue (uses send key)."""
    with ServiceBusClient.from_connection_string(SB_SEND_CONNECTION_STRING) as client:
        with client.get_queue_sender(SB_QUEUE_NAME) as sender:
            sender.send_messages(ServiceBusMessage(json.dumps(body)))


def receive_messages(max_wait_time: int = 5) -> list[dict]:
    """Receive and complete all available messages (uses listen key)."""
    messages = []
    with ServiceBusClient.from_connection_string(SB_LISTEN_CONNECTION_STRING) as client:
        with client.get_queue_receiver(SB_QUEUE_NAME, max_wait_time=max_wait_time) as receiver:
            for msg in receiver:
                messages.append(json.loads(str(msg)))
                receiver.complete_message(msg)
    return messages
