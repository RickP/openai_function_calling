# OpenAI local function calling template

A command line client for the OpenAI API with local [function calling](https://platform.openai.com/docs/guides/function-calling).
It serves as an extended example on how to implement this for OpenAI assistants. I used this as a base for my text-based home automation controller with functions that control things like lights and my sonos system on [this device](https://hackaday.io/project/196223-post-apocalyptic-terminal).

This code automatically generates an assistant with the function definitions for python functions in a file and creates a thread and a runner for the assistant. It uses the rich module to render formatted markdown of the responses and also calls the defined functions when the model wants to execute them and returns the results of the functions to the model.

## Structure

The project consists of 3 python files

- assistant.py - The main file that creates the assistant and starts the thread and runner.
- functions.py - The file that contains the functions that are callable by the model.
- generate_json.py - The decorator that creates the json from the functions in functions.py to configure the OpenAI assistant.

## Installation

    pip install -r requirements.txt

If arrow keys don't work as expected when inputting text you also need the 'readline' or 'gnureadline' packages. 
They should be installed via your systems package manager (apt, brew, etc.).

## Configuration

You need either an environment variable OPENAI_API_KEY or set your API key in assistant.py (variable openai_api_key).
You can also change the model to use in this file (variable model). There is also a setting for the system prompt (assistant_instructions).

## Functions

You can add functions to the functions.py file. A function has to be in this form including the '@generate_json' decorator.
The comment is used to create the description for the OpenAI model so be verbose about what is does.
There are also some examples in the functions.py file. The OpenAI Model will call your function with the parameters you defined.

```
@generate_json
def add_numbers(number_a: int, number_b: int, operation: str = 'add') -> int:
    """Returns the sum of two numbers
    :param number_a: int: The first number
    :param number_b: int: The second number
    :param operation: string: The operation to perform (add or multiply)
    Must be one of: "add", "multiply"
    Default: "add"
    """
    if operation == 'add':
        return number_a + number_b
    else:
        return number_a * number_b
```

## Usage

    python assistant.py

Type "exit" or "quit" to get out.

If you make changes to your functions.py or your assistant config (e.g. model or system prompt) you need to reconfigure the assistant on OpenAI with:

    python assistant.py -r

You can check the correctness of the function definitions on the [OpenAI developer website](https://platform.openai.com/assistants)

As there is an example function that can get the weather for a latitude and longitude try a prompt like:
"What is the weather in Berlin next Saturday?". The model will figure out how to invoke the local function and use it to answer the question.

## ToDo

Scrolling up does not really work on longer responses (Text get's repeated).
Pull requests are welcome.
