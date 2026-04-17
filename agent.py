import json
import os
from decimal import Decimal

from dotenv import load_dotenv
from pydantic_ai import Agent

from calculator import calculate

load_dotenv()

MODEL = os.getenv("MODEL", "google-gla:gemini-2.5-flash")

agent = Agent(
    MODEL,
    system_prompt=(
        "You are a helpful assistant that solves math questions step by step. "
        "Use calculator_tool for arithmetic. "
        "Use product_lookup when a question asks about product prices from the catalog."
    ),
)


def load_catalog(path: str = "products.json") -> dict[str, Decimal]:
    with open(path) as f:
        catalog = json.load(f)
    return {name: Decimal(str(price)) for name, price in catalog.items()}


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


@agent.tool_plain
def calculator_tool(expression: str) -> str:
    return calculate(expression)


@agent.tool_plain
def product_lookup(product_name: str) -> str:
    catalog = load_catalog()
    if product_name in catalog:
        return money(catalog[product_name])
    available_products = ", ".join(sorted(catalog))
    return f"Product not found: {product_name}. Available products: {available_products}"


def load_questions(path: str = "math_questions.md") -> list[str]:
    questions = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and line[0].isdigit() and ". " in line[:4]:
                questions.append(line.split(". ", 1)[1])
    return questions


def print_trace(result) -> None:
    print("Trace")
    for message in result.all_messages():
        for part in message.parts:
            kind = part.part_kind
            if kind in ("user-prompt", "system-prompt"):
                continue
            if kind == "text":
                print(f"- Reason: {part.content}")
            elif kind == "tool-call":
                print(f"- Act: {part.tool_name}({part.args})")
            elif kind == "tool-return":
                print(f"- Result: {part.content}")


def main() -> None:
    questions = load_questions()
    for i, question in enumerate(questions, 1):
        print(f"Question {i}")
        print(question)
        print()
        result = agent.run_sync(question)
        print_trace(result)
        print()
        print(f"Answer: {result.output}")
        print("\n---\n")


if __name__ == "__main__":
    main()
