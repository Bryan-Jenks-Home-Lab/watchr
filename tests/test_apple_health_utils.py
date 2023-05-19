import xml.etree.ElementTree as ET

import pytest

from src.apple_health.utils import get_xml_file_root_element, parse_xml_data_to_df


def test_get_xml_file_root_element(tmp_path):
    data = """<?xml version="1.0" encoding="UTF-8"?>
<HealthData locale="en_US">
    <ExportDate value="2021-08-18 18:18:18 -0400" />
    <Me HKCharacteristicTypeIdentifierDateOfBirth="1980-01-01"
        HKCharacteristicTypeIdentifierBiologicalSex="HKBiologicalSexMale"
        HKCharacteristicTypeIdentifierBloodType="HKBloodTypeNotSet"
        HKCharacteristicTypeIdentifierFitzpatrickSkinType="HKFitzpatrickSkinTypeNotSet" />
    <Record type="HKQuantityTypeIdentifierBodyMassIndex" sourceName="Health" sourceVersion="14.6"
        device="&lt;&lt;HKDevice: 0x280e0d5c0&gt;, name:Apple Watch, manufacturer:Apple Inc., model:Watch, hardware:Watch6,4, software:7.6&gt;"
        unit="count" creationDate="2021-08-18 18:18:18 -0400" startDate="2021-08-18 18:18:18 -0400"
        endDate="2021-08-18 18:18:18 -0400" value="24.0" />
    <Record type="HKQuantityTypeIdentifierBodyMass" sourceName="Health" sourceVersion="14.6"
        device="&lt;&lt;HKDevice: 0x280e0d5c0&gt;, name:Apple Watch, manufacturer:Apple Inc., model:Watch, hardware:Watch6,4, software:7.6&gt;"
        unit="lb" creationDate="2021-08-18 18:18:18 -0400" startDate="2021-08-18 18:18:18 -0400"
        endDate="2021-08-18 18:18:18 -0400" value="200.0" />
</HealthData>
    """
    temp_file = tmp_path / "data.xml"
    temp_file.write_text(data)
    root_element = get_xml_file_root_element(temp_file)

    assert isinstance(root_element, ET.Element)
