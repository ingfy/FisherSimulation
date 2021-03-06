import sys
import numpy
from FisherSimulation import entities
from time import strftime

default_filename = "log.txt"
vote_fitness_relation_filename = "vfr.csv"
sep = ","

class LogMessage(object):
    def __init__(self, timestamp, text):
        self.date = strftime("%Y-%m-%d %H:%M:%S")
        self.timestmap = timestamp
        self.text = text

    def __str__(self):
        return "[%(date)s] <%(timestamp)> %(text)" % {
            "date": self.date,
            "timestamp": self.timestamp,
            "text": self.text
        }

class LogEvent(object):
    pass

class RoundStatistics(LogEvent):
    filename = "round_statistics.csv"

    def __init__(self, num, average_fitnesses, avg_num_complaints,
        num_unblocked_cells, num_aquacultures):
        self.num = num
        self.average_fisherman_fitness = average_fitnesses["fisherman"]
        self.avg_num_fisherman_complaints = avg_num_complaints["fisherman"]
        self.num_unblocked_cells = num_unblocked_cells
        self.num_aquacultures = num_aquacultures

    attrs_format = [
        ("num", "d"),
        ("average_fisherman_fitness", "f"),
        ("avg_num_fisherman_complaints", ".2f"),
        ("num_unblocked_cells", "d"),
        ("num_aquacultures", "d")
    ]

    def to_csv_line(self):
        line = sep.join(["%" + ("(%s)%s" % (a, f))
            for a, f in self.attrs_format]) + "\n"

        return line % {
            label: getattr(self, label) for label, __ in self.attrs_format
        }

    @classmethod
    def headers(c):
        return sep.join([label for label, __ in c.attrs_format]) + "\n"


class VoteFitnessRelation(LogEvent):
    def __init__(self, agent):
        self.agent = agent

    def add_vote(self, num_complaints):
        self.num_complaints = num_complaints

    def add_fitness(self, fitness):
        self.fitness = fitness

class StatisticsLogger(object):
    FILENAME = "statistics.csv"

    def __init__(self):
        self._statistics = {}    # round to data, data is {fieldname: value}
        self._fields = ["round"]
        self._written_fields = ["round"]

    def write_round(self, round):
        if len(self._written_fields) < len(self._fields):
            # If we discover a new field that has never been written before,
            # delete the old file and add a new header line with all the fields
            with open(StatisticsLogger.FILENAME, "w") as file:
                file.write(StatisticsLogger.to_headers_line(self._fields))
            self._written_fields = self._fields
            for r in self._statistics:
                self.write_round(r)
        else:
            line = StatisticsLogger.to_columns(
                self._statistics[round],
                self._fields
            )
            with open(StatisticsLogger.FILENAME, "a") as file:
                file.write(line)

    def add_phase_statistics(self, round, data):
        for key in data:
            if not key in self._fields:
                self._fields.append(key)
            if not round in self._statistics:
                self._statistics[round] = {}
                self._statistics[round]["round"] = round
            
            value = data[key]["value"]
            if not key in self._statistics[round]:
                self._statistics[round][key] = 0.0
            if data[key].get("mode", "add") == "add":
                self._statistics[round][key] += value
            else:
                self._statistics[round][key] = value

    @classmethod
    def to_headers_line(cls, fields):
        return ",".join(f.replace(",", "") for f in fields) + "\n"

    @classmethod
    def to_columns(cls, statistics, keys):
        def f(e): return "%.10f" % e if e is not None else ""
        return ",".join(f(statistics.get(key, None)) for key in keys) + "\n"


class Logger(StatisticsLogger):
    def __init__(self, filename):
        StatisticsLogger.__init__(self)
        self.filename = filename
        self.vote_fitness_relations = {}
        with open(vote_fitness_relation_filename, "w") as file:
            file.write("round,agent,num_complaints,fitness\n")
        with open(RoundStatistics.filename, "w") as file:
            file.write(RoundStatistics.headers())

    def log(self, message):
        with open(filename, "a") as file:
            file.write("%s\n" % str(message) + "\n")

    def write_round_statistics(self, round, world, aquacultures):
        statistics = RoundStatistics(
            round,
            {
                "fisherman": numpy.mean(
                    [self.vote_fitness_relations[round][a].fitness
                        for a in self.vote_fitness_relations[round]
                        if a.__class__ == entities.Fisherman])
            },
            {
                "fisherman": numpy.mean(
                    [self.vote_fitness_relations[round][a].num_complaints
                        for a in self.vote_fitness_relations[round] if
                        getattr(self.vote_fitness_relations[round][a],
                            "num_complaints", None) is not None and
                        a.__class__ == entities.Fisherman])
            },
            len([c for c in world.get_all_cells() if not c.is_blocked()]),
            len(aquacultures)
        )
        with open(RoundStatistics.filename, "a") as file:
            file.write(statistics.to_csv_line())

    def save_vote_fitness_relation(self, round, agent):
        line = "%(round)d,%(agent)s,%(num_complaints)d,%(fitness)f\n"
        rel = self.vote_fitness_relations[round][agent]
        text = line % {
            "round":            round,
            "agent":            agent.get_id(),
            "num_complaints":   rel.num_complaints,
            "fitness":          rel.fitness
        }
        with open(vote_fitness_relation_filename, "a") as file:
            file.write(text)

    def add_fitness(self, round, agent, fitness):
        if agent in self.vote_fitness_relations[round]:
            self.vote_fitness_relations[round][agent].add_fitness(fitness)
            if not getattr(self.vote_fitness_relations[round][agent],
                "num_complaints", None) is None:
                self.save_vote_fitness_relation(round, agent)

    def add_vote(self, round, agent, num_complaints):
        if agent in self.vote_fitness_relations[round]:
            self.vote_fitness_relations[round][agent].add_vote(num_complaints)

    def vote_fitness_relation(self, round, agent):
        if not round in self.vote_fitness_relations:
            self.vote_fitness_relations[round] = {}
        self.vote_fitness_relations[round][agent] = VoteFitnessRelation(agent)

    @classmethod
    def new(c):
        return c(default_filename)