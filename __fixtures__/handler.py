import logging


def handler(data: dict, log: logging.Logger):
    data["new_filed"] = "new_value"
    log.info(data)
    return data
