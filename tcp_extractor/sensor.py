import json
import random
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 10110))


while True:
    timestamp = time.time()
    payload = {
        "items": [
            {
                "externalid": "randon_floats3",
                "datapoints": [{"timestamp": timestamp, "value": random.uniform(0.5, 30)}],
            },
            {"externalid": "random_floats4", "datapoints": [{"timestamp": timestamp, "value": random.uniform(0.2, 9)}]},
        ]
    }
    msg = json.dumps(payload)
    print(msg)
    s.send(bytes(msg + "\r\n", encoding="utf-8"))
    time.sleep(0.5)
