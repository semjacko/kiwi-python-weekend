# kiwi-python-weekend

**For a given flight data in a form of `csv` file (check the examples), prints out a structured list of all flight combinations for a selected route between airports A -> B, sorted by the final price for the trip.**

# Usage

solution \<dataset\> \<origin\> \<destination\> [options]...

# Required arguments

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `dataset`     | string  | Path to csv              |                              |
| `origin`      | string  | Origin airport code      |                              |
| `destination` | string  | Destination airport code |                              |

# Optional arguments

| Argument name   | short, long   | type    | Description                         | Notes                        |
|-----------------|---------------|---------|-------------------------------------|------------------------------|
| `bags`          | -b, --bags    | integer | Number of requested bags            | Optional (defaults to 0)     |
| `changes`       | -c, --changes | integer | Maximum number of changes           | Optional (defaults to 1)     |
| `min_days_stay` | -m, --mindays | boolean | Minimum days to stay in destination | Optional (defaults to 1)     |
| `max_days_stay` | -l, --maxdays | boolean | Maximum days to stay in destination | Optional (defaults to 10)    |
| `return`        | -r, --return  | boolean | Is it a return flight?              | Optional (defaults to false) |
