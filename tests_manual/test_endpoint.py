# -*- coding: utf-8 -*-
import pytest
from rich import print as rprint
from aws_comprehend.tests import bsm, run_cov_test
from aws_comprehend.better_boto.endpoint import (
    EndpointStatusEnum,
    Endpoint,
    list_endpoints,
    describe_endpoint,
    update_endpoint,
    delete_endpoint,
    wait_endpoint,
    wait_create_or_update_endpoint_to_succeed,
    wait_delete_endpoint_to_finish,
    WaiterError,
)


class TestDocumentClassifier:
    def test(self):
        print("")

        endpoint_name = "tax-document-classifier-v000001"
        endpoint_arn = Endpoint.build_arn(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            name=endpoint_name,
        )

        endpoint = describe_endpoint(bsm=bsm, name_or_arn=endpoint_name)
        endpoint = describe_endpoint(bsm=bsm, name_or_arn=endpoint_arn)
        assert endpoint.aws_account_id == bsm.aws_account_id
        assert endpoint.aws_region == bsm.aws_region
        assert endpoint.name == endpoint_name
        # rprint(endpoint)

        assert describe_endpoint(bsm=bsm, name_or_arn="invalid") is None
        # since the endpoint is already in service, it should instantly return
        wait_create_or_update_endpoint_to_succeed(bsm=bsm, name_or_arn=endpoint_name, verbose=False)
        # since the endpoint doesn't exists, it should instantly fail
        with pytest.raises(WaiterError):
            wait_create_or_update_endpoint_to_succeed(bsm=bsm, name_or_arn="invalid", verbose=False)

        endpoints = list_endpoints(bsm=bsm).all()
        # rprint(endpoints)

        endpoints = list_endpoints(bsm=bsm, status="IN_SERVICE").all()
        # rprint(endpoints)

        # since the endpoint doesn't exist, it should return False
        flag = delete_endpoint(bsm=bsm, name_or_arn="invalid")
        assert flag is False

        # since the endpoint is already in service, it should instantly raise error
        with pytest.raises(WaiterError):
            wait_delete_endpoint_to_finish(bsm=bsm, name_or_arn=endpoint_name, verbose=False)
        # since the endpoint does not exists, it should instantly return
        wait_delete_endpoint_to_finish(bsm=bsm, name_or_arn="invalid", verbose=False)



if __name__ == "__main__":
    run_cov_test(__file__, "aws_comprehend.better_boto.endpoint", preview=False)
