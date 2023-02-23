# -*- coding: utf-8 -*-

"""
The data model for custom document classifier.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime

from iterproxy import IterProxy
from boto_session_manager import BotoSesManager


class DocumentClassifierStatusEnum(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    TRAINING = "TRAINING"
    DELETING = "DELETING"
    STOP_REQUESTED = "STOP_REQUESTED"
    STOPPED = "STOPPED"
    IN_ERROR = "IN_ERROR"
    TRAINED = "TRAINED"


@dataclasses.dataclass
class DocumentClassifierVersion:
    """
    :param arn: example, arn:aws:comprehend:us-east-1:669508176277:document-classifier/tax-document-classifier/version/v000001
    :param language_code: example: en
    """

    arn: str = dataclasses.field(default=None)
    language_code: T.Optional[str] = dataclasses.field(default=None)
    version_name: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    status_message: T.Optional[str] = dataclasses.field(default=None)
    submit_time: T.Optional[datetime] = dataclasses.field(default=None)
    end_time: T.Optional[datetime] = dataclasses.field(default=None)
    training_start_time: T.Optional[datetime] = dataclasses.field(default=None)
    training_end_time: T.Optional[datetime] = dataclasses.field(default=None)
    input_data_config: T.Optional[dict] = dataclasses.field(default=None)
    output_data_config: T.Optional[dict] = dataclasses.field(default=None)
    classifier_metadata: T.Optional[dict] = dataclasses.field(default=None)
    data_access_role_arn: T.Optional[str] = dataclasses.field(default=None)
    volume_kms_key_id: T.Optional[str] = dataclasses.field(default=None)
    vpc_config: T.Optional[dict] = dataclasses.field(default=None)
    mode: T.Optional[str] = dataclasses.field(default=None)
    model_kms_key_id: T.Optional[str] = dataclasses.field(default=None)
    source_model_arn: T.Optional[str] = dataclasses.field(default=None)

    @property
    def classifier_name(self) -> str:
        return self.arn.split("/")[1]

    @property
    def aws_account_id(self) -> str:
        return self.arn.split(":")[4]

    @property
    def aws_region(self) -> str:
        return self.arn.split(":")[3]

    @classmethod
    def from_describe_document_classifier_response(
        cls,
        document_classifier_properties: dict,
    ) -> "DocumentClassifierVersion":
        """
        :param document_classifier_properties: the dict at the field "DocumentClassifierProperties"

        Ref:

        - describe_document_classifier: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_document_classifier
        - list_document_classifiers: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classifiers
        """
        return cls(
            arn=document_classifier_properties.get("DocumentClassifierArn"),
            language_code=document_classifier_properties.get("LanguageCode"),
            version_name=document_classifier_properties.get("VersionName"),
            status=document_classifier_properties.get("Status"),
            status_message=document_classifier_properties.get("Message"),
            submit_time=document_classifier_properties.get("SubmitTime"),
            end_time=document_classifier_properties.get("EndTime"),
            training_start_time=document_classifier_properties.get("TrainingStartTime"),
            training_end_time=document_classifier_properties.get("TrainingEndTime"),
            input_data_config=document_classifier_properties.get("InputDataConfig"),
            output_data_config=document_classifier_properties.get("OutputDataConfig"),
            classifier_metadata=document_classifier_properties.get(
                "ClassifierMetadata"
            ),
            data_access_role_arn=document_classifier_properties.get(
                "DataAccessRoleArn"
            ),
            volume_kms_key_id=document_classifier_properties.get("VolumeKmsKeyId"),
            vpc_config=document_classifier_properties.get("VpcConfig"),
            mode=document_classifier_properties.get("Mode"),
            model_kms_key_id=document_classifier_properties.get("ModelKmsKeyId"),
            source_model_arn=document_classifier_properties.get("SourceModelArn"),
        )

    @classmethod
    def build_arn(
        cls,
        aws_account_id: str,
        aws_region: str,
        classifier_name: str,
        version_name: str,
    ) -> str:
        return (
            f"arn:aws:comprehend:{aws_region}:{aws_account_id}:document-classifier"
            f"/{classifier_name}/version/{version_name}"
        )

    @classmethod
    def get_latest(
        cls,
        bsm: BotoSesManager,
        classifier_name: str,
    ) -> T.Optional["DocumentClassifierVersion"]:
        """
        :param bsm:
        :param classifier_name:
        :return:

        Ref:

        - list_document_classifier_summaries: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classifier_summaries
        """
        response = bsm.comprehend_client.list_document_classifier_summaries(
            MaxResults=100
        )
        for document_classifier_summary in response["DocumentClassifierSummariesList"]:
            if document_classifier_summary["DocumentClassifierName"] == classifier_name:
                version_name = document_classifier_summary["LatestVersionName"]
                arn = (
                    f"arn:aws:comprehend:{bsm.aws_region}:{bsm.aws_account_id}:document-classifier"
                    f"/{classifier_name}/version/{version_name}"
                )
                return describe_document_classifier(bsm=bsm, arn=arn)
        return None


class DocumentClassifierVersionIterProxy(IterProxy[DocumentClassifierVersion]):
    pass


def _list_document_classifiers(
    bsm: BotoSesManager,
    name: T.Optional[str] = None,
    status: T.Optional[str] = None,
    submit_time_before: T.Optional[datetime] = None,
    submit_time_after: T.Optional[datetime] = None,
    max_items: int = 1000,
    page_size: int = 100,
) -> T.Iterable[DocumentClassifierVersion]:
    """
    Use paginator to list all document classifier.

    If you use "name" in the filter, then it always returns in descending
     order based on version creation time.

    :param bsm:
    :param name:
    :param status:
    :param submit_time_before:
    :param submit_time_after:
    :param max_items:
    :param page_size:

    :return:

    Ref:

    - list_document_classifiers: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.list_document_classifiers
    """
    # You can only set one filter at a time.
    if (
        sum(
            [
                name is not None,
                status is not None,
                submit_time_before is not None,
                submit_time_after is not None,
            ]
        )
        > 1
    ):
        raise ValueError
    filter = dict()
    if name is not None:  # pragma: no cover
        filter["DocumentClassifierName"] = name
    if status is not None:  # pragma: no cover
        filter["Status"] = status
    if submit_time_before is not None:  # pragma: no cover
        filter["SubmitTimeBefore"] = submit_time_before
    if submit_time_after is not None:  # pragma: no cover
        filter["SubmitTimeAfter"] = submit_time_after

    paginator = bsm.comprehend_client.get_paginator("list_document_classifiers")

    kwargs = dict(
        PaginationConfig=dict(
            MaxItems=max_items,
            PageSize=page_size,
        )
    )
    if len(filter):
        kwargs["Filter"] = filter
    for response in paginator.paginate(**kwargs):
        for document_classifier_properties in response.get(
            "DocumentClassifierPropertiesList", []
        ):
            yield DocumentClassifierVersion.from_describe_document_classifier_response(
                document_classifier_properties
            )


def list_document_classifiers(
    bsm: BotoSesManager,
    name: T.Optional[str] = None,
    status: T.Optional[str] = None,
    submit_time_before: T.Optional[datetime] = None,
    submit_time_after: T.Optional[datetime] = None,
    max_items: int = 1000,
    page_size: int = 100,
) -> DocumentClassifierVersionIterProxy:
    return DocumentClassifierVersionIterProxy(
        _list_document_classifiers(
            bsm=bsm,
            name=name,
            status=status,
            submit_time_before=submit_time_before,
            submit_time_after=submit_time_after,
            max_items=max_items,
            page_size=page_size,
        )
    )


def describe_document_classifier(
    bsm: BotoSesManager,
    arn: str,
) -> T.Optional[DocumentClassifierVersion]:
    """
    :param bsm:
    :param arn:

    :return: DocumentClassifierVersion object or None if not found.

    Ref:

    - describe_document_classifier: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.describe_document_classifier
    """
    try:
        response = bsm.comprehend_client.describe_document_classifier(
            DocumentClassifierArn=arn,
        )
        return DocumentClassifierVersion.from_describe_document_classifier_response(
            document_classifier_properties=response["DocumentClassifierProperties"],
        )
    except Exception as e:
        if "ResourceNotFoundException" in str(e):
            return None
        else:  # pragma: no cover
            raise e
