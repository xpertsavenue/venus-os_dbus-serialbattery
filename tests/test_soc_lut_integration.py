#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration tests for SOC_LUT with Battery class
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import parse_soc_lut
from battery import Battery, Cell


class MockBattery(Battery):
    """Mock Battery class for testing"""
    
    def __init__(self):
        # Initialize without port/baud/address
        self.port = "test_port"
        self.baud_rate = 9600
        self.address = None
        self.cells = []
        self.cell_count = 4
        self.soc_lut = None
        self.voltage = None
        self.current = None
        self.soc = 0
        self.soh = 100
        self.capacity = 100
        self.type = "MockBattery"
    
    def test_connection(self) -> bool:
        return True
    
    def get_settings(self) -> bool:
        return True
    
    def refresh_data(self) -> bool:
        return True


def test_battery_with_soc_lut():
    """Test battery with SOC_LUT"""
    battery = MockBattery()
    
    # Parse SOC_LUT
    soc_lut_str = "3.0:0, 3.2:5, 3.3:10, 3.4:15, 3.5:20, 3.55:30, 3.6:35, 3.65:40, 3.7:45, 3.75:50, 3.8:60, 3.85:70, 3.9:80, 3.95:85, 4.0:90, 4.05:93, 4.1:95, 4.15:98, 4.2:100"
    battery.soc_lut = parse_soc_lut(soc_lut_str)
    
    assert battery.soc_lut is not None, "SOC_LUT should be parsed"
    assert len(battery.soc_lut) == 19, "SOC_LUT should have 19 entries"
    
    # Create cells with known voltages (4 cells à 3.5V = 14V total, average = 3.5V)
    battery.cells = [
        Cell(),
        Cell(),
        Cell(),
        Cell(),
    ]
    
    battery.cells[0].voltage = 3.5
    battery.cells[1].voltage = 3.5
    battery.cells[2].voltage = 3.5
    battery.cells[3].voltage = 3.5
    
    # Test interpolation
    avg_voltage = battery.get_cell_voltage_sum() / battery.cell_count
    assert avg_voltage == 3.5, "Average voltage should be 3.5V"
    
    print(f"✓ Battery test passed with avg voltage: {avg_voltage}V")


def test_battery_cell_voltage_variance():
    """Test battery with varying cell voltages"""
    battery = MockBattery()
    
    soc_lut_str = "3.0:0, 3.2:5, 3.3:10, 3.4:15, 3.5:20, 3.55:30, 3.6:35, 3.65:40, 3.7:45, 3.75:50, 3.8:60, 3.85:70, 3.9:80, 3.95:85, 4.0:90, 4.05:93, 4.1:95, 4.15:98, 4.2:100"
    battery.soc_lut = parse_soc_lut(soc_lut_str)
    
    battery.cells = [
        Cell(),
        Cell(),
        Cell(),
        Cell(),
    ]
    
    # Mixed cell voltages
    battery.cells[0].voltage = 3.4
    battery.cells[1].voltage = 3.5
    battery.cells[2].voltage = 3.6
    battery.cells[3].voltage = 3.7
    
    avg_voltage = battery.get_cell_voltage_sum() / battery.cell_count
    expected_avg = (3.4 + 3.5 + 3.6 + 3.7) / 4
    assert abs(avg_voltage - expected_avg) < 0.001, "Average voltage calculation failed"
    
    print(f"✓ Battery variance test passed with avg voltage: {avg_voltage:.3f}V")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Running SOC_LUT Integration Tests")
    print("="*50 + "\n")
    
    try:
        test_battery_with_soc_lut()
        test_battery_cell_voltage_variance()
        print("\n" + "="*50)
        print("All integration tests passed ✓")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)