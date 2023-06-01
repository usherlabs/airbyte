import datetime
import urllib.parse
from dataclasses import InitVar
from dataclasses import dataclass
from typing import Mapping, Any
from typing import Optional
from typing import Union

import time
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.models import PreparedRequest

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
class CastingTransform(RecordTransformation):
    """
    Default transformation that does not change anything.
    """
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.name = parameters.get("name")

    def transform(
            self,
            record: Record,
            config: Optional[Config] = None,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
        schema = self._get_schema_root_properties()

        return transformer.transform(record, schema)

    def _get_schema_root_properties(self):
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()
        return schema

    def __eq__(self, other):
        return other.__dict__ == self.__dict__


@dataclass
class CustomDatetimeIncrementalSync(DatetimeBasedCursor):
    def parse_date(self, date: str) -> datetime.datetime:
        # if date time format is %s and have more than 10 digits, then it is in milisseconds
        if self.datetime_format == "%s" and len(str(date)) > 10:
            date_in_seconds = int(date) / 1000
            return self._parser.parse(date_in_seconds, self.datetime_format)

        return self._parser.parse(date, self.datetime_format)
