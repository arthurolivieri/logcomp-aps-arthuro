from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

Register = str

@dataclass
class Instr:
    op: str
    args: Tuple[str, ...]

class AirConditionerVM:

    def __init__(self):
        self.registers: Dict[Register, int] = {f"T{i}": 0 for i in range(10)}
        
        self.variables: Dict[str, int] = {}
        
        self.sensors: Dict[Register, int] = {
            "TEMP": 25,      # Current room temperature (Celsius)
            "HUMIDITY": 60,  # Current humidity percentage
            "OCCUPIED": 0,   # Presence sensor (0=empty, 1=occupied)
            "TIME": 43200    # Current time in seconds (default: 12:00)
        }
        
        # Device state
        self.device_state: Dict[str, int] = {
            "POWER_STATE": 0,    # 0=off, 1=on
            "MODE": 0,           # 0=cool, 1=heat, 2=dry, 3=fan, 4=auto
            "TARGET_TEMP": 24,   # Target temperature
            "FAN_SPEED": 0,      # 0=off, 1=low, 2=mid, 3=high
            "SWING_STATE": 0     # 0=off, 1=on
        }
        
        # Program execution state
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.pc: int = 0
        self.halted: bool = False
        self.steps: int = 0
        self.ticks: int = 0
        
        self.last_cmp_result: int = 0

    # --- Assembler / Loader ---
    def load_program(self, source: str):
        """Load and parse assembly program"""
        self.program.clear()
        self.labels.clear()
        self.pc = 0
        self.halted = False
        self.steps = 0
        self.ticks = 0

        lines = source.splitlines()
        # First pass: collect labels
        idx = 0
        for raw in lines:
            line = raw.split(';', 1)[0].strip()
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Empty label definition.")
                if label in self.labels:
                    raise ValueError(f"Duplicate label: {label}")
                self.labels[label] = idx
            else:
                idx += 1

        # Second pass: parse instructions
        for raw in lines:
            line = raw.split(';', 1)[0].strip()
            if not line or line.endswith(':'):
                continue
            tokens = line.replace(',', ' ').split()
            op = tokens[0].upper()
            args = tuple(tokens[1:])
            self.program.append(Instr(op, args))

    # --- Execution ---
    def step(self):
        """Execute one instruction"""
        if self.halted:
            return
        if not (0 <= self.pc < len(self.program)):
            self.halted = True
            return

        instr = self.program[self.pc]
        self.steps += 1
        self.ticks += 1
        
        # Update thermal model after each instruction
        self._update_thermal_model()

        # Execute instruction
        if instr.op == "LOAD_IMM":
            reg, val = instr.args[0], int(instr.args[1])
            self.registers[reg] = val
            self.pc += 1

        elif instr.op == "STORE":
            var, reg = instr.args[0], instr.args[1]
            self.variables[var] = self.registers[reg]
            self.pc += 1

        elif instr.op == "LOAD":
            # Handle both: "LOAD var, Tn" and "LOAD Tn, var"
            arg1, arg2 = instr.args[0], instr.args[1]
            if arg1.startswith('T') and arg1[1:].isdigit():
                # Format: LOAD Tn, var (compiler's format)
                reg, var = arg1, arg2
            else:
                # Format: LOAD var, Tn (alternative format)
                var, reg = arg1, arg2
            self.registers[reg] = self.variables.get(var, 0)
            self.pc += 1

        elif instr.op == "ADD":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            self.registers[rd] = self.registers[r1] + self.registers[r2]
            self.pc += 1

        elif instr.op == "SUB":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            self.registers[rd] = self.registers[r1] - self.registers[r2]
            self.pc += 1

        elif instr.op == "MUL":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            self.registers[rd] = self.registers[r1] * self.registers[r2]
            self.pc += 1

        elif instr.op == "DIV":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            if self.registers[r2] == 0:
                raise RuntimeError("Division by zero")
            self.registers[rd] = self.registers[r1] // self.registers[r2]
            self.pc += 1

        elif instr.op == "INC":
            reg = instr.args[0]
            self.registers[reg] += 1
            self.pc += 1

        elif instr.op == "DEC":
            reg = instr.args[0]
            self.registers[reg] -= 1
            self.pc += 1

        elif instr.op == "NEG":
            rd, r1 = instr.args[0], instr.args[1]
            self.registers[rd] = -self.registers[r1]
            self.pc += 1

        elif instr.op == "CMP_EQ":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] == self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "CMP_NE":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] != self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "CMP_LT":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] < self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "CMP_LE":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] <= self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "CMP_GT":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] > self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "CMP_GE":
            rd, r1, r2 = instr.args[0], instr.args[1], instr.args[2]
            result = 1 if self.registers[r1] >= self.registers[r2] else 0
            self.registers[rd] = result
            self.last_cmp_result = result
            self.pc += 1

        elif instr.op == "JZ":
            label = instr.args[0]
            if self.last_cmp_result == 0:
                if label not in self.labels:
                    raise ValueError(f"Unknown label: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif instr.op == "JNZ":
            label = instr.args[0]
            if self.last_cmp_result != 0:
                if label not in self.labels:
                    raise ValueError(f"Unknown label: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif instr.op == "JMP":
            label = instr.args[0]
            if label not in self.labels:
                raise ValueError(f"Unknown label: {label}")
            self.pc = self.labels[label]

        elif instr.op == "READ_SENSOR":
            reg, sensor = instr.args[0], instr.args[1].upper()
            if sensor not in self.sensors:
                raise ValueError(f"Unknown sensor: {sensor}")
            self.registers[reg] = self.sensors[sensor]
            self.pc += 1

        elif instr.op == "WAIT":
            reg = instr.args[0]
            wait_time = self.registers[reg]
            # Simulate waiting by advancing time
            self.sensors["TIME"] = (self.sensors["TIME"] + wait_time) % 86400
            self.ticks += wait_time
            self.pc += 1

        elif instr.op == "POWER":
            state = instr.args[0].upper()
            self.device_state["POWER_STATE"] = 1 if state == "ON" else 0
            self.pc += 1

        elif instr.op == "SET_MODE":
            mode_str = instr.args[0].upper()
            mode_map = {"COOL": 0, "HEAT": 1, "DRY": 2, "FAN": 3, "AUTO": 4}
            if mode_str not in mode_map:
                raise ValueError(f"Unknown mode: {mode_str}")
            self.device_state["MODE"] = mode_map[mode_str]
            self.pc += 1

        elif instr.op == "SET_TEMP":
            reg = instr.args[0]
            self.device_state["TARGET_TEMP"] = self.registers[reg]
            self.pc += 1

        elif instr.op == "SET_FAN":
            level_str = instr.args[0].upper()
            level_map = {"OFF": 0, "LOW": 1, "MID": 2, "HIGH": 3}
            if level_str not in level_map:
                raise ValueError(f"Unknown fan level: {level_str}")
            self.device_state["FAN_SPEED"] = level_map[level_str]
            self.pc += 1

        elif instr.op == "SET_SWING":
            state = instr.args[0].upper()
            self.device_state["SWING_STATE"] = 1 if state == "ON" else 0
            self.pc += 1

        elif instr.op == "PRINT":
            self._print_state()
            self.pc += 1

        elif instr.op == "HALT":
            print("*** Air Conditioner Program Halted ***")
            self.halted = True

        else:
            raise ValueError(f"Unknown instruction: {instr.op}")

    def _update_thermal_model(self):
        """
        Simple thermal model for air conditioning:
        - Temperature changes based on AC mode, power state, and fan speed
        - Cooling: temp decreases toward target
        - Heating: temp increases toward target
        - Natural drift toward ambient (assumed 25C)
        """
        if self.device_state["POWER_STATE"] == 0:
            # AC is off, natural drift toward ambient
            ambient = 25
            current = self.sensors["TEMP"]
            drift = (ambient - current) * 0.01
            self.sensors["TEMP"] = max(0, min(50, int(current + drift)))
            return

        mode = self.device_state["MODE"]
        target = self.device_state["TARGET_TEMP"]
        fan_speed = self.device_state["FAN_SPEED"]
        current = self.sensors["TEMP"]

        # Calculate temperature change rate
        rate = 0.0
        if mode == 0:  # COOL
            if current > target:
                rate = -0.1 * (1 + fan_speed * 0.5)
        elif mode == 1:  # HEAT
            if current < target:
                rate = 0.1 * (1 + fan_speed * 0.5)
        elif mode == 2:  # DRY
            # Dehumidification with slight cooling
            if self.sensors["HUMIDITY"] > 40:
                self.sensors["HUMIDITY"] = max(0, self.sensors["HUMIDITY"] - 1)
                rate = -0.05
        elif mode == 3:  # FAN
            # Just circulation, slight drift toward ambient
            rate = (25 - current) * 0.01

        # Update temperature (clamp to reasonable range)
        new_temp = current + int(rate)
        self.sensors["TEMP"] = max(0, min(50, new_temp))

    def _print_state(self):
        """Print current system state"""
        mode_names = ["COOL", "HEAT", "DRY", "FAN", "AUTO"]
        fan_names = ["OFF", "LOW", "MID", "HIGH"]
        print(f"=== Air Conditioner State ===")
        print(f"Power: {'ON' if self.device_state['POWER_STATE'] else 'OFF'}")
        print(f"Mode: {mode_names[self.device_state['MODE']]}")
        print(f"Target Temp: {self.device_state['TARGET_TEMP']}°C")
        print(f"Current Temp: {self.sensors['TEMP']}°C")
        print(f"Fan: {fan_names[self.device_state['FAN_SPEED']]}")
        print(f"Swing: {'ON' if self.device_state['SWING_STATE'] else 'OFF'}")
        print(f"Humidity: {self.sensors['HUMIDITY']}%")
        print(f"Occupied: {'YES' if self.sensors['OCCUPIED'] else 'NO'}")
        print(f"Time: {self.sensors['TIME']//3600:02d}:{(self.sensors['TIME']%3600)//60:02d}")
        print(f"============================")

    def run(self, max_steps: Optional[int] = None):
        """Run program until halt or max_steps reached"""
        while not self.halted:
            if max_steps is not None and self.steps >= max_steps:
                raise RuntimeError("Step limit reached (possible infinite loop).")
            self.step()

    # --- Helpers ---
    def state(self) -> Dict:
        """Get current VM state"""
        return {
            "registers": dict(self.registers),
            "variables": dict(self.variables),
            "sensors": dict(self.sensors),
            "device": dict(self.device_state),
            "pc": self.pc,
            "halted": self.halted,
            "steps": self.steps,
            "ticks": self.ticks
        }

    def reset(self):
        """Reset VM to initial state"""
        for reg in self.registers:
            self.registers[reg] = 0
        self.variables.clear()
        self.sensors = {
            "TEMP": 25,
            "HUMIDITY": 60,
            "OCCUPIED": 0,
            "TIME": 43200
        }
        self.device_state = {
            "POWER_STATE": 0,
            "MODE": 0,
            "TARGET_TEMP": 24,
            "FAN_SPEED": 0,
            "SWING_STATE": 0
        }
        self.pc = 0
        self.halted = False
        self.steps = 0
        self.ticks = 0
        self.last_cmp_result = 0

    def set_sensor(self, sensor: str, value: int):
        """Manually set a sensor value (for testing)"""
        sensor = sensor.upper()
        if sensor not in self.sensors:
            raise ValueError(f"Unknown sensor: {sensor}")
        self.sensors[sensor] = value


# --------- Demo programs ---------

# 1) Basic temperature control
BASIC_TEMP_PROGRAM = """
; Basic temperature control program
POWER ON
SET_MODE COOL
LOAD_IMM T0, 22
SET_TEMP T0
SET_FAN MID
PRINT
HALT
"""

# 2) Conditional control based on temperature
CONDITIONAL_PROGRAM = """
; Turn on cooling if temperature is too high
READ_SENSOR T0, TEMP
LOAD_IMM T1, 25
CMP_GT T2, T0, T1
JZ no_cooling

; Temperature > 25, activate cooling
POWER ON
SET_MODE COOL
LOAD_IMM T3, 22
SET_TEMP T3
SET_FAN HIGH
PRINT
JMP end

no_cooling:
; Temperature is fine
POWER OFF
PRINT

end:
HALT
"""

# 3) Loop example - gradual temperature adjustment
LOOP_PROGRAM = """
; Gradually adjust temperature
POWER ON
SET_MODE COOL
SET_FAN MID

LOAD_IMM T0, 5        ; Loop counter (5 iterations)
LOAD_IMM T1, 26       ; Starting temperature

loop:
SET_TEMP T1           ; Set target temperature
PRINT
LOAD_IMM T2, 1
SUB T1, T1, T2        ; Decrease by 1
DEC T0                ; Decrement counter
LOAD_IMM T3, 0
CMP_GT T4, T0, T3     ; Check if counter > 0
JNZ loop              ; Continue if not zero

HALT
"""

# 4) Presence-based control with time
PRESENCE_TIME_PROGRAM = """
; Smart control based on presence and time
READ_SENSOR T0, OCCUPIED
LOAD_IMM T1, 1
CMP_EQ T2, T0, T1
JZ not_occupied

; Room is occupied
READ_SENSOR T3, TIME
LOAD_IMM T4, 79200      ; 22:00 in seconds (22*3600)
CMP_GE T5, T3, T4
JZ daytime

; Nighttime occupied mode (eco)
POWER ON
SET_MODE COOL
LOAD_IMM T6, 24
SET_TEMP T6
SET_FAN LOW
PRINT
JMP end

daytime:
; Daytime occupied mode (comfort)
POWER ON
SET_MODE COOL
LOAD_IMM T7, 21
SET_TEMP T7
SET_FAN MID
PRINT
JMP end

not_occupied:
; Room is empty, turn off or eco mode
POWER ON
SET_MODE COOL
LOAD_IMM T8, 26
SET_TEMP T8
SET_FAN OFF
PRINT

end:
HALT
"""

# 5) Dehumidification mode
DEHUMIDIFY_PROGRAM = """
; Activate dehumidification if humidity is too high
READ_SENSOR T0, HUMIDITY
LOAD_IMM T1, 70
CMP_GT T2, T0, T1
JZ normal_mode

; High humidity, activate dry mode
POWER ON
SET_MODE DRY
SET_FAN HIGH
PRINT
JMP end

normal_mode:
; Normal cooling mode
POWER ON
SET_MODE COOL
LOAD_IMM T3, 23
SET_TEMP T3
SET_FAN MID
PRINT

end:
HALT
"""


# Quick usage example
if __name__ == "__main__":
    import sys
    
    vm = AirConditionerVM()

    if len(sys.argv) > 1:
        # Load program from file
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                program_content = f.read()
            vm.load_program(program_content)
            print(f"Loaded program from: {filename}")
            print()
            vm.run(max_steps=10000)
            print("\n=== Final State ===")
            print(f"Steps executed: {vm.steps}")
            print(f"Ticks elapsed: {vm.ticks}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Run demo programs
        print("=== Demo 1: Basic Temperature Control ===\n")
        vm.load_program(BASIC_TEMP_PROGRAM)
        vm.run()
        
        print("\n\n=== Demo 2: Conditional Control (Temp = 28°C) ===\n")
        vm.reset()
        vm.set_sensor("TEMP", 28)
        vm.load_program(CONDITIONAL_PROGRAM)
        vm.run()
        
        print("\n\n=== Demo 3: Loop Example ===\n")
        vm.reset()
        vm.load_program(LOOP_PROGRAM)
        vm.run()
        
        print("\n\n=== Demo 4: Presence & Time Control ===\n")
        vm.reset()
        vm.set_sensor("OCCUPIED", 1)
        vm.set_sensor("TIME", 79200)  # 22:00
        vm.load_program(PRESENCE_TIME_PROGRAM)
        vm.run()
        
        print("\n\n=== Demo 5: Dehumidification (Humidity = 75%) ===\n")
        vm.reset()
        vm.set_sensor("HUMIDITY", 75)
        vm.load_program(DEHUMIDIFY_PROGRAM)
        vm.run()
