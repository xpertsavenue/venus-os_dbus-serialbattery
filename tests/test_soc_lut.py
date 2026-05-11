#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for SOC_LUT (State of Charge Lookup Table) feature
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import parse_soc_lut, interpolate_soc_from_voltage


def test_parse_soc_lut_valid():
    """Test parsing a valid SOC_LUT string"""
    soc_lut_str = "3.0:0, 3.2:5, 3.3:10, 3.4:15, 3.5:20, 3.55:30, 3.6:35, 3.65:40, 3.7:45, 3.75:50, 3.8:60, 3.85:70, 3.9:80, 3.95:85, 4.0:90, 4.05:93, 4.1:95, 4.15:98, 4.2:100"
    result = parse_soc_lut(soc_lut_str)
    
    assert result is not None, "SOC_LUT parsing returned None"
    assert len(result) == 19, f"Expected 19 entries, got {len(result)}"
    assert result[3.0] == 0, "First entry should be 3.0V -> 0%"
    assert result[4.2] == 100, "Last entry should be 4.2V -> 100%"
    print("✓ test_parse_soc_lut_valid passed")


def test_parse_soc_lut_empty():
    """Test parsing an empty SOC_LUT string"""
    result = parse_soc_lut("")
    assert result is None, "Empty SOC_LUT should return None"
    print("✓ test_parse_soc_lut_empty passed")


def test_parse_soc_lut_invalid_format():
    """Test parsing invalid SOC_LUT format"""
    soc_lut_str = "3.0-0, 3.2-5"  # Wrong format (- instead of :)
    result = parse_soc_lut(soc_lut_str)
    assert result is None, "Invalid format should return None"
    print("✓ test_parse_soc_lut_invalid_format passed")


def test_parse_soc_lut_invalid_values():
    """Test parsing SOC_LUT with invalid SOC values"""
    soc_lut_str = "3.0:0, 3.2:150"  # 150% is invalid
    result = parse_soc_lut(soc_lut_str)
    assert result is None, "SOC > 100 should return None"
    print("✓ test_parse_soc_lut_invalid_values passed")


def test_interpolate_soc_below_minimum():
    """Test interpolation with voltage below minimum"""
    soc_lut = {3.0: 0, 3.5: 50, 4.0: 100}
    result = interpolate_soc_from_voltage(2.5, soc_lut)
    assert result == 0, "Voltage below minimum should return minimum SOC"
    print("✓ test_interpolate_soc_below_minimum passed")


def test_interpolate_soc_above_maximum():
    """Test interpolation with voltage above maximum"""
    soc_lut = {3.0: 0, 3.5: 50, 4.0: 100}
    result = interpolate_soc_from_voltage(4.5, soc_lut)
    assert result == 100, "Voltage above maximum should return maximum SOC"
    print("✓ test_interpolate_soc_above_maximum passed")


def test_interpolate_soc_exact_match():
    """Test interpolation with exact voltage match"""
    soc_lut = {3.0: 0, 3.5: 50, 4.0: 100}
    result = interpolate_soc_from_voltage(3.5, soc_lut)
    assert result == 50, "Exact match should return exact SOC"
    print("✓ test_interpolate_soc_exact_match passed")


def test_interpolate_soc_between_points():
    """Test linear interpolation between two points"""
    soc_lut = {3.0: 0, 4.0: 100}
    result = interpolate_soc_from_voltage(3.5, soc_lut)
    assert result == 50, "3.5V should interpolate to 50%"
    
    result = interpolate_soc_from_voltage(3.2, soc_lut)
    assert result == 20, "3.2V should interpolate to 20%"
    
    result = interpolate_soc_from_voltage(3.8, soc_lut)
    assert result == 80, "3.8V should interpolate to 80%"
    print("✓ test_interpolate_soc_between_points passed")


def test_interpolate_soc_full_lut():
    """Test with full realistic SOC_LUT"""
    soc_lut_str = "3.0:0, 3.2:5, 3.3:10, 3.4:15, 3.5:20, 3.55:30, 3.6:35, 3.65:40, 3.7:45, 3.75:50, 3.8:60, 3.85:70, 3.9:80, 3.95:85, 4.0:90, 4.05:93, 4.1:95, 4.15:98, 4.2:100"
    soc_lut = parse_soc_lut(soc_lut_str)
    
    # Test some key points
    assert soc_lut is not None, "SOC_LUT parsing failed"
    
    # Test interpolation at 3.5V (should be exactly 20%)
    result = interpolate_soc_from_voltage(3.5, soc_lut)
    assert result == 20, f"3.5V should be 20%, got {result}"
    
    # Test interpolation between 3.5V and 3.55V
    result = interpolate_soc_from_voltage(3.525, soc_lut)
    expected = 20 + (3.525 - 3.5) * (30 - 20) / (3.55 - 3.5)
    assert abs(result - expected) < 0.01, f"3.525V interpolation failed: expected {expected}, got {result}"
    
    print("✓ test_interpolate_soc_full_lut passed")


def test_interpolate_soc_none_input():
    """Test interpolation with None input"""
    soc_lut = {3.0: 0, 3.5: 50, 4.0: 100}
    result = interpolate_soc_from_voltage(None, soc_lut)
    assert result is None, "None voltage should return None"
    
    result = interpolate_soc_from_voltage(3.5, None)
    assert result is None, "None SOC_LUT should return None"
    print("✓ test_interpolate_soc_none_input passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Running SOC_LUT Unit Tests")
    print("="*50 + "\n")
    
    tests = [
        test_parse_soc_lut_valid,
        test_parse_soc_lut_empty,
        test_parse_soc_lut_invalid_format,
        test_parse_soc_lut_invalid_values,
        test_interpolate_soc_below_minimum,
        test_interpolate_soc_above_maximum,
        test_interpolate_soc_exact_match,
        test_interpolate_soc_between_points,
        test_interpolate_soc_full_lut,
        test_interpolate_soc_none_input,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)