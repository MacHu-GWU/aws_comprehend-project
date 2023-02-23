# -*- coding: utf-8 -*-

from rich import print as rprint
from aws_comprehend.tests import bsm
from aws_comprehend import better_boto

model_arn = "arn:aws:comprehend:us-east-1:669508176277:document-classifier/tax-document-classifier/version/v000002"
endpoint_name = "tax-document-classifier-v000001"
endpoint_arn = better_boto.Endpoint.build_arn(
    aws_account_id=bsm.aws_account_id,
    aws_region=bsm.aws_region,
    name=endpoint_name,
)

# better_boto.wait_create_or_update_endpoint_to_succeed(bsm=bsm, name_or_arn=endpoint_arn)
# better_boto.wait_delete_endpoint_to_finish(bsm=bsm, name_or_arn=endpoint_arn)

# response = bsm.comprehend_client.create_endpoint(
#     EndpointName=f"{self.classifier_version.name}-{self.classifier_version.version_name}",
#     ModelArn=self.classifier_version.arn,
#     DesiredInferenceUnits=1,
#     DataAccessRoleArn=self.real_time_endpoint_iam_role_arn,
# )
