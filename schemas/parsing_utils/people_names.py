
def parse_names(name_fields: dict) -> dict:
    '''
    Parses people name fields according to business logic.

    This function helps us to keep following Single responsability and Open/close principle.
    since it makes easier to change business requierements in a future
    '''
    name_fields['first_name'] = name_fields['first_name'].capitalize()
    name_fields['second_name'] = name_fields['second_name'].capitalize() if name_fields['second_name'] is not None else None
    name_fields['first_lastname'] = name_fields['first_lastname'].capitalize()
    name_fields['second_lastname'] = name_fields['second_lastname'].capitalize()

    return name_fields