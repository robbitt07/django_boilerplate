#!/usr/bin/env python
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

import json
import logging
import pika
from pika.exceptions import ConnectionClosed, NoFreeChannels
import time

logger = logging.getLogger('service')

MAX_FAIL = 2


class QueueConnection(object):
    def __init__(self, queues: list = settings.RABBITMQ_QUEUES):
        self.host = settings.RABBITMQ_HOST
        self.virtual_host = settings.RABBITMQ_VHOST
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASS
        self.queues = queues
        self.connection = None

    def _establish_connection(self, initial=False, wait=True):
        if initial:
            logger.info(f'Establishing connection with RabbitMQ host: {self.host}', extra={'task': 'QueueConnection'})

        if self.connection is not None:
            try:
                self.connection.close()
            except:
                pass

        if wait:
            time.sleep(2)

        #TODO: Add logging on failure
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, virtual_host=self.virtual_host, credentials=self.credentials,
                connection_attempts=10, heartbeat=1200
            )
        )
        self.channel = self.connection.channel()
        for queue in self.queues:
            self.channel.queue_declare(queue=queue, durable=True)

    def get_channel(self):
        try:
            if not self.connection or self.connection.is_closed:
                logger.warn(
                    f'Re-establishing connection with RabbitMQ host: {self.host}',
                    extra={'task': 'QueueConnection'}
                )
                self._establish_connection()
            return self.connection.channel()
        except ConnectionClosed:
            time.sleep(1)
            logger.warn(
                f'Re-establishing connection with RabbitMQ host: {self.host}',
                extra={'task': 'QueueConnection'}
            )
            self._establish_connection()
            return self.connection.channel()

        except NoFreeChannels:
            time.sleep(1)
            logger.warn(
                f'Re-establishing connection with RabbitMQ host: {self.host}',
                extra={'task': 'QueueConnection'}
            )
            self._establish_connection()
            return self.connection.channel()

    def _send_message(self, queue: str, message: str) -> bool:
        # Establish Connection
        credentials = pika.PlainCredentials(self.user, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, virtual_host=self.virtual_host, credentials=credentials,
                connection_attempts=10, heartbeat=1200
            )
        )
        channel = connection.channel()
        # Declare Queue
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange='', 
            routing_key=queue, 
            body=message,
            properties=pika.BasicProperties(
                delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
        ))
        connection.close()

    def publish(self, queue: str, message: str, fail_count: int = 0) -> bool:
        try:
            # Send Message
            self._send_message(queue=queue, message=message)
            logger.info(
                f'Queue=`{queue}` Submitted message: {message[0:100]}',
                extra={'task': 'QueueConnection'}
            )
            return True
        except Exception as e:
            logger.error(
                'Failed to publish message', exc_info=True,
                extra={'task': 'QueueConnection'}
            )
            if fail_count >= MAX_FAIL:
                raise e
            # Increment Fail Count
            fail_count += 1
            self.publish(queue=queue, message=message, fail_count=fail_count)
            return False

    def consume(self, callback, queue: str = 'default'):
        self._establish_connection(initial=True, wait=False)
        channel = self.get_channel()
        channel.basic_qos(prefetch_count=1)
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_consume(queue=queue, on_message_callback=callback)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()

        self.connection.close()

    def queue_declare(self, queue: str) -> bool:
        # Establish Connection
        credentials = pika.PlainCredentials(self.user, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, virtual_host=self.virtual_host, credentials=credentials,
                connection_attempts=10, heartbeat=1200
            )
        )
        channel = connection.channel()
        # Declare Queue
        channel.queue_declare(queue=queue, durable=True)


QUEUE_CONNECTION = QueueConnection()


def publish_task(task: str,
                 params: dict,
                 queue: str = 'default',
                 connection: QueueConnection = QUEUE_CONNECTION) -> bool:
    # Build Message
    message = json.dumps({
        "task": task, "params": params}, cls=DjangoJSONEncoder
    )

    # Publish Message
    return connection.publish(queue=queue, message=message)
