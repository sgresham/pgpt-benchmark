import argparse
import requests
import json
import time

def query_api(api_data, hostname="localhost", port=8001, verbose=False):
    results = []

    for api_entry in api_data:
        match api_entry['api']:
            case 'completions':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {
                    "Content-Type": "application/json"
                }

                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    with requests.post(url, json=params, headers=headers, verify=False, stream=params["stream"]) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    line = line.decode().strip()
                                    if line == "data: [DONE]":
                                        break
                                    elif line.startswith("data:"):
                                        try:
                                            parsed_data = json.loads(line[5:])
                                            if 'choices' in parsed_data and len(parsed_data['choices']) > 0:
                                                delta = parsed_data['choices'][0]['delta']
                                                if 'content' in delta:
                                                    if verbose:
                                                        print(delta['content'])
                                        except json.decoder.JSONDecodeError:
                                            print("Error decoding JSON:", line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["prompt"], "time_elapsed": elapsed_time})
            case 'chat/completions':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {
                    "Content-Type": "application/json"
                }
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    with requests.post(url, json=params, headers=headers, verify=False, stream=params["stream"]) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    line = line.decode().strip()
                                    if line == "data: [DONE]":
                                        break
                                    elif line.startswith("data:"):
                                        try:
                                            parsed_data = json.loads(line[5:])
                                            if 'choices' in parsed_data and len(parsed_data['choices']) > 0:
                                                delta = parsed_data['choices'][0]['delta']
                                                if 'content' in delta:
                                                    if verbose:
                                                        print(delta['content'])
                                        except json.decoder.JSONDecodeError:
                                            print("Error decoding JSON:", line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})
            case 'ingest/file':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {}  # No need to specify Content-Type, requests will set it for multipart/form-data
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    files = {'file': open(params['file'], 'rb')}  # Assuming 'file' is the key containing the file path in params
                    with requests.post(url, files=files, data=params, headers=headers, verify=False) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    line = line.decode().strip()
                                    if line == "data: [DONE]":
                                        break
                                    elif line.startswith("data:"):
                                        try:
                                            parsed_data = json.loads(line[5:])
                                            if 'choices' in parsed_data and len(parsed_data['choices']) > 0:
                                                delta = parsed_data['choices'][0]['delta']
                                                if 'content' in delta:
                                                    if verbose:
                                                        print(delta['content'])
                                        except json.decoder.JSONDecodeError:
                                            print("Error decoding JSON:", line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})
            case 'ingest/list':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {}  
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    with requests.get(url, headers=headers, verify=False) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    line = line.decode().strip()
                                    if verbose:
                                        print(line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})
            case 'ingest/delete':
                url_base = f"http://{hostname}:{port}/v1/ingest/list"
                headers = {} 
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    with requests.get(url_base, headers=headers, verify=False) as response:
                        if response.status_code == 200:
                            data = response.json()  # Parse JSON response
                            for document in data["data"]:  # Iterate through the data
                                if document["doc_metadata"]["file_name"] == params["file"]:
                                    doc_id = document["doc_id"]
                                    url = f"http://{hostname}:{port}/v1/ingest/{doc_id}"
                                    # Send API request for each doc_id
                                    with requests.delete(url, headers=headers, verify=False) as delete_response:
                                        if delete_response.status_code == 200:
                                            print(f"Document with doc_id {doc_id} deleted successfully.")
                                        else:
                                            print(f"Failed to delete document with doc_id {doc_id}.")
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query API")
    parser.add_argument("--hostname", default="localhost", help="Hostname (default: localhost)")
    parser.add_argument("--port", type=int, default=8001, help="Port (default: 8001)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--file", default="data.json", help="test filename and path (default: data.json)")
    args = parser.parse_args()

    with open(args.file, "r") as file:
        api_data = json.load(file)

    query_results = query_api(api_data, args.hostname, args.port, args.verbose)
    for result in query_results:
        print(f"Time elapsed for prompt {result['prompt']}: {result['time_elapsed']} seconds")