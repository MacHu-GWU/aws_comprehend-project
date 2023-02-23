# -*- coding: utf-8 -*-

import os
import pytest

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
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
