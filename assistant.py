#!/usr/bin/env python3

import argparse
import json
import inspect
import os

from openai.types.beta.threads import Message, MessageDelta
from openai import AssistantEventHandler, OpenAI
from typing_extensions import override

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

# Implement your local functions in functions.py
import functions

# Try to import readline if possible
try:
    import readline                  
except ImportError:
    try:
        import gnureadline as readline                         
    except ImportError:
        pass

# assistant settings
assistant_name = "Function_Caller"
assistant_instructions = "You are a personal assistant that runs on the users command line. You call functions whenever needed."
model = "gpt-4o"
openai_api_key = "YOUR_OPENAI_API_KEY" # Can be omitted if you have the environment variable set

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--reconfigure", help="Reconfigure assistant", action="store_true")
args = parser.parse_args()

# Initialize objects
console = Console()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", openai_api_key))

# Find assistant id
assistants = client.beta.assistants.list()
assistant_id = None
for assistant in assistants:
    if assistant.name == assistant_name:
        assistant_id = assistant.id
        break

# Create assistant if it doesn't exist
if assistant_id is None:
    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=assistant_instructions,
        model=model
    )
    assistant_id = assistant.id
    args.reconfigure = True # Force reconfiguration
    print("Assistant created")
# Else, get existing assistant
else:
    assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)

# Reconfigure assistant if requested
if args.reconfigure:
    tools = []

    # Get all functions with the @generate_json decorator
    decorated_functions = [obj for name, obj in inspect.getmembers(functions, inspect.isfunction) if hasattr(obj, 'json')]

    # Print the JSON for each decorated function
    for func in decorated_functions:
        tools.append({"type": "function", "function": func.json})


    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tools=tools
    )
    
    print("Assistant configured")


thread = client.beta.threads.create()

# Handler for assistant events
class EventHandler(AssistantEventHandler):
    @override
    def on_text_delta(self, delta: MessageDelta, snapshot: Message) -> None:
        global response, live
        if delta.value:
            response.append(delta.value)
            live.update(Markdown("".join(response), style="green"))
        
    @override
    def on_event(self, event):
        global response, live
        if event.event == 'thread.run.requires_action':
            tool_outputs = []
            for tool in event.data.required_action.submit_tool_outputs.tool_calls:
                
                func = tool.function.name
                params = json.loads(tool.function.arguments)
                
                # Call function with params
                result = getattr(functions, func)(**params)
                
                if result is None:
                    result = ""
                    
                # Communicate the output to the API
                tool_outputs.append({"tool_call_id": tool.id, "output": str(result)})
                
            with client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=thread.id,
                run_id=event.data.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()


# Welcome message         
console.print("Starting assistant", style="bold")
console.print()

# Loop with user input and assistant response
while True:
    # Get user input
    console.print('> ', end="")
    query = console.input()
    
    # Ignore empty queries
    if query == '':
        continue
    
    # Exit if user types quit or exit
    if query == 'quit' or query == 'exit':
        exit()

    # Send message to API -> Response is handled by EventHandler
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
    
        response = []
        md = Markdown("")
        with Live(md, console=console, vertical_overflow="visible", auto_refresh=True) as live:
            live.update(console.status("", spinner="arrow3"))
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
    except Exception as e:
        console.print(e, style="bold red")