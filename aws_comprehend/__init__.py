# -*- coding: utf-8 -*-

"""
Amazon Comprehend enhancement.
"""


from ._version import __version__

__short_description__ = "Amazon Comprehend enhancement."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from . import better_boto
    from .comprehend_csv import to_csv
    from .waiter import WaiterError, Waiter
except:
    pass