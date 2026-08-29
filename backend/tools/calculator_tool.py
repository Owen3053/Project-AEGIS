from backend.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):

    name = "calculator"

    description = "Perform basic mathematical calculations"

    def execute(self, data):

        if not data:
            return "What would you like me to calculate?"

        try:

            allowed = "0123456789+-*/().% "

            if any(char not in allowed for char in data):
                return "I can only perform basic mathematical calculations."

            result = eval(data, {"__builtins__": {}}, {})

            return f"The answer is {result}"

        except Exception:
            return "I couldn't calculate that."
