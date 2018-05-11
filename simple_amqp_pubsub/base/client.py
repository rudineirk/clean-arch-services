from typing import Any

from simple_amqp_pubsub.data import Event


class PubSubClient:
    def __init__(self, pubsub: 'BasePubSub', service: str):
        self.pubsub = pubsub
        self.service = service

        self.events_cache = {}

    def push(self, event: str, payload: Any):
        return self.pubsub.push(Event(
            service=self.service,
            event=event,
            payload=payload,
        ))

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass

        try:
            return self.events_cache[name]
        except KeyError:
            pass

        def publisher(payload):
            event = Event(
                service=self.service,
                event=name,
                payload=payload,
            )
            return self.pubsub.push(event)

        self.events_cache[name] = publisher
        return publisher
