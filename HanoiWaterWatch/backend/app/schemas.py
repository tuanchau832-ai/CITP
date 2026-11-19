from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class Reading(Strict):
    v: Optional[float]=Field(strict=True)
    u: str
    q: Literal['ok','fault']
    raw: Optional[int]=Field(default=None,ge=0,le=4095,strict=True)
    gen: Literal['input','profile']
    fr: Optional[Literal['injected','disconnected','out_of_range']]=None
    @model_validator(mode='after')
    def fault(self):
        if (self.q=='fault') != (self.v is None) or (self.q=='fault' and self.fr is None): raise ValueError('fault requires null value and reason')
        return self
class Frame(Strict):
    seq: int=Field(ge=0,le=2147483647,strict=True)
    measured_at: Optional[datetime]
    time_source: Literal['ntp','server','uptime']
    uptime_ms: int=Field(ge=0,strict=True)
    buffered: bool=Field(strict=True)
    mode: Literal['manual','gradual_ph','spike_turb','do_drop']
    readings: dict[str,Reading]=Field(min_length=1)
    @model_validator(mode='after')
    def clock(self):
        if self.time_source=='uptime' and self.measured_at is not None: raise ValueError('uptime requires null timestamp')
        if self.time_source!='uptime' and (self.measured_at is None or self.measured_at.utcoffset() is None or self.measured_at.utcoffset().total_seconds()!=0): raise ValueError('UTC measured_at required')
        return self
class Diag(Strict):
    buffer_depth: int=Field(default=0,ge=0,strict=True)
    dropped_frames: int=Field(default=0,ge=0,strict=True)
    rejected_batches: int=Field(default=0,ge=0,strict=True)
    wifi_rssi: Optional[int]=Field(default=None,strict=True)
class Batch(Strict):
    schema_version: Literal['hww.frames.v1']=Field(alias='schema')
    station_code: str=Field(pattern=r'^HWW-[A-Z]{3}-\d{3}$')
    device_code: str
    boot_id: str=Field(pattern=r'^[0-9a-f]{8}$')
    fw_version: str=Field(max_length=100)
    sent_at: Optional[datetime]
    sent_uptime_ms: int=Field(ge=0,strict=True)
    diag: Diag
    frames: list[Frame]=Field(min_length=1,max_length=50)
    @model_validator(mode='after')
    def uptime(self):
        if any(f.uptime_ms>self.sent_uptime_ms for f in self.frames): raise ValueError('frame uptime exceeds sent uptime')
        if self.sent_at is not None and (self.sent_at.utcoffset() is None or self.sent_at.utcoffset().total_seconds()!=0): raise ValueError('UTC sent_at required')
        return self
