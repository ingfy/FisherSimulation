import simulation.simulation as simulation
import sys
import simulation.util as util
import simulation.phases as phases

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
        rounds = 0
        steps = 1
        reports = []
        prev_phase = None
        while True:            
            current_phase = self.simulation.get_current_phase()            
            new_round = current_phase == "COASTPLAN" and prev_phase == "LEARNING"
            if rounds == 0:
                steps -= 1
            else:
                if new_round:
                    rounds -= 1
            if rounds == 0 and steps == 0:
                if len(reports) > 0:
                    print "Rounds done."
                    report_mode = get_report_mode()
                    if report_mode == "all":
                        for r in reports:
                            print_phase_report(r)
                        print map_to_string(self.simulation_info.map)
                    elif report_mode == "last":
                        print_phase_report(reports[-1])
                        print map_to_string(self.simulation_info.map)
                else:
                    print map_to_string(self.simulation_info.map)
                # else do nothing
                
                reports = []
                print "Next phase: %s" % current_phase
                rounds, steps = get_numer_of_iterations()
            print "Current phase: %s" % current_phase
            result = self.simulation.step()
            reports.append(result)            
            
            print result.data
            
            # modify map
            self.simulation_info.map.grid = util.update_map(
                self.simulation_info.map.grid, result.map.grid
            )
            prev_phase = result.phase

    def exit(self):
        # save log and stuff        
        print "Simulation finished."
        print map_to_string(self.simulation_info.map)

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
    header = "M A P"
    if include_symbols:
        header += ", symbols:\n" + \
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
            
            if slot.fisherman:
                modifier = str(slot.num_fishermen) if \
                    slot.num_fishermen <= 9 else "+"
            else:
                modifier = "*" if slot.spawning else " "
                
            cell.append(modifier)
            line.append("".join(cell))
        lines.append(" ".join(line))
    return header + "\n" + "\n".join(lines)
        
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
        
def get_report_mode():
    try:
        return {"E": "all", "L": "last", "N": None}[input_or_default(
            "Reporting how much? (E)verything, (L)ast phase, or (N)othing?",
            "L"
        )]
    except KeyboardInterrupt:
        raise
    except:
        print "Invalid format."
        return get_report_mode()

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
        return get_numer_of_iterations()
        
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