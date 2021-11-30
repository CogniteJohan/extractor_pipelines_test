from dataclasses import dataclass

from cognite.extractorutils.configtools import BaseConfig, StateStoreConfig


@dataclass
class ExtractorConfig:
    state_store: StateStoreConfig = StateStoreConfig()


@dataclass
class TcpConfig:
    socket_port: int
    max_bucket_size: int
    time_series_prefix: str
    upload_interval: int
    max_queue_length: int
    data_set_ext_id: str


@dataclass
class Config(BaseConfig):
    tcp: TcpConfig
    extractor: ExtractorConfig = ExtractorConfig()
