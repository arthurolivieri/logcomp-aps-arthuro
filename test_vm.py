#!/usr/bin/env python3
"""
Test script for AirConditioner VM with different scenarios
"""

from airconditioner_vm import AirConditionerVM

def test_scenario(name, vm, sensor_settings, program_file):
    """Run a test scenario with specific sensor values"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    
    # Reset VM
    vm.reset()
    
    # Set sensor values
    for sensor, value in sensor_settings.items():
        vm.set_sensor(sensor, value)
    
    # Load and run program
    with open(program_file, 'r') as f:
        program = f.read()
    
    vm.load_program(program)
    
    print(f"\nInitial Sensors:")
    print(f"  Temperature: {vm.sensors['TEMP']}°C")
    print(f"  Humidity: {vm.sensors['HUMIDITY']}%")
    print(f"  Occupied: {'YES' if vm.sensors['OCCUPIED'] else 'NO'}")
    print(f"  Time: {vm.sensors['TIME']//3600:02d}:{(vm.sensors['TIME']%3600)//60:02d}")
    
    print(f"\n--- Running Program ---\n")
    vm.run(max_steps=1000)
    
    print(f"\nFinal Device State:")
    print(f"  Power: {'ON' if vm.device_state['POWER_STATE'] else 'OFF'}")
    mode_names = ["COOL", "HEAT", "DRY", "FAN", "AUTO"]
    print(f"  Mode: {mode_names[vm.device_state['MODE']]}")
    print(f"  Target Temp: {vm.device_state['TARGET_TEMP']}°C")
    print(f"  Current Temp: {vm.sensors['TEMP']}°C")
    fan_names = ["OFF", "LOW", "MID", "HIGH"]
    print(f"  Fan: {fan_names[vm.device_state['FAN_SPEED']]}")
    print(f"  Steps: {vm.steps}, Ticks: {vm.ticks}")


if __name__ == "__main__":
    vm = AirConditionerVM()
    program_file = "test.asm"
    
    # Test 1: Hot room, high humidity, occupied, daytime
    test_scenario(
        "Test 1: Hot & Humid Room (Occupied, Daytime)",
        vm,
        {"TEMP": 28, "HUMIDITY": 75, "OCCUPIED": 1, "TIME": 43200},  # 12:00
        program_file
    )
    
    # Test 2: Cool room, normal humidity, empty, nighttime
    test_scenario(
        "Test 2: Cool Room (Empty, Nighttime)",
        vm,
        {"TEMP": 20, "HUMIDITY": 50, "OCCUPIED": 0, "TIME": 79200},  # 22:00
        program_file
    )
    
    # Test 3: Warm room, occupied, evening
    test_scenario(
        "Test 3: Warm Room (Occupied, Evening)",
        vm,
        {"TEMP": 26, "HUMIDITY": 55, "OCCUPIED": 1, "TIME": 72000},  # 20:00
        program_file
    )
    
    # Test 4: Very humid room
    test_scenario(
        "Test 4: Very Humid Room",
        vm,
        {"TEMP": 24, "HUMIDITY": 80, "OCCUPIED": 0, "TIME": 36000},  # 10:00
        program_file
    )
    
    print(f"\n{'='*60}")
    print("  All Tests Complete!")
    print(f"{'='*60}\n")
