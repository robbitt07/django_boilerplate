import argparse
from decouple import config
import pika
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--vhost", type=str, required=True, help="Vhost")
args = parser.parse_args()


def rest_queue_list(user=config("RABBITMQ_USER"),
                    password=config("RABBITMQ_PASS"),
                    host=config("RABBITMQ_HOST"),
                    port=config("RABBITMQ_ADMIN_PORT"),
                    virtual_host=None):
    url = "http://%s:%s/api/queues/%s" % (host, port, virtual_host or "")
    response = requests.get(url, auth=(user, password))
    queues = [q["name"] for q in response.json() if q["vhost"] == args.vhost]
    return queues


if __name__ == "__main__":
    credentials = pika.PlainCredentials(config("RABBITMQ_USER"), config("RABBITMQ_PASS"))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config("RABBITMQ_HOST"),
            port=config("RABBITMQ_PORT"),
            virtual_host=args.vhost,
            credentials=credentials
        )
    )
    channel = connection.channel()

    queues = rest_queue_list(virtual_host=args.vhost)
    for queue in queues:
        try:
            channel.queue_purge(queue)
        except Exception as e:
            print(str(e))