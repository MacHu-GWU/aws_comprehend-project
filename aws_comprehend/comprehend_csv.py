# -*- coding: utf-8 -*-

"""
Handle the Comprehend CSV data format.

Reference:

- multi class: https://docs.aws.amazon.com/comprehend/latest/dg/prep-classifier-data-multi-class.html
- multi label: https://docs.aws.amazon.com/comprehend/latest/dg/prep-classifier-data-multi-label.html
"""

import typing as T


def encode_label(
    label: T.Union[str, T.List[str]],
) -> str:
    if not isinstance(label, list):
        label = [
            label,
        ]
    return "|".join(label)


def encode_text(
    text: str,
) -> str:
    """
    For multi-class classification job Comprehend only recognize single line
    body of text. This function will convert multi line text to single line text.

    Examples:

        >>> text = ('''
        ... line1.
        ... line2.
        ... line3.
        ... ''')
        >>> encode_text(text)
        "line1. line2. line3."

    Ref: https://docs.aws.amazon.com/comprehend/latest/dg/prep-classifier-data-multi-class.html
    """
    return text.replace("\n", " ").replace('"', '""')


def encode_row(
    label: T.Union[str, T.List[str]],
    text: str,
) -> str:
    """
    The Amazon Comprehend accept CSV format and both label and content must be
    quoted. The content cannot have any newline character.

    Ref: https://docs.aws.amazon.com/comprehend/latest/dg/prep-classifier-data-multi-class.html
    """
    return '"{}","{}"'.format(
        encode_label(label),
        encode_text(text),
    )


def to_csv(
    rows: T.List[
        T.Tuple[
            T.Union[str, T.List[str]],
            str,
        ]
    ]
) -> str:
    return "\n".join([encode_row(label, text) for label, text in rows])
