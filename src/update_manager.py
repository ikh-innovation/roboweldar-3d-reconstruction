from src.type_definitions import MilliSeconds


class UpdateManager:
    def __init__(self, update_interval: MilliSeconds):
        raise NotImplementedError

    def scan_logs(self):
        raise NotImplementedError

    def prepare_requests(self):
        raise NotImplementedError

    def batch_send_requests(self):
        raise NotImplementedError

    def run(self):
        while condition:
            # collect logs, see which statuses have changed (check diff) and post updates using the
    #           pyfiware REST interface and the data model that was agreed upon


