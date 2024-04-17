# -*- coding: utf-8 -*-

"""
Debug aws_comprehend. You can also learn how to use aws_comprehend by reading this file.

Requirements:

    pip install "pathlib_mate>=1.3.2,<2.0.0"
    pip install "Faker>=24.0.0"
"""

import random
from datetime import datetime

from faker import Faker
from pathlib_mate import Path
from boto_session_manager import BotoSesManager
from s3pathlib import S3Path, context
from rich import print as rprint

import aws_comprehend.api as comp


# ------------------------------------------------------------------------------
# Change the following variables to your own settings
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
aws_profile = "bmt_app_dev_us_east_1"
# ------------------------------------------------------------------------------

fake = Faker()
dir_here = Path.dir_here(__file__)
dir_f1040 = dir_here / "f1040"
dir_fw2 = dir_here / "fw2"
dir_train = dir_here / "train"
dir_test = dir_here / "test"

bsm = BotoSesManager(profile_name=aws_profile)
context.attach_boto_session(bsm.boto_ses)
bucket = f"{bsm.aws_account_alias}-{bsm.aws_region}-data"
s3dir_root = S3Path(f"s3://{bucket}/project/aws_comprehend/").to_dir()
model_name = "tax-doc-classifier"
data_access_role = f"arn:aws:iam::{bsm.aws_account_id}:role/all-services-admin-role"


def random_ssn() -> str:
    ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    return ssn


def s1_generate_train_test():
    dir_train.remove_if_exists()
    dir_test.remove_if_exists()
    dir_train.mkdir_if_not_exists()
    dir_test.mkdir_if_not_exists()

    f1040_page_list = [p.read_text() for p in dir_f1040.select_by_ext(".txt")]
    fw2_page_list = [p.read_text() for p in dir_fw2.select_by_ext(".txt")]

    n_sample_per_class = 100

    for i in range(1, 1 + n_sample_per_class):
        text = random.choice(f1040_page_list)
        text = text.replace(
            "Your first name and middle initial Last name",
            f"Your first name and middle initial Last name {fake.name()}",
        )
        text = text.replace(
            "33 Add lines 25d, 26, and 32. These are your total payments . . . . . . . . . . . . 33",
            f"33 Add lines 25d, 26, and 32. These are your total payments . . . . . . . . . . . . 33 {random.randint(0, 10000)}",
        )
        dir_train.joinpath(f"f1040_{i}.txt").write_text(text)

    for i in range(1, 1 + n_sample_per_class):
        text = random.choice(fw2_page_list)
        text = text.replace(
            "a Employee’s social security number",
            f"a Employee’s social security number {random_ssn()}",
        )
        dir_train.joinpath(f"fw2_{i}.txt").write_text(text)


def s2_create_custom_model():
    # --------------------------------------------------------------------------
    # Prepare the training data
    # --------------------------------------------------------------------------
    rows = list()
    for p in dir_train.select_by_ext(".txt"):
        if p.fname.startswith("f1040"):
            label = "f1040"
        elif p.fname.startswith("fw2"):
            label = "fw2"
        else:  # pragma: no cover
            raise ValueError
        text = p.read_text()
        rows.append((label, text))
    train_data = comp.to_csv(rows)

    # --------------------------------------------------------------------------
    # Figure out the new version name
    # --------------------------------------------------------------------------
    classifier_version = comp.better_boto.DocumentClassifierVersion.get_latest(
        bsm=bsm, classifier_name=model_name
    )
    if classifier_version is None:
        new_version = "v000001"
    else:
        last_version = int(classifier_version.version_name[1:])
        new_version = f"v{str(last_version + 1).zfill(6)}"

    # --------------------------------------------------------------------------
    # Create new model
    # --------------------------------------------------------------------------
    now = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    s3dir_input = s3dir_root.joinpath(f"{model_name}/{now}/input").to_dir()
    s3dir_output = s3dir_root.joinpath(f"{model_name}/{now}/output").to_dir()
    print(f"{s3dir_input.console_url = !s}")
    print(f"{s3dir_output.console_url = !s}")

    s3path_train = s3dir_input.joinpath("train.csv")
    s3path_train.write_text(train_data, content_type="text/plain")

    bsm.comprehend_client.create_document_classifier(
        DocumentClassifierName=model_name,
        VersionName=new_version,
        DataAccessRoleArn=data_access_role,
        InputDataConfig=dict(
            DataFormat="COMPREHEND_CSV",
            S3Uri=s3path_train.uri,
            DocumentType="PLAIN_TEXT_DOCUMENT",
        ),
        OutputDataConfig=dict(
            S3Uri=s3dir_output.uri,
        ),
        LanguageCode=comp.better_boto.LanguageEnum.en.value,
        Mode="MULTI_CLASS",
    )


def s3_wait_create_custom_model_to_succeed(version_name: str):
    classifier_version = comp.better_boto.describe_document_classifier(
        bsm=bsm,
        arn=comp.better_boto.DocumentClassifierVersion.build_arn(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            classifier_name=model_name,
            version_name=version_name,
        ),
    )
    rprint(classifier_version)

    # since the classifier is already trained, it should instantly return
    comp.better_boto.wait_create_document_classifier_to_succeed(
        bsm=bsm,
        arn=classifier_version.arn,
        verbose=True,
    )


def s4_deploy_endpoint(version_name: str):
    endpoint_name = f"{model_name}-{version_name}"
    model_arn = comp.better_boto.DocumentClassifierVersion.build_arn(
        aws_account_id=bsm.aws_account_id,
        aws_region=bsm.aws_region,
        classifier_name=model_name,
        version_name=version_name,
    )
    response = bsm.comprehend_client.create_endpoint(
        EndpointName=endpoint_name,
        ModelArn=model_arn,
        DesiredInferenceUnits=1,
        DataAccessRoleArn=data_access_role,
    )
    rprint(response)


def s5_wait_create_endpoint_to_succeed(version_name: str):
    endpoint_name = f"{model_name}-{version_name}"
    comp.better_boto.wait_create_or_update_endpoint_to_succeed(
        bsm=bsm,
        name_or_arn=endpoint_name,
        verbose=True,
    )


def s6_test_endpoint(version_name: str):
    endpoint_name = f"{model_name}-{version_name}"
    endpoint_arn = comp.better_boto.Endpoint.build_arn(
        aws_account_id=bsm.aws_account_id,
        aws_region=bsm.aws_region,
        name=endpoint_name,
    )
    response = bsm.comprehend_client.classify_document(
        Text=dir_f1040.joinpath("f1040-page1.txt").read_text(),
        # Text=dir_fw2.joinpath("fw2-page1.txt").read_text(),
        EndpointArn=endpoint_arn,
    )
    rprint(response)


if __name__ == "__main__":
    s1_generate_train_test()
    # s2_create_custom_model()
    # version_name = "v000001"
    # s3_wait_create_custom_model_to_succeed(version_name)
    # s4_deploy_endpoint(version_name)
    # s5_wait_create_endpoint_to_succeed(version_name)
    # s6_test_endpoint(version_name)
