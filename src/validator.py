from typing import Any, Dict, Tuple

def validate_request_tokens(req: Dict[str, Any]) -> bool:
    """
    Validates request 'tokens' field.
    Protects: Rule R5.
    A request is invalid if 'tokens' is:
    - missing
    - not an integer (floats, booleans, strings, nulls are invalid)
    - less than 1
    """
    if "tokens" not in req:
        return False
    tokens = req["tokens"]
    # In Python, bool is a subclass of int (isinstance(True, int) == True),
    # so we must strictly ensure type is int and not bool.
    if type(tokens) is not int:
        return False
    if tokens < 1:
        return False
    return True

def validate_request_key(req: Dict[str, Any], limits_config: Dict[str, Any]) -> bool:
    """
    Validates that request 'key' exists in limits.json 'keys' mapping.
    Protects: Rule R6.
    """
    if "key" not in req or not isinstance(req["key"], str):
        return False
    keys_map = limits_config.get("keys", {})
    return req["key"] in keys_map
