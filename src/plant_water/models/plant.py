import logging

from typing import Optional
from datetime import datetime, timedelta

class Plant:
    def __init__(self,
                 name: str,
                 common_name: str,
                 species_name: str,
                 planted_on: datetime,
                 last_watered: Optional[datetime] = None,
                 moisture_level: Optional[int] = None):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.common_name = common_name
        self.species_name = species_name
        self.planted_on = planted_on
        self.last_watered = last_watered
        self.moisture_level = moisture_level

    @property
    def time_since_watered(self) -> timedelta:
        if self.last_watered:
            return datetime.now() - self.last_watered
        return datetime.now() - self.planted_on