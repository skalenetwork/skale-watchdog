from websocket import create_connection
import json
from datetime import datetime


def request_ima_healthcheck(endpoint):
    ws = create_connection(endpoint, timeout=5)
    ws.send('{ "id": 1, "method": "get_last_transfer_errors"}')
    result = ws.recv()
    print("Received '%s'" % result)
    print(type(result))
    errs_json = json.loads(result)
    errs = errs_json['last_transfer_errors']
    print(f'Num = {len(errs)} >>> ERS={errs}')
    for err in errs:
        print(datetime.utcfromtimestamp(err['ts']))
    ws.close()
    return errs


