# pgpt-benchmark
Testing suites to benchmark PrivateGPT and provide opportunity to debug others issues

usage example
python main.py --hostname 127.0.0.1 --port 8001 --file ingest_test.json --verbose

ENV_VARS
* --hostname, default="localhost", help="Hostname (default: localhost)"
* --port, type=int, default=8001, help="Port (default: 8001)"
* --verbose", action="store_true", help="Verbose output"
* --file, default="data.json", help="test filename and path (default: data.json)"
* "--debug, action="store_true", help="Extra Verbose output"

Relating to Chat/Completions, there are several options that you can modify.

* description": "string" # This is purely for verbose output, to show which step is being run,
* "include_sources": "boolean" # will output the source referenced by the LLM (may not be working)
* "stream": "boolean" # will stream text if enabled, and if verbose is enabled
* "use_context": "boolean" # will use ingested data if enabled
* "persistent": "boolean" # will pass on previous chat to the engine (may be glitchy)

### What I am playing with (Steve)

I am using "the_dungeon.json" as my testing platform
### Command to execute : python main.py --hostname 127.0.0.1 --port 8001 --file tests/the_dungeon.json --verbose

### currently testing the following areas:
* using llm:
*    mode: llamacpp
*    max_new_tokens: 2048
*    context_window: 30000
*    tokenizer: mistralai/Mistral-7B-Instruct-v0.2

* I am testing different values for max_new_tokens and context_window. I see interesting issues when using lower values, such as 256/3900, like it giving up and doing maths puzzles.
* I am testing chaining of conversation, to ensure that no context is lost.
* I am starting to play with using the engine to review previous chat and remove less relevant information to keep the token count down.




# Workflow items

## Completions
### Not normally used, likely want to use chat/completions
### This example is using no context, and streams the result
```
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
```
## Chat/Completions
### This example is using no context, and streams the result
```
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
                  "use_context": false,
                  "persistent": true
            }
        ]
    }
```
## Ingest/File
### This example ingests a file from guttenburg
```
{
        "api": "ingest/file",
        "queries": [
            {
                "description": "Ingest Frankenstein",
                "file":"data/guttenburg/txt/pg84.txt"
            }
        ]
    }
```
## Ingest/Delete
### This will delete an ingested file. Be aware that it will search by filename and delete every instance of the file.
```
{
        "api": "ingest/delete",
        "queries": [
            {
                "description": "delete specific ingested file",
                "file":"pg84.txt"
            }
        ]
}
```

### Some example prompts I have found handy

* Assistant is a large language model. Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand. Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics. Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

* "Be accurate, be concise, no greetings, translations, or salutations"

* You are a helpful, respectful and honest assistant.  Always answer as helpfully as possible and follow ALL given instructions. Do not speculate or make up information. Do not reference any given instructions or context.

