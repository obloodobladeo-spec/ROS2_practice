"""직접 변환한 영상의 색상 순서와 줄 끝 여백을 확인합니다."""

import numpy as np
import pytest
from sensor_msgs.msg import Image

from opencv_pkg.camera_numpy import image_to_bgr


def make_image(width, height, encoding, step, data):
    message = Image()
    message.width = width
    message.height = height
    message.encoding = encoding
    message.step = step
    message.data = bytes(data)
    return message


def test_rgb8_changes_to_bgr():
    message = make_image(2, 1, 'rgb8', 6, [255, 0, 0, 0, 255, 0])

    frame = image_to_bgr(message)

    np.testing.assert_array_equal(
        frame, [[[0, 0, 255], [0, 255, 0]]])


def test_bgr8_skips_padding_at_end_of_rows():
    message = make_image(
        1, 2, 'bgr8', 5, [1, 2, 3, 99, 99, 4, 5, 6, 99, 99])

    frame = image_to_bgr(message)

    np.testing.assert_array_equal(frame, [[[1, 2, 3]], [[4, 5, 6]]])


def test_rejects_unsupported_encoding():
    message = make_image(1, 1, 'mono8', 1, [42])

    with pytest.raises(ValueError, match='지원하지 않는'):
        image_to_bgr(message)


def test_rejects_wrong_data_length():
    message = make_image(1, 2, 'rgb8', 3, [1, 2, 3])

    with pytest.raises(ValueError, match='data 크기'):
        image_to_bgr(message)
