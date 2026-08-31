import ast
import operator
import re

from backend.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):

    name = "calculator"

    description = "Perform basic mathematical calculations"

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def execute(self, data):

        if data is None:
            return self.failure(
                "What would you like me to calculate?"
            )

        expression = str(data).strip()

        if not expression:
            return self.failure(
                "What would you like me to calculate?"
            )

        expression = expression.lower()

        replacements = {
            "multiplied by": "*",
            "multiply by": "*",
            "times": "*",
            "divided by": "/",
            "divide by": "/",
            "plus": "+",
            "minus": "-",
            "modulo": "%",
        }

        for phrase, symbol in replacements.items():
            expression = expression.replace(
                phrase,
                symbol
            )

        expression = re.sub(
            r"[?!.,;:]+$",
            "",
            expression
        ).strip()

        allowed = "0123456789+-*/().% "

        if any(
            char not in allowed
            for char in expression
        ):
            return self.failure(
                "I can only perform basic mathematical calculations."
            )

        try:

            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = self._evaluate(tree.body)

            return self.success({
                "expression": expression,
                "result": result
            })

        except ZeroDivisionError:

            return self.failure(
                "I can't divide by zero."
            )

        except Exception:

            return self.failure(
                "I couldn't calculate that."
            )

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):

            if isinstance(
                node.value,
                (int, float)
            ):
                return node.value

            raise ValueError(
                "Invalid constant"
            )

        if isinstance(node, ast.BinOp):

            operation = self.OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported operator"
                )

            left = self._evaluate(
                node.left
            )

            right = self._evaluate(
                node.right
            )

            return operation(
                left,
                right
            )

        if isinstance(node, ast.UnaryOp):

            operation = self.OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported operator"
                )

            operand = self._evaluate(
                node.operand
            )

            return operation(
                operand
            )

        raise ValueError(
            "Unsupported expression"
        )


if __name__ == "__main__":

    calculator = CalculatorTool()

    tests = [
        "25 * 4",
        "100 + 50",
        "37 * 24?",
        "25 times 40",
        "100 divided by 4",
        "50 plus 25",
        "10 minus 3",
        "2 ** 8",
        "10 / 0",
        "hello world"
    ]

    for test in tests:

        print(
            f"{test} -> "
            f"{calculator.execute(test)}"
        )