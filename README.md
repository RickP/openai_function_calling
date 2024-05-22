# openai_function_calling

A command line client for the OpenAI API with local function calling.

## Installation

    pip install -r requirements.txt

## Configuration

You need either an environment variable OPENAI_API_KEY or set your API key in assistant.py (variable openai_api_key).
You can also change the model to use in this file (variable model).

## Functions

You can add functions to the functions.py file. A function has to be in this form including the '@generate_json' decorator.
The comment is used to create the description for the OpenAI model so be verbose about what is does.
There are also some examples in the functions.py file. The OpenAI Model will call your function with the parameters you defined.

'''
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
'''

## Usage

    python assistant.py

If you make changes to your functions.py you need to reconfigure the assistant on openAI with:

    python assistant.py -r

As there is a function that can get the weather for a latitude and longitude try a prompt like:
"What is the weather in Berlin next Saturday?". The model will figure out how to invoke the local function and use it to answer the question.