import argparse
import json
from query_api import query_api

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query API")
    parser.add_argument("--hostname", default="localhost", help="Hostname (default: localhost)")
    parser.add_argument("--port", type=int, default=8001, help="Port (default: 8001)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Extra Verbose output")
    parser.add_argument("--file", default="data.json", help="test filename and path (default: data.json)")
    args = parser.parse_args()

    with open(args.file, "r") as file:
        api_data = json.load(file)

    query_results = query_api(api_data, args.hostname, args.port, args.verbose, args.debug)
    for result in query_results:
        print(f"Time elapsed for prompt {result['prompt']}: {result['time_elapsed']} seconds")
