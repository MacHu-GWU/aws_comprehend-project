# -*- coding: utf-8 -*-

from rich import print as rprint
from aws_comprehend.tests import bsm, run_cov_test
from aws_comprehend.better_boto.endpoint import (
    Endpoint,
    list_endpoints,
    describe_endpoint,
)


class TestDocumentClassifier:
    def test(self):
        print("")

        endpoint_name = "tax-document-classifier-v000001"

        endpoint = describe_endpoint(bsm=bsm, name_or_arn=endpoint_name)
        endpoint = describe_endpoint(
            bsm=bsm,
            name_or_arn=Endpoint.build_arn(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=endpoint_name,
            ),
        )
        assert endpoint.aws_account_id == bsm.aws_account_id
        assert endpoint.aws_region == bsm.aws_region
        assert endpoint.name == endpoint_name
        rprint(endpoint)

        assert describe_endpoint(bsm=bsm, name_or_arn="invalid") is None

        rprint(list_endpoints(bsm=bsm).all())
        rprint(list_endpoints(bsm=bsm, status="IN_SERVICE").all())



if __name__ == "__main__":
    run_cov_test(__file__, "aws_comprehend.better_boto.endpoint", preview=False)
