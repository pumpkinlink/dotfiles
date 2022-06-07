from dataclasses import dataclass
import os
from typing import Sequence

app_key = os.environ.get(
    'omie_app_key')
app_secret = os.environ.get(
    'omie_app_secret')


@dataclass
class OmieRequestBody:
    call: str = None
    app_key: str = app_key
    app_secret: str = app_secret
    param: Sequence | None = None
