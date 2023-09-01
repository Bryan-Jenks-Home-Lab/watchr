import pytest

from src.apple_health.models import AppleHealthProcessor
from src.common import get_processor


def test_get_processor():
    assert get_processor("export.zip") == AppleHealthProcessor
