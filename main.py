import argparse
import requests
import json
import time

def query_api(api_data, hostname="localhost", port=8001, verbose=False, debug=False):
    results = []
    previous_messages = ''

    for api_entry in api_data:
        match api_entry['api']:
            #
            # Completions, not often used.
            #
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
            #
            # chat/completions, the appropriate way to query privateGPT
            #
            case 'chat/completions':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                full_response = ""
                user_message = ""
                headers = {
                    "Content-Type": "application/json"
                }
                for params in api_entry['queries']:
                    full_response = ""
                    user_message = ""
                    for message in params["messages"]:
                        if message["role"] == "user":
                            user_message = message["content"]
                            if params['persistent']:
                                message["content"] += "\n" + previous_messages
                            if debug:
                                print(f"###Full context fed to LLM###\n {message['content']} \n ###End of Full Context### \n")
                    start_time = time.time()  # Record start time
                    with requests.post(url, json=params, headers=headers, verify=False, stream=params["stream"]) as response:
                        if response.status_code == 200:
                            if verbose:
                                print(f"USER_MESSAGE: {user_message}\n")
                            for line in response.iter_lines():
                                if line:
                                    if line.startswith(b"data:"):
                                        line = line[len(b"data:"):].strip()
                                    if line == b"[DONE]":
                                        print("\nAPI RESPONSE COMPLETED\n\n")
                                        break
                                    if params["stream"]:
                                        try:
                                            parsed_data = json.loads(line)
                                            content_text = parsed_data['choices'][0]['delta']['content']
                                            if verbose:
                                                print(content_text, end="")
                                            if params['persistent']:
                                                full_response  += content_text
                                        except json.decoder.JSONDecodeError:
                                            print("Error decoding JSON:", line)
                                        except KeyError:
                                            print("KeyError:", line)
                                    else:  # If stream is False, print the context data
                                        try:
                                            parsed_data = json.loads(line)
                                            content_text = parsed_data["choices"][0]["message"]["content"]
                                            if verbose:
                                                print(content_text)
                                            if params['persistent']:
                                                full_response  += content_text
                                        except json.decoder.JSONDecodeError:
                                            print("Error decoding JSON:", line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    if params['persistent']:
                        previous_messages += full_response # + user_message + ' '
                    results.append({"prompt": params["description"],
                                    "time_elapsed": elapsed_time
                                     })
            #
            # Ingest File
            #
            case 'ingest/file':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {}  # No need to specify Content-Type, requests will set it for multipart/form-data
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    files = {'file': open(params['file'], 'rb')}  # Assuming 'file' is the key containing the file path in params
                    with requests.post(url, files=files, data=params, headers=headers, verify=False) as response:
                        print('FILE INGESTED:',params['file'])
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})
            #
            # List ingested
            #
            case 'ingest/list':
                url = f"http://{hostname}:{port}/v1/{api_entry['api']}"
                headers = {}  
                for params in api_entry['queries']:
                    start_time = time.time()  # Record start time
                    with requests.get(url, headers=headers, verify=False) as response:
                        if response.status_code:
                            for line in response.iter_lines():
                                if line:
                                    line = line.decode().strip()
                                    if verbose:
                                        print(line)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"],
                                     "time_elapsed": elapsed_time,
                                     })
            #
            # Delete Ingest File/s. Will delete all files with same name.
            #
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
                                        print('what is the status', delete_response)
                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time
                    results.append({"prompt": params["description"], "time_elapsed": elapsed_time})

    return results

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
