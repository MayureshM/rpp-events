from aws_lambda_powertools.utilities.parser import (
    BaseModel,
    parse,
)
from typing import Literal, Dict, Union
# from typing_extensions import Literal


class TaskEventModel(BaseModel):
    href: str
    work_order_key: str
    site_id: str
    work_order_number: str
    work_order_key: str
    dealer_number: int

    class Config:
        extra = "allow"


class LaborModel(BaseModel):
    labor_name: str
    labor_time: str
    site_id: str

    class Config:
        extra = "allow"


class PartLaborModel(BaseModel):
    ip_part_status: str
    part_name: str
    site_id: str

    class Config:
        extra = "allow"


class DynamoDBStreamChangedRecordModel(BaseModel):
    Keys: Dict
    NewImage: Union[LaborModel, PartLaborModel, None]

    class Config:
        extra = "allow"


class DynamoDBStreamRecordModel(BaseModel):
    eventName: Literal["INSERT", "MODIFY", "REMOVE"]
    dynamodb: DynamoDBStreamChangedRecordModel


def validate_event_detail(event, envelope):
    return parse(model=TaskEventModel, envelope=envelope, event=event)


def validate_eb_event(event, envelope):
    return parse(model=DynamoDBStreamRecordModel, envelope=envelope, event=event)
