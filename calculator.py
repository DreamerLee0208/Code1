import math


def calculate(expression: str) -> str:
    allowed = {"__builtins__": {}, "abs": abs, "round": round, "min": min, "max": max}
    allowed.update({k: v for k, v in vars(math).items() if not k.startswith("_")})
    try:
        result = eval(expression, allowed)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
