import time
import urllib.parse
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from dataclasses import dataclass
from requests.models import PreparedRequest
from typing import Mapping, Any
from typing import Optional
from typing import Union

from source_binance.utils import get_signature


@dataclass
class BinanceAuthenticator(NoAuth):
    """Binance authenticator"""
    config: Config
    api_key: Union[InterpolatedString, str]
    api_secret: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._api_key = InterpolatedString.create(self.api_key, parameters=parameters).eval(self.config)
        self._api_secret = InterpolatedString.create(self.api_secret, parameters=parameters).eval(self.config)

    def __call__(self, request: PreparedRequest):
        timestamp = int(time.time() * 1000)

        [dry_url, query_string] = urllib.parse.splitquery(request.url)
        params = urllib.parse.parse_qs(query_string)
        params["timestamp"] = timestamp
        payload = get_signature(self._api_secret, params)
        params["signature"] = payload

        request.prepare_url(dry_url, params)

        request.headers.update({

            "X-MBX-APIKEY": self._api_key,
        })

        return request


@dataclass
class DefaultTransform(RecordTransformation):
    """
    Default transformation that does not change anything.
    """

    def transform(
            self,
            record: Record,
            config: Optional[Config] = None,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
        return transformer.transform(record)

    def __eq__(self, other):
        return other.__dict__ == self.__dict__
