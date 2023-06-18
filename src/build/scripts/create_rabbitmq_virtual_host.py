from decouple import config

import argparse
import requests


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vhost", type=str, required=True, help="Vhost")
    args = parser.parse_args()

    # Local Config
    host = config("RABBITMQ_HOST")
    port = config("RABBITMQ_ADMIN_PORT")
    user = config("RABBITMQ_USER")
    password = config("RABBITMQ_PASS")
    url = "http://%s:%s/api/vhosts/%s" % (host, port, args.vhost)
    response = requests.put(url, auth=(user, password))
    if response.status_code == 201:
        print(f"Virtual Host `{args.vhost}` created")
    elif response.status_code == 204:
        print(f"Virtual Host `{args.vhost}` already exists")
    else:
        print(f"Error Creating Virtual Host `{args.vhost}`: {response.reason}")
