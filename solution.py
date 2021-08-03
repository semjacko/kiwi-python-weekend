#!/usr/bin/python

import sys, getopt, csv
from airport import Airport
import json
from datetime import datetime, timedelta


USAGE_STR = '\n\n USAGE:\n\n solution <input_csv> <origin> <destination> [-b BAGS_NUMBER] [-c MAX_CHANGES] [-m MIN_DAYS_STAY] [-l MAX_DAYS_STAY] [-r]\n\n'
MAX_DAYS_ERR = '\n Max days cannot be less than min days.\n If not specified, the default value for max days is 10.\n'
AIRPORTS_ERR = '\n One of these airports does not exist :(\n'
INPUT_FILE_ERR = '\n The input file either does not exist or is in the wrong format :(\n'


def find_paths(
    src_airport, 
    dest_airport, 
    bags, 
    max_changes, 
    min_days_to_stay,
    max_days_to_stay, 
    return_flight
):
    '''
    Searches for all possible paths to the destination and/or back to the source, 
    taking into account the requirements

    Args:
        src_airport (:class:`.Airport`): Object for the source airport.
        dest_airport (:class:`.Airport`): Object for the target destination.
        bags (int): Number of bags.
        max_changes (int): Maximum number of changes.
        min_days_to_stay (int): Minimum days to staying in destination.
        max_days_to_stay (int): Maximum days to staying in destination.
        return_flight (bool): Whether the flight is return.

    Returns:
        A list of dictionaries. Single dictionary represent full 
        path to the destination and/or back to the source:
            "path_to_destination" (list): list of flights to the destination for this path
            "path_to_source" (list): list of flights for way back to the source for this path
        
    '''
    # get paths to destination 
    # "min_datetime_departure" and "max_datetime_departure" are not specified by 
    # user but it is set automatically to datetime.min and datetime.max but it would
    # be easy to take them also as input  
    paths_to_destination = src_airport.find_flights_to_destination(dest_airport, bags, max_changes, datetime.min, datetime.max, [])

    if not return_flight:
        return [{
            'path_to_destination': p2d,
            'path_to_source': []
            } for p2d in paths_to_destination
        ]

    return_paths = []

    # for every path to destination find path to source
    for p2d in paths_to_destination:
        last_flight_to_destination = p2d[-1]
        arrival = datetime.fromisoformat(last_flight_to_destination['arrival'])
        min_datetime_departure = arrival + timedelta(days=min_days_to_stay)
        max_datetime_departure = arrival + timedelta(days=max_days_to_stay)

        paths_to_source = dest_airport.find_flights_to_destination(src_airport, bags, max_changes, min_datetime_departure, max_datetime_departure, [])
        
        for p2s in paths_to_source:
            return_paths.append({
                'path_to_destination': p2d,
                'path_to_source': p2s
            })
        
    return return_paths


def create_output(paths, path_bags_count):
    output = []

    for path in paths:

        path_flights = []
        path_total_price = 0
        path_bags_allowed = path['path_to_destination'][0]['bags_allowed']
        
        path_to_destination_begin = datetime.fromisoformat(path['path_to_destination'][0]['departure'])
        path_to_destination_end = datetime.fromisoformat(path['path_to_destination'][-1]['arrival'])
        path_travel_time = path_to_destination_end - path_to_destination_begin

        if len(path['path_to_source']) > 0:
            path_to_source_begin = datetime.fromisoformat(path['path_to_source'][0]['departure'])
            path_to_source_end = datetime.fromisoformat(path['path_to_source'][-1]['arrival'])
            path_travel_time += path_to_source_end - path_to_source_begin

        full_path = path['path_to_destination'] + path['path_to_source']

        for flight in full_path:
            
            path_flights.append({
                "flight_no": flight["flight_no"],
                "origin": flight["origin"],
                "destination": flight["destination"],
                "departure": flight["departure"],
                "arrival": flight["arrival"],
                "base_price": flight["base_price"],
                "bag_price": flight["bag_price"],
                "bags_allowed": flight["bags_allowed"]
            })

            path_total_price += flight["base_price"] + path_bags_count * flight["bag_price"]
            path_bags_allowed = min(path_bags_allowed, flight["bags_allowed"])

        output.append({
            "flights": path_flights,
            "bags_allowed": path_bags_allowed,
            "bags_count": path_bags_count,
            "destination": full_path[-1]['destination'],
            "origin": full_path[0]['origin'],
            "total_price": path_total_price,
            "travel_time": str(path_travel_time)
        })
    
    output.sort(key=lambda e:e['total_price'])

    return output


def create_airports(csv_filename):
    # Dictionary of airports
    airports = {}
    
    try:
        with open(csv_filename, 'r') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            
            for row in reader:
                flight_no = row[0]
                origin = row[1]
                destination = row[2]
                departure = row[3]
                arrival = row[4]
                base_price = row[5]
                bag_price = row[6]
                bags_allowed = row[7]
                
                if not airports.get(origin):
                    airports[origin] = Airport(origin)
                if not airports.get(destination):
                    airports[destination] = Airport(destination)
                    
                airports[origin].add_flight(airports[destination], flight_no, departure, arrival, base_price, bag_price, bags_allowed)
    except:
        print(INPUT_FILE_ERR)
        sys.exit(2)

    return airports


def main(argv):
    bags = 0
    max_changes = 1
    min_days_to_stay = 1
    max_days_to_stay = 10
    return_flight = False

    # Get arguments from command line
    try:
        csv_file = argv[0]
        origin = argv[1]
        destination = argv[2]
        opts, args = getopt.getopt(argv[3:], 'hb:c:d:l:r', ['bags=', 'changes=', 'mindays=', 'maxdays=', 'return'])
    except (IndexError, getopt.GetoptError):
        print(USAGE_STR)
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print(USAGE_STR)
            sys.exit()
        elif opt in ('-b', '--bags'):
            bags = int(arg)
        elif opt in ('-c', '--changes'):
            max_changes = int(arg)
        elif opt in ('-r', '--return'):
            return_flight = True
        elif opt in ('-d', '--mindays'):
            min_days_to_stay = int(arg)
        elif opt in ('-l', '--maxdays'):
            max_days_to_stay = int(arg)

    if max_days_to_stay < min_days_to_stay:
        print(MAX_DAYS_ERR)
        sys.exit(2)

    airports = create_airports(csv_file)

    try:
        origin_airport, destination_airport = airports[origin], airports[destination]
    except:
        print(AIRPORTS_ERR)
        sys.exit(2)

    paths = find_paths(origin_airport, destination_airport, bags, max_changes, min_days_to_stay, max_days_to_stay, return_flight)
    
    output = create_output(paths, bags)

    print(json.dumps(output, indent=4))


if __name__ == '__main__':
    main(sys.argv[1:])