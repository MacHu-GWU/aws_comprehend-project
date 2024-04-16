# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from aws_comprehend.tests import run_cov_test

    run_cov_test(__file__, "aws_comprehend", is_folder=True, preview=False)
