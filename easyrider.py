import json
import re

BUS_DATA = 'input'  # if "input" then, receive from stdin, else, from file declared here
DUMP_FILE = ""  # given a path, will dump the data to a file


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
            print(x.bus_id, x.stop_id, x.stop_name, x.next_stop, x.stop_type, x.a_time)

    def check_data(self):
        errors = [0] * 6  # respectively by self.Bus class order
        for x in self.buses:
            if x["bus_id"] == "" or type(x["bus_id"]) != int:
                errors[0] += 1
            if x["stop_id"] == "" or type(x["stop_id"]) != int:
                errors[1] += 1
            if x["stop_name"] == "" or type(x["stop_name"]) != str:
                errors[2] += 1
            if x["next_stop"] == "" or type(x["next_stop"]) != int:
                errors[3] += 1
            if type(x["stop_type"]) != str or len(x["stop_type"]) > 1:
                errors[4] += 1
            if x["a_time"] == "" or type(x["a_time"]) != str:
                errors[5] += 1
            else:
                if re.match(r'\d\d?:\d\d', x["a_time"]) is None:
                    errors[5] += 1
        print("""Type and required field validation: {} errors
bus_id: {}
stop_id: {}
stop_name: {}
next_stop: {}
stop_type: {}
a_time: {}""".format(sum(errors), *errors))


if __name__ == '__main__':
    fleet = Fleet()
    fleet.import_data(BUS_DATA)
    fleet.check_data()
