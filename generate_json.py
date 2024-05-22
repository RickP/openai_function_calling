# Helper for genearating JSON for the openAI API tool configuration

import json
import re

def param_type_to_json_type(param_type):
    type_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object'
    }
    return type_mapping.get(param_type, 'string')

def process_param_description(param_desc_lines):
    param_description = []
    enum_values = []
    default_value = None

    for line in param_desc_lines:
        if line.startswith('Must be one of:'):
            enum_values = [value.strip('"') for value in line.split(':')[1].strip().split('", "')]
        elif line.startswith('Default:'):
            default_value = line.split(':')[1].strip()
        else:
            param_description.append(line)

    return ' '.join(param_description).strip(), enum_values, default_value

def generate_json(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    docstring = func.__doc__.strip().split('\n')
    name = func.__name__
    description = docstring[0]
    parameters = {}
    current_param = None
    current_param_desc = []

    for line in docstring[1:]:
        line = line.strip()
        if line.startswith(':param'):
            if current_param:
                param_description, enum_values, default_value = process_param_description(current_param_desc)
                param_dict = {
                    'type': param_type_to_json_type(param_type),
                    'description': param_description
                }

                if enum_values:
                    param_dict['enum'] = enum_values

                if default_value:
                    param_dict['default'] = default_value

                parameters[current_param] = param_dict

            param_parts = line.split(':')[1:]
            param_name = param_parts[0].strip()
            param_type = param_parts[1].strip()
            current_param = param_name
            current_param_desc = [':'.join(param_parts[2:])]
        else:
            current_param_desc.append(line)

    if current_param:
        param_description, enum_values, default_value = process_param_description(current_param_desc)
        param_dict = {
            'type': param_type_to_json_type(param_type),
            'description': param_description
        }

        if enum_values:
            param_dict['enum'] = enum_values

        if default_value:
            param_dict['default'] = default_value

        parameters[current_param] = param_dict

    required_params = [k.split()[-1] for k, v in parameters.items() if 'default' not in v]

    json_data = {
        'name': name,
        'description': description,
        'parameters': {
            'type': 'object',
            'properties': {k.split()[-1]: v for k, v in parameters.items()},
            'required': required_params
        } if parameters else {}
    }

    wrapper.json = json_data
    return wrapper