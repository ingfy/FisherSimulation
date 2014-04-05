import simulation
import sys
import phases

class CommandLineInterface(object):
    def __init__(self):
        self.simulation = simulation.Simulation()
        self.simulation_info = None

    def start(self):
        config_filename = input_or_default(
            "Configuration file?", self.simulation.get_default_config_filename()
        )
        self.simulation.setup_config(filename=config_filename)
        print "Configuration setup finished."
        print "Simulation ready to start."
        raw_input("Press Enter to initialize.")
        self.simulation_info = self.simulation.initialize()
        print "Initialization OK."
        print map_to_string(self.simulation_info.map)
        print "Simulation started."
        self.run_phases()
        
    def run_phases(self):
        new_round = False
        rounds = steps = 0
        reports = []
        while True:
            current_phase = self.simulation.get_current_phase()            
            if rounds == 0 and steps == 0:
                for r in reports:
                    print_phase_report(r)
                print map_to_string(self.simulation_info.map)
                reports = []
                print "Current phase: %s" % current_phase
                rounds, steps = get_numer_of_iterations()
            if rounds == 0:
                steps -= 1
            else:
                if new_round:
                    rounds -= 1
            
            result = self.simulation.step()
            reports.append(result)
            new_round = result.new_round
            
            # modify map
            self.simulation_info.map.grid = update_map(
                self.simulation_info.map.grid, result.map.grid
            )

    def exit(self):
        print "Simulation finished."
        print map_to_string(self.simulation_info.map)
        
def update_map(old, updates):
    return [[old_cell if new_cell is None else new_cell 
        for (old_cell, new_cell) in zip(*row)] 
            for row in zip(old, updates)]

map_symbol_explanations = [
    "[L]and",
    "[F]isherman",
    "[A]quaculture",
    "[B]locked",
    "[ ] for empty"
]
map_modifier_explanations = [
    "* means good fishing (spawning)"
]
def map_to_string(map, include_symbols=True):
    str = "M A P"
    if include_symbols:
        str += ", symbols:\n" + \
            "\t" + ", ".join(map_symbol_explanations) + ".\n" + \
            "\tModifiers: " + ", ".join(map_modifier_explanations) + "."
    r_num = 0
    lines = ["   " + "".join("%02d " % n for n in xrange(len(map.grid)))]
    for r in map.grid:
        line = ["%02d" % r_num]
        r_num += 1
        for slot in r:
            cell = []
            if slot.land:
                cell.append("L")
            elif slot.aquaculture:
                cell.append("A")
            elif slot.blocked:
                cell.append("B")
            elif slot.fisherman:
                cell.append("F")
            else:
                cell.append(" ")
            modifier = "*" if slot.spawning else " "
            cell.append(modifier)
            line.append("".join(cell))
        lines.append(" ".join(line))
    return str + "\n" + "\n".join(lines)
        
def print_phase_report(phase_report):
    print "Phase: %s" % phase_report.phase
    print "Messages:\n%s" % "\n\t".join([str(m) for m in phase_report.messages])
    changed_cells = []
    for x in xrange(len(phase_report.map.grid)):
        for y in xrange(len(phase_report.map.grid[x])):
            if not phase_report.map.grid[x][y] is None:
                changed_cells.append(((x, y), phase_report.map.grid[x][y]))
    print "Cells changed:%s" % (" NONE" if len(changed_cells) == 0 else "")
    for ((x, y), cell) in changed_cells:
        print "Cell changed at (%d, %d). Now: %s" % (x, y, cell)    
        
def get_numer_of_iterations():
    try:
        rounds, steps = (int(e) for e in input_or_default(
            "Run how many iterations? (<rounds>.<steps>, " +
                "ex. 4.2 for 4 complete rounds and 2 steps into the fifth.",
            "0.1"
        ).split("."))
        return rounds, steps
    except KeyboardInterrupt:
        raise
    except:
        print "Invalid format."
        get_numer_of_iterations()
        
def input_or_default(str, default):
    data = raw_input(str + " [%s] " % default)
    if data.lower() == "q": raise KeyboardInterrupt
    return data or default
        
def main():
    cli = CommandLineInterface()
    cli.start()
    cli.exit()
    
if __name__ == "__main__":
    sys.exit(main())