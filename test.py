from python_actr import *


class ButtonDisplay(Model):
    value1 = 0
    value2 = 0

    def observe(self):
        self.parent.state = self.value1

    def press1(self):
        self.value1 += 1

    def press2(self):
        self.value2 += 1


class Env(Model):
    button_ui = ButtonDisplay()
    state = 0


class Agent(ACTR):
    goal = Buffer()
    goal.set('observe')

    def observe(goal='observe',
                button_ui='value1:?val1 value2:?val2'):  # Match multiple values with spaces
        print(f"Value1: {val1}, Value2: {val2}")
        goal.set('press')

    def press(goal='press'):
        button_ui.press1()
        button_ui.press2()
        goal.set('observe')


env = Env()
env.agent = Agent()
env.agent.button_ui = env.button_ui
env.run()
