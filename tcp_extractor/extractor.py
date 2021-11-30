import json
import logging
import os
import socket
import sys
import time
from threading import Event
from typing import Any, Optional

import psutil
from cognite.client import CogniteClient
from cognite.client.data_classes import DatapointsList, TimeSeries
from cognite.extractorutils.statestore import AbstractStateStore
from cognite.extractorutils.uploader import DataPointList, TimeSeriesUploadQueue

from tcp_extractor import lib
from tcp_extractor.config import Config

logger = logging.getLogger(__name__)


def run_extractor(cognite: CogniteClient, states: AbstractStateStore, config: Config, stop_event: Event) -> None:
    logger.info(" STARTING THE EXTRACTION ")

    data_set_id = lib.get_data_set_id(ext_id=config.tcp.data_set_ext_id, client=cognite)

    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", config.tcp.socket_port))
    s.listen()

    def default_time_series_factory(external_id: str, datapoints: DatapointsList) -> TimeSeries:
        """
        Default time series factory when new timeseries are ingested
        Args:
            external_id: External ID of time series to create
            datapoints: The list of datapoints that were tried to be inserted
        Returns:
            A TimeSeries object with external_id set
        """
        # global data_set_source_time_series_id

        return TimeSeries(external_id=external_id, name=external_id, is_string=False, data_set_id=data_set_id)

    logger.info(
        f"The live TCP extractor has started. Listening for connections on localhost port: {config.tcp.socket_port}"
    )
    upload_queue = TimeSeriesUploadQueue(
        cdf_client=cognite, max_upload_interval=config.tcp.upload_interval, create_missing=default_time_series_factory
    )
    upload_queue.start()
    logger.info("Upload queue started.")

    # Listening to socket port
    while not stop_event.is_set():
        clientsocket, address = s.accept()
        logger.info(f"Accepted connection from {address}")
        leftover = ""

        while not stop_event.is_set():
            msg = clientsocket.recv(config.tcp.max_bucket_size).decode("utf-8")

            if not msg:
                logger.info(f"{address}: Client disconnected")
                clientsocket.close()
                break

            try:
                result = lib.json_stich_partial_strings(new_string=msg, leftover=leftover)
            except:
                logger.info(
                    f"The function 'json_stich_partial_strings' failed.\n Old leftover: {leftover}\n Message: {msg}\n Exiting Script"
                )
                sys.exit(1)

            leftover = result.get("leftover")
            msg_list = result.get("datapoints_list")

            for i in range(0, len(msg_list)):
                try:
                    payload = json.loads(msg_list[i])
                    # print('Received payload')  #Keep commented out unless needed during testing
                except:
                    logger.error(f"Failed to load json")
                    logger.error(f"msg_list[{i}]: \n {msg_list[i]}")
                    logger.error(f"msg: \n {msg}")
                    sys.exit(1)
                for item in payload["items"]:
                    list_of_tuples = lib.dicts_to_tuples(item["datapoints"])
                    time_series_ext_id = config.tcp.time_series_prefix + item["externalid"].replace(" ", "_")
                    upload_queue.add_to_upload_queue(datapoints=list_of_tuples, external_id=time_series_ext_id)
            queue_length = upload_queue.__len__()
            script_memory_usage_MB = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)

            if queue_length > config.tcp.max_queue_length:
                upload_queue.stop(ensure_upload=False)
                upload_queue = TimeSeriesUploadQueue(
                    cdf_client=cognite,
                    max_upload_interval=config.tcp.upload_interval,
                    create_missing=default_time_series_factory,
                )
                upload_queue.start()
                logger.error(f"The length of the upload queue exceeded the limit. The queue has been reset.")
                logger.error(f"The queue length was {queue_length}. The limit is {config.tcp.max_queue_length}")
                logger.error(f"Current memory consumption is {script_memory_usage_MB} MB")

    upload_queue.stop()
