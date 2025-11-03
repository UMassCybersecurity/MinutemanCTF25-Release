from pioemu import emulate

TARGET_PIN = 2 # GPIO to generate square wave on
TARGET_TOGGLE_CYCLES = 50 # clock cycles before pin should switch
TARGET_CYCLES = 10 # Number of cycles before PIO is considered successful

CYCLE_LIMIT = TARGET_TOGGLE_CYCLES * TARGET_CYCLES * 2 + 50 # Generous limit
TARGET_PIN_MASK = 0b1 << TARGET_PIN

def run_program(opcodes: list[int], clk_limit = CYCLE_LIMIT) -> bool:
  generator = emulate(opcodes, stop_when=lambda _, state: state.clock > clk_limit)
  last_cycle_time = 0
  valid_cycles = 0

  for before, after in generator:
      # Ensure target pin is set
      if not after.pin_directions & TARGET_PIN_MASK:
          continue
      
      if before.pin_values & TARGET_PIN_MASK != after.pin_values & TARGET_PIN_MASK:
        # toggle
        diff = after.clock - last_cycle_time
        last_cycle_time = after.clock
        if diff != TARGET_TOGGLE_CYCLES:
          valid_cycles = 0
          continue

        valid_cycles += 1
        if valid_cycles == TARGET_CYCLES:
          return True
    
  return False

if __name__ == "__main__":
  from adafruit_pioasm import assemble
  program = """
.program toggle
set pindirs, 4
loop:
set pins, 4 [31]
nop [17]
set pins, 0 [31]
nop [16]
jmp loop
"""
  print(run_program(assemble(program)))
