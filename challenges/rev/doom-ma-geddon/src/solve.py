import angr
import claripy

# Load the binary
project = angr.Project("./doomageddon", auto_load_libs=False)

# Create a bitvector for the 50-byte flag
flag_len = 50
flag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(flag_len)]
flag = claripy.Concat(*flag_chars)

# Set up initial state with symbolic stdin
state = project.factory.full_init_state(
    args=["./doomageddon"],
    stdin=flag
)

# Constrain the input to printable characters (optional, but often useful)
for k in flag_chars:
    state.solver.add(k >= 0x20)
    state.solver.add(k <= 0x7e)

# Create simulation manager
simgr = project.factory.simulation_manager(state)

# Define win and lose addresses
win_addr = 0x4031b8
lose_addr = 0x4031c9

# Goat
simgr.one_active.options.add(angr.options.LAZY_SOLVES)

# Explore paths that reach win and avoid lose
simgr.explore(find=win_addr, avoid=lose_addr)


# Check if we found a solution
if simgr.found:
    found = simgr.found[0]
    solution = found.solver.eval(flag, cast_to=bytes)
    print("[+] Flag found:", solution)
else:
    print("[-] No solution found.")
