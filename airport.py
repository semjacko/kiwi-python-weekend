from datetime import datetime, timedelta

MIN_HOURS_STAY = 1
MAX_HOURS_STAY = 6


class Airport:

    def __init__(self, name):
        self.name = name
        self.flights = []

    def add_flight(
        self, 
        dest_airport, 
        flight_no, 
        departure, 
        arrival, 
        base_price, 
        bag_price, 
        bags_allowed
    ):
        flight = {
            'origin': self.name,
            'destination': dest_airport.name,
            'dest_airport': dest_airport,
            'flight_no': flight_no,
            'departure': departure,
            'arrival': arrival,
            'base_price': float(base_price),
            'bag_price': float(bag_price),
            'bags_allowed': int(bags_allowed)
        }
        self.flights.append(flight)

    def find_flights_to_destination(
        self, 
        dest_airport, 
        bags, 
        max_changes, 
        min_datetime_departure, 
        max_datetime_departure, 
        prev_flights
    ):
        '''
        Searches for all paths to the destination, taking the requirements into account

        Args:
            dest_airport (:class:`.Airport`): Object for the goal destination.
            bags (int): Number of bags.
            max_changes (int): Maximum number of changes.
            min_datetime_departure (datetime): The earliest flight to the goal destination.
            max_datetime_departure (datetime): The latest flight to the goal destination.
            prev_flights (list): List of previous flights.

        Returns:
            A list of possible paths from start to the goal destination, where path is list 
            of all flights from start to the goal destination for this particular path
        '''

        if self.name == dest_airport.name:
            return [prev_flights]

        if max_changes < 0:
            return []

        paths_to_destination = []

        for flight in self.flights:    # Iterate through all flights from this airport
            if not self.validate_flight(flight, bags, min_datetime_departure, max_datetime_departure, prev_flights):
                continue

            # Calculate next earliest and latest flight departure
            arrival = datetime.fromisoformat(flight['arrival'])
            next_min_datetime_departure = arrival + timedelta(hours=MIN_HOURS_STAY)
            next_max_datetime_departure = arrival + timedelta(hours=MAX_HOURS_STAY)

            # Get paths to destination and concatenate
            paths = flight['dest_airport'].find_flights_to_destination(dest_airport, bags, max_changes - 1, next_min_datetime_departure, next_max_datetime_departure, prev_flights + [flight])
            paths_to_destination += paths

        return paths_to_destination


    def validate_flight(
        self, 
        flight, 
        bags, 
        min_datetime_departure, 
        max_datetime_departure, 
        prev_flights
    ):
        # check bags limit
        if bags > flight['bags_allowed']:
            return False
        
        # check time limits
        departure = datetime.fromisoformat(flight['departure'])
        if not min_datetime_departure <= departure <= max_datetime_departure:
            return False
        
        # check if some of origins of prev_flights doesnt already contain destination of this flight
        for pf in prev_flights:
            if pf['origin'] == flight['destination']:
                return False

        return True
