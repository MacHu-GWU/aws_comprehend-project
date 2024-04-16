# -*- coding: utf-8 -*-

from aws_comprehend import api


def test():
    _ = api
    _ = api.better_boto
    _ = api.better_boto.DocumentClassifierStatusEnum
    _ = api.better_boto.LanguageEnum
    _ = api.better_boto.DocumentClassifierVersion
    _ = api.better_boto.list_document_classifiers
    _ = api.better_boto.describe_document_classifier
    _ = api.better_boto.wait_create_document_classifier_to_succeed
    _ = api.better_boto.wait_delete_document_classifier_to_finish
    _ = api.better_boto.EndpointStatusEnum
    _ = api.better_boto.Endpoint
    _ = api.better_boto.list_endpoints
    _ = api.better_boto.describe_endpoint
    _ = api.better_boto.wait_create_or_update_endpoint_to_succeed
    _ = api.better_boto.wait_delete_endpoint_to_finish
    _ = api.to_csv


if __name__ == "__main__":
    from aws_comprehend.tests import run_cov_test

    run_cov_test(__file__, "aws_comprehend.api", preview=False)
