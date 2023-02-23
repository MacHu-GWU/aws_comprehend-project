# -*- coding: utf-8 -*-
import pytest
from rich import print as rprint
from aws_comprehend.tests import bsm, run_cov_test
from aws_comprehend.better_boto.document_classifier import (
    DocumentClassifierStatusEnum,
    DocumentClassifierVersion,
    list_document_classifiers,
    describe_document_classifier,
    delete_document_classifier,
    wait_document_classifier,
    wait_create_document_classifier_to_succeed,
    wait_delete_document_classifier_to_finish,
    WaiterError,
)


class TestDocumentClassifier:
    def test(self):
        print("")

        # ----------------------------------------------------------------------
        classifier_name = "tax-document-classifier"
        classifier_version = describe_document_classifier(
            bsm=bsm,
            arn=DocumentClassifierVersion.build_arn(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                classifier_name=classifier_name,
                version_name="v000001",
            ),
        )
        assert classifier_version.aws_account_id == bsm.aws_account_id
        assert classifier_version.aws_region == bsm.aws_region
        assert classifier_version.classifier_name == classifier_name
        # rprint(classifier_version)

        # since the classifier is already trained, it should instantly return
        wait_create_document_classifier_to_succeed(
            bsm=bsm, arn=classifier_version.arn, verbose=False
        )
        # since the classifier is already trained, it should instantly fail
        with pytest.raises(WaiterError):
            wait_delete_document_classifier_to_finish(
                bsm=bsm, arn=classifier_version.arn, verbose=False
            )

        # since the classifier does not exist, it should instantly fail
        invalid_arn = DocumentClassifierVersion.build_arn(
            aws_account_id=classifier_version.aws_account_id,
            aws_region=classifier_version.aws_region,
            classifier_name=classifier_version.classifier_name,
            version_name="v999999",
        )
        with pytest.raises(WaiterError):
            wait_create_document_classifier_to_succeed(
                bsm=bsm, arn=invalid_arn, verbose=False
            )
        # since the classifier does not exist, it should instantly return
        wait_delete_document_classifier_to_finish(
            bsm=bsm, arn=invalid_arn, verbose=False
        )

        # ----------------------------------------------------------------------
        assert (
            describe_document_classifier(
                bsm=bsm,
                arn=DocumentClassifierVersion.build_arn(
                    aws_account_id=bsm.aws_account_id,
                    aws_region=bsm.aws_region,
                    classifier_name=classifier_name,
                    version_name="v999999",
                ),
            )
            == None
        )

        # ----------------------------------------------------------------------
        classifier_version = DocumentClassifierVersion.get_latest(
            bsm=bsm, classifier_name=classifier_name
        )
        # rprint(classifier_version)

        assert (
            DocumentClassifierVersion.get_latest(bsm=bsm, classifier_name="invalid")
            is None
        )

        # ----------------------------------------------------------------------
        classifier_version = list_document_classifiers(
            bsm=bsm, name=classifier_name
        ).one_or_none()
        assert classifier_version.aws_account_id == bsm.aws_account_id
        # rprint(classifier_version)
        assert list_document_classifiers(bsm=bsm, name="invalid").one_or_none() is None

        # ----------------------------------------------------------------------
        with pytest.raises(ValueError):
            list_document_classifiers(
                bsm=bsm,
                name=classifier_name,
                status=DocumentClassifierStatusEnum.TRAINED,
            ).all()


if __name__ == "__main__":
    run_cov_test(
        __file__, "aws_comprehend.better_boto.document_classifier", preview=False
    )
