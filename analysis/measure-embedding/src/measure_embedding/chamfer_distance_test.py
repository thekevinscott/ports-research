import numpy as np
import pytest

from measure_embedding.chamfer_distance import chamfer_distance

A = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
B = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
ONES = np.array([1.0, 1.0])


def describe_chamfer_distance():
    def it_is_zero_for_identical_sets():
        report = chamfer_distance(A, B, ONES, ONES)
        assert report["chamfer_distance"] == pytest.approx(0.0)
        assert report["chamfer_a_to_b"] == pytest.approx(0.0)
        assert report["chamfer_b_to_a"] == pytest.approx(0.0)

    def it_is_symmetric():
        b = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        forward = chamfer_distance(A, b, ONES, ONES)
        backward = chamfer_distance(b, A, ONES, ONES)
        assert forward["chamfer_distance"] == pytest.approx(backward["chamfer_distance"])
        assert forward["chamfer_a_to_b"] == pytest.approx(backward["chamfer_b_to_a"])
        assert forward["chamfer_b_to_a"] == pytest.approx(backward["chamfer_a_to_b"])

    def it_raises_the_side_a_far_row_sits_on():
        a = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        report = chamfer_distance(a, np.array([[1.0, 0.0, 0.0]]), ONES, np.array([1.0]))
        assert report["chamfer_a_to_b"] == pytest.approx(0.5)
        assert report["chamfer_b_to_a"] == pytest.approx(0.0)
        assert report["chamfer_distance"] == pytest.approx(0.25)

    def it_weights_each_row_by_its_length():
        a = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        b = np.array([[1.0, 0.0, 0.0]])
        heavy_near = chamfer_distance(a, b, np.array([3.0, 1.0]), np.array([1.0]))
        heavy_far = chamfer_distance(a, b, np.array([1.0, 3.0]), np.array([1.0]))
        assert heavy_near["chamfer_a_to_b"] == pytest.approx(0.25)
        assert heavy_far["chamfer_a_to_b"] == pytest.approx(0.75)

    def it_handles_one_side_with_more_rows_than_the_other():
        a = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        b = np.array([[1.0, 0.0, 0.0]])
        report = chamfer_distance(a, b, np.array([1.0, 1.0, 1.0]), np.array([1.0]))
        assert report["chamfer_a_to_b"] == pytest.approx(2 / 3)
        assert report["chamfer_b_to_a"] == pytest.approx(0.0)

    def it_reports_the_row_count_of_each_side():
        report = chamfer_distance(A, np.array([[1.0, 0.0, 0.0]]), ONES, np.array([1.0]))
        assert (report["file_count_a"], report["file_count_b"]) == (2, 1)
