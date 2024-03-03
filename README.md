# pgpt-benchmark
Testing suites to benchmark PrivateGPT and provide opportunity to debug others issues

usage example
python main.py --hostname 127.0.0.1 --port 8001 --file ingest_test.json --verbose

ENV_VARS
--hostname", default="localhost", help="Hostname (default: localhost)"
--port", type=int, default=8001, help="Port (default: 8001)"
--verbose", action="store_true", help="Verbose output"
--file", default="data.json", help="test filename and path (default: data.json)"

test examples
These can be chained, for example, first ingest, then query, then remove ingest

## Completions
### Not normally used, likely want to use chat/completions
### This example is using no context, and streams the result

{
        "api": "completions",
        "queries": [
            {
                "description": "Count to 5 in Japanese, stream, no context",
                "include_sources": false,
                "prompt": "Count to 5 in Japanese",
                "stream": true,
                "system_prompt": "Be accurate, be concise, no greetings, translations, or salutations",
                "use_context": false
            }
        ]
    }

## Chat/Completions
### This example is using no context, and streams the result

{
        "api": "chat/completions",
        "queries": [
            {
                "description": "Count to 5 in Japanese, stream, no context",
                "include_sources": false,
                "messages": [
                    {
                      "content": "Be accurate, be concise, no greetings, translations, or salutations",
                      "role": "system"
                    },
                    {
                      "content": "Count to 5 in Japanese",
                      "role": "user"
                    }
                  ],
                  "stream": true,
                  "use_context": false
            }
        ]
    }

## Ingest/File
### This example ingests a file from guttenburg
{
        "api": "ingest/file",
        "queries": [
            {
                "description": "Ingest Frankenstein",
                "file":"data/guttenburg/txt/pg84.txt"
            }
        ]
    }

## Ingest/Delete
### This will delete an ingested file. Be aware that it will search by filename and delete every instance of the file.
{
        "api": "ingest/delete",
        "queries": [
            {
                "description": "delete specific ingested file",
                "file":"pg84.txt"
            }
        ]
}

