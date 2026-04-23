from launcher import ModelStack
from textual.app import App

try:
    class TestApp(App):
        DEFAULT_CSS = ModelStack.DEFAULT_CSS
    app = TestApp()
    print("Actual CSS Valid")
except Exception as e:
    print(f"CSS Error: {e}")
