import json
import re
from itertools import groupby

BUS_DATA = 'input'  # if "input" then, receive from stdin, else, from file declared here
DUMP_FILE = "bus.json"  # given a path, will dump the data to a file

stop_name_match = re.compile(r"([A-Z]\w*\s){1,2}(Road|Avenue|Boulevard|Street)(?! )")
stop_type_match = re.compile(r"\b[SFO]\b")
stop_time_match = re.compile(r"(^0\d:[0-5]\d$)|(^1\d:[0-5]\d$)|(^2[0-3]:[0-5]\d$)")


class Fleet:

    def __init__(self):
        self.buses = []

    def add_bus(self, bus):
        self.buses.append(bus)

    def import_data(self, file_name):
        if file_name == "input":
            data = json.loads(str(input()))
            for bus in data:
                self.add_bus(bus)
        else:
            with open(file_name, 'r') as f:
                data = json.load(f)
                for bus in data:
                    self.add_bus(bus)

        if DUMP_FILE:
            with open(DUMP_FILE, 'w') as f:
                json.dump(data, f, indent=4)

    def show(self):
        for x in self.buses:
            print(x["bus_id"], x["stop_id"], x["stop_name"], x["stop_type"], x["a_time"])

    def check_data(self):
        """checking data with regex for correct typing"""
        errors = [0] * 3
        for x in self.buses:
            if x["stop_name"] == "" or type(x["stop_name"]) != str:
                errors[0] += 1
            elif stop_name_match.match(x["stop_name"]) is None:
                errors[0] += 1

            if len(x["stop_type"]) > 0:
                if stop_type_match.search(x["stop_type"]) is None:
                    errors[1] += 1

            if x["a_time"] == "" or type(x["a_time"]) != str:
                errors[2] += 1
            else:
                if stop_time_match.match(x["a_time"]) is None:
                    errors[2] += 1

        print("""Type and required field validation: {} errors
stop_name: {}
stop_type: {}
a_time: {}""".format(sum(errors), *errors))

    def line_stops(self):
        """function for listing line_stops"""
        group = []

        # inner to outer loop: sort by id, then separate by id
        for _, bus in groupby(sorted(self.buses, key=lambda i: i["bus_id"]), lambda k: k["bus_id"]):
            group.append(list(bus))

        # create list for stops with different memory addresses
        lines = [[] for x in range(len(group))]

        # store ids for printing
        ids = [group[i][0]["bus_id"] for i in range(len(group))]

        # store all of the stop values in list
        for bus in group:
            for x in bus:
                lines[group.index(bus)].append(x["stop_id"])

        # only unique values inside lines
        for x in range(len(lines)):
            lines[x] = set(lines[x])

        print("Line names and number of stops:")
        for x in range(len(lines)):
            print("Line {}: {} stops".format(ids[x], len(lines[x])))

    def bus_schedule_check(self):
        # TODO: find a more efficient way to separate S, F and transfer stops
        """function for checking bus start, end line and stops"""
        # add lists for stop types
        start = []
        transfer = []
        final = []

        # sort by bus id
        group = sorted(self.buses, key=lambda i: i["bus_id"])

        # separate by bus id
        group = [list(x) for _, x in groupby(group, lambda k: k["bus_id"])]

        # create list for all the unique street names
        streets = set([x["stop_name"] for x in self.buses])

        # from each line add start stop and final stop to stop type lists
        for buses in group:
            for x in buses:
                if x["stop_type"] == "S":
                    start.append((x["bus_id"], x["stop_name"]))
                elif x["stop_type"] == "F":
                    final.append((x["bus_id"], x["stop_name"]))

        # if bus is missing start or end line, print error
        for buses in group:
            for bus in buses:
                if bus["stop_type"] == "S" and bus["stop_name"] not in [x[1] for x in start]:
                    print("There is no start or end stop for the line: {}.".format(bus["bus_id"]))
                    return
                if bus["stop_type"] == "F" and bus["stop_name"] not in [x[1] for x in final]:
                    print("There is no start or end stop for the line: {}.".format(bus["bus_id"]))
                    return
            types = [x["stop_type"] for x in buses]
            if "S" not in types or "F" not in types:
                print("There is no start or end stop for the line: {}.".format(bus["bus_id"]))
                return

        # if a non-transfer stop is in transfer list, remove it
        for x in streets:
            n_buses = 0
            for buses in group:
                if x in [y["stop_name"] for y in buses]:
                    n_buses += 1
                    continue
            if n_buses > 1:
                transfer.append(x)

        # to assure no street name appear more than once
        start = sorted(set([x[1] for x in start]))
        transfer = sorted(set(transfer))
        final = sorted(set([x[1] for x in final]))

        # print results
        print("Start stops: {}".format(len(start)), list(start))
        print("Transfer stops: {}".format(len(transfer)), list(transfer))
        print("Final stops: {}".format(len(final)), list(final))


if __name__ == '__main__':
    fleet = Fleet()
    fleet.import_data(BUS_DATA)
    fleet.bus_schedule_check()
