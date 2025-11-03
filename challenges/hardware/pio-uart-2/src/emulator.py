from pioemu import emulate, State

import queue

import random
import logging
from io import StringIO

UART_RX_PIN = 0 # The pin the incoming UART signal is connected to
UART_RTS_PIN = 1 # The pin the RTS signal is connected to
UART_CYCLE_RATE = 8 # Number of PIO cycles between each UART bit (Like inverse BAUD rate)
UART_VALID_BYTES_COUNT = 10 # Number of valid bytes to receive before stopping

UART_RTS_ACTIVE_RANGE = (400, 600) # Range of possible number of cycles to hold RTS high
UART_RTS_INACTIVE_RANGE = (100, 300) # Range of possible number of cycles to hold RTS low

MAX_CYCLES = 2500

class UARTClient:
    def __init__(self, rx_pin: int, rts_pin: int, cycle_rate: int, logger: logging.Logger, rts_grace: int, rts_active_range: tuple[int, int], rts_inactive_range: tuple[int, int]) -> None:
        """
        UART Client that will read UART data from the specified RX pin and manage RTS on the specified RTS pin.
        
        :param rx_pin: The pin number for RX (should be attached to TX of the pico)
        :param rts_pin: The pin number for RTS (should be attached to CTS of the pico)
        :param cycle_rate: Number of PIO cycles between each UART bit
        :param logger: Logger to use for logging messages
        :param rts_grace: Number of cycles client will still accept data after RTS is deasserted
        :param rts_active_range: Range of possible number of cycles to hold RTS high
        :param rts_inactive_range: Range of possible number of cycles to hold RTS low
        """
        self.transmission_start = 0 # When the start bit is received
        self.data = 0 # Current data
        self.rts_switch_time = 0 # Cycle when RTS should be switched
        self.rts_grace_end = 0 # Cycle when data will stop being accepted after RTS deassertion
        self.rts_state = False # Current RTS state
        self.last_bit_received = -1 # Last bit index received

        self.rx_pin = rx_pin
        self.rts_pin = rts_pin
        self.cycle_rate = cycle_rate
        self.rts_grace = rts_grace
        self.rts_active_range = rts_active_range
        self.rts_inactive_range = rts_inactive_range
        
        self.logger = logger.getChild("UART")
        
        self.byte_history = queue.Queue()

        assert self.cycle_rate > 0
        assert self.rx_pin >= 0
        assert self.rts_pin >= 0
        assert self.rts_pin != self.rx_pin
        assert self.rts_grace > 0

    def _reset(self) -> None:
        """ Reset the UART client state """
        self.transmission_start = 0
        self.last_bit_received = -1 # start bit is -1
        self.data = 0

    def update(self, state: State) -> None:
        pin_state = state.pin_values

        # We are not currently in a transmission
        if self.transmission_start == 0:
            # Check for start of new transmission
            if (pin_state & (1 << self.rx_pin)) == 0:
                # start bit detected
                self.logger.info(f"[CLK {state.clock}] Start bit detected")

                # discard if RTS pin is low and we are not in grace period
                if (pin_state & (1 << self.rts_pin)) == 0 and state.clock > self.rts_grace_end:
                    self.logger.warning(f"[CLK {state.clock}] RTS pin low and grace period ended, ignoring transmission")
                    return

                # New transmission started!
                self.transmission_start = state.clock
            return

        # We are in an active transmission
        bit_index = (state.clock - self.transmission_start) // self.cycle_rate - 1
        if bit_index == self.last_bit_received:
            # No new bit to read yet
            return
        
        if bit_index - self.last_bit_received > 1:
            # missed bit(s), discard byte
            self.logger.error(f"[CLK {state.clock}] Missed bit(s) (your program may be stalling for too long!), discarding byte")
            self._reset()
            return
        
        if bit_index < 8:
            # reading data bits
            bit = (pin_state >> self.rx_pin) & 1
            self.data |= (bit << bit_index)
            self.last_bit_received = bit_index
            self.logger.debug(f"[CLK {state.clock}] Read bit {bit_index}: {bit}")
        elif bit_index == 8:
            # parity bit
            parity = 0
            for i in range(8):
                parity ^= (self.data >> i) & 1
            bit = (pin_state >> self.rx_pin) & 1
            if bit == parity: # We are using even parity
                self.logger.info(f"[CLK {state.clock}] Parity bit correct")
                self.last_bit_received = bit_index
            else:
                self.logger.warning(f"[CLK {state.clock}] Parity bit incorrect, discarding byte")
                self._reset()
        else:
            # stop bit
            bit = (pin_state >> self.rx_pin) & 1
            if bit == 1:
                self.logger.info(f"[CLK {state.clock}] Stop bit correct, received byte: {self.data:08b} ({self.data})")
                self.byte_history.put(self.data)
            else:
                self.logger.warning(f"[CLK {state.clock}] Stop bit incorrect, discarding byte")
            self._reset()

    def pin_input_source(self, state: State) -> int:
        pin_state = state.pin_values

        # Manage RTS pin
        if state.clock >= self.rts_switch_time:
            if self.rts_state:
                # currently high, switch to low
                self.rts_switch_time = random.randint(*self.rts_inactive_range) + state.clock
                self.rts_grace_end = state.clock + self.rts_grace
                self.rts_state = False
                pin_state &= ~(1 << self.rts_pin)
                self.logger.info(f"[CLK {state.clock}] RTS deasserted")
            else:
                # currently low, switch to high
                self.rts_switch_time = random.randint(*self.rts_active_range) + state.clock
                self.rts_state = True
                pin_state |= (1 << self.rts_pin)
                self.logger.info(f"[CLK {state.clock}] RTS asserted")
        
        return pin_state

def run_emulator(opcodes: list[int], max_cycles: int = MAX_CYCLES) -> tuple[bool, str]: 
    """
    Run the users opcodes in the emulator and return True if successful (give flag) along with log messages
    
    :param opcodes: List of opcodes to run in the emulator
    :param max_cycles: Maximum number of cycles to run the emulator for
    """

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("Emulator")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    uart_client = UARTClient(UART_RX_PIN, UART_RTS_PIN, UART_CYCLE_RATE, logger, UART_CYCLE_RATE * 2, UART_RTS_ACTIVE_RANGE, UART_RTS_INACTIVE_RANGE)
    byte_history = []

    logger.info("Starting emulation")
    emulator = emulate(opcodes, stop_when=lambda _, state: state.clock > max_cycles, input_source=uart_client.pin_input_source)
    valid_bytes = 0

    for before, after in emulator:
        # logger.debug(f"[CLK {before.clock}] Pin state after: {after.pin_values:08b}")
        if len(after.transmit_fifo) == 0:
            new_byte = random.randint(0, 255)
            logger.info(f"[CLK {after.clock}] Sending new byte: {new_byte:08b} ({new_byte})")
            after.transmit_fifo.append(new_byte)
            byte_history.append(new_byte)
        
        uart_client.update(after)

        if not uart_client.byte_history.empty():
            byte = uart_client.byte_history.get()
            if valid_bytes == 0:
                # Try to find first matching byte in history and discard earlier bytes
                for i in range(len(byte_history)):
                    if byte_history[i] == byte:
                        logger.debug(f"Found first matching byte in generation history at index {i}, discarding earlier bytes")
                        byte_history = byte_history[i:]
                        break
            
            # Match against expected byte
            if len(byte_history) and byte == byte_history[0]:
                valid_bytes += 1
                byte_history.pop(0)
                logger.info(f"Valid byte {valid_bytes}/{UART_VALID_BYTES_COUNT} received!")
                if valid_bytes >= UART_VALID_BYTES_COUNT:
                    logger.info("Received all valid bytes!")
                    return True, stream.getvalue()
            else:
                logger.warning(f"Invalid byte received, resetting valid byte count")
                valid_bytes = 0
    
    logger.info("Emulator finished without receiving enough valid bytes")
    return False, stream.getvalue()

if __name__ == "__main__":
    from adafruit_pioasm import assemble

    program = """
.program uart_tx

; initialize
set pindirs, 1 ; Set pin as output
set pins, 1   ; Idle high

.wrap_target:
    
.wrap
"""
    
    print(run_emulator(assemble(program))[0])