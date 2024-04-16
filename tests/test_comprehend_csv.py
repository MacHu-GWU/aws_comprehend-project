# -*- coding: utf-8 -*-

from aws_comprehend.comprehend_csv import (
    encode_label,
    encode_text,
    encode_row,
    to_csv,
)


def test_encode_row():
    assert (
        encode_row(
            ["class1"], 'My name is "Alice".\nThis is my son "Bob".\nNice to meet your'
        )
        == '"class1","My name is ""Alice"". This is my son ""Bob"". Nice to meet your"'
    )


if __name__ == "__main__":
    from aws_comprehend.tests import run_cov_test

    run_cov_test(__file__, "aws_comprehend.comprehend_csv", preview=False)
