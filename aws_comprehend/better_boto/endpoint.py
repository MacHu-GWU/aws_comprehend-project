# -*- coding: utf-8 -*-

"""
The data model for Comprehend real-time inference endpoint.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime

from iterproxy import IterProxy
from boto_session_manager import BotoSesManager


class EndpointStatusEnum(str, enum.Enum):
    CREATING = "CREATING"
    DELETING = "DELETING"
    FAILED = "FAILED"
    IN_SERVICE = "IN_SERVICE"
    UPDATING = "UPDATING"


@dataclasses.dataclass
class Endpoint:
    """
    :param arn: example, arn:aws:comprehend:us-east-1:669508176277:document-classifier-endpoint/tax-document-classifier-v000001
    """

    arn: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    failed_reason: T.Optional[str] = dataclasses.field(default=None)
    model_arn: T.Optional[str] = dataclasses.field(default=None)
    inference_unites: T.Optional[int] = dataclasses.field(default=None)
    data_access_role_arn: T.Optional[str] = dataclasses.field(default=None)
    desired_model_arn: T.Optional[str] = dataclasses.field(default=None)
    desired_inference_units: T.Optional[int] = dataclasses.field(default=None)
    desired_data_access_role_arn: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    update_time: T.Optional[datetime] = dataclasses.field(default=None)

    @classmethod
    def from_describe_endpoint_response(cls, data: dict) -> "Endpoint":
        """
        Ref:

        - describe_endpoint: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_endpoint
        """
        return cls(
            arn=data["EndpointArn"],
            status=data["Status"],
            failed_reason=data.get("Message"),
            model_arn=data.get("ModelArn"),
            inference_unites=data.get("CurrentInferenceUnits"),
            data_access_role_arn=data.get("DataAccessRoleArn"),
            desired_model_arn=data.get("DesiredModelArn"),
            desired_inference_units=data.get("DesiredInferenceUnits"),
            desired_data_access_role_arn=data.get("DesiredDataAccessRoleArn"),
            create_time=data.get("CreationTime"),
            update_time=data.get("LastModifiedTime"),
        )

    @classmethod
    def build_arn(
        cls,
        aws_account_id: str,
        aws_region: str,
        name: str,
    ) -> str:
        return f"arn:aws:comprehend:{aws_region}:{aws_account_id}:document-classifier-endpoint/{name}"

    @property
    def name(self) -> str:
        return self.arn.split("/")[-1]

    @property
    def aws_account_id(self) -> str:
        return self.arn.split(":")[4]

    @property
    def aws_region(self) -> str:
        return self.arn.split(":")[3]


def _list_endpoints(
    bsm: BotoSesManager,
    model_arn: T.Optional[str] = None,
    status: T.Optional[str] = None,
    creation_time_before: T.Optional[datetime] = None,
    creation_time_after: T.Optional[datetime] = None,
    max_items: int = 1000,
    page_size: int = 100,
) -> T.Iterable[Endpoint]:
    """
    Use paginator to list all endpoint.

    :param bsm:
    :param model_arn:
    :param status:
    :param creation_time_before:
    :param creation_time_after:
    :param max_items:
    :param page_size:
    :return:
    """
    # You can only set one filter at a time.
    if (
        sum(
            [
                model_arn is not None,
                status is not None,
                creation_time_before is not None,
                creation_time_after is not None,
            ]
        )
        > 1
    ):
        raise ValueError
    filter = dict()
    if model_arn is not None:  # pragma: no cover
        filter["ModelArn"] = model_arn
    if status is not None:  # pragma: no cover
        filter["Status"] = status
    if creation_time_before is not None:  # pragma: no cover
        filter["CreationTimeBefore"] = creation_time_before
    if creation_time_after is not None:  # pragma: no cover
        filter["CreationTimeAfter"] = creation_time_after

    paginator = bsm.comprehend_client.get_paginator("list_endpoints")

    kwargs = dict(
        PaginationConfig=dict(
            MaxItems=max_items,
            PageSize=page_size,
        )
    )
    if len(filter):
        kwargs["Filter"] = filter
    for response in paginator.paginate(**kwargs):
        for endpoint_properties in response.get("EndpointPropertiesList", []):
            yield Endpoint.from_describe_endpoint_response(endpoint_properties)


class EndpointIterProxy(IterProxy[Endpoint]):
    pass


def list_endpoints(
    bsm: BotoSesManager,
    model_arn: T.Optional[str] = None,
    status: T.Optional[str] = None,
    creation_time_before: T.Optional[datetime] = None,
    creation_time_after: T.Optional[datetime] = None,
    max_items: int = 1000,
    page_size: int = 100,
) -> EndpointIterProxy:
    return EndpointIterProxy(
        _list_endpoints(
            bsm=bsm,
            model_arn=model_arn,
            status=status,
            creation_time_before=creation_time_before,
            creation_time_after=creation_time_after,
            max_items=max_items,
            page_size=page_size,
        )
    )


def describe_endpoint(
    bsm: BotoSesManager,
    name_or_arn: str,
) -> T.Optional[Endpoint]:
    """

    :param bsm:
    :param name_or_arn:
    :return:

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_endpoint
    """
    if name_or_arn.startswith("arn:"):
        arn = name_or_arn
    else:
        arn = f"arn:aws:comprehend:{bsm.aws_region}:{bsm.aws_account_id}:document-classifier-endpoint/{name_or_arn}"
    try:
        response = bsm.comprehend_client.describe_endpoint(EndpointArn=arn)
        return Endpoint.from_describe_endpoint_response(response["EndpointProperties"])
    except Exception as e:
        if "ResourceNotFoundException" in str(e):
            return None
        else:  # pragma: no cover
            raise e
