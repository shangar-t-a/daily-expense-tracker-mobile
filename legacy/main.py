"""App to track daily expenses on mobile devices using Kivy framework."""

import datetime
import os

from kivy.app import App
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

database = []
saved_items = []


class ScreenManagement(ScreenManager):
    """Screen Manager for the App."""

    pass


class MainScreen(Screen):
    """Main Screen with options."""

    PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
    main_wall = StringProperty("".join((PROJECT_PATH, "/images/mainwall.jpg")))


class EditorScreen(Screen):
    """Editor Screen for edit expense."""

    pass


class SaveScreen(Screen):
    """Save screen to get save name for expense page."""

    PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
    save_wall = StringProperty("".join((PROJECT_PATH, "/images/savewall.jpg")))


class LoadScreen(Screen):
    """Load screen to display the stored entries."""


class MainScreenWidgets(AnchorLayout):
    """Select options inside main Screen.

    1. NEW
    2. LOAD
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press_new(self, e):
        for ele in database:
            for wid in ele:
                wid.text = ""

    def on_press_load(self, e):
        PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
        store = JsonStore("".join((PROJECT_PATH, "/assets/save.json")))

        saved_sheets = list(store.keys())

        for itr in range(len(saved_sheets)):
            saved_items[itr][0].text = saved_sheets[itr]


class EditorScreenWidgets(GridLayout):
    """Populates the widgets in the Editor Screen."""

    def __init__(self, **kwargs):
        super(EditorScreenWidgets, self).__init__()
        self.cols = 3
        self.header = ["Add Items", "Balance/Income", "Expense"]

        global database

        for item in self.header:
            label = Button(text=item, background_color=(0, 100, 200, 1), disabled=True)
            self.add_widget(label)

        self.items = []
        self.expences = []
        self.Balance = []

        for index in range(15):
            item = TextInput(multiline=False)
            balance = TextInput(multiline=False)
            expence = TextInput(multiline=False)

            self.items.append(item)
            self.Balance.append(balance)
            self.expences.append(expence)

            self.add_widget(self.items[index])
            self.add_widget(self.Balance[index])
            self.add_widget(self.expences[index])

            database.append((item, balance, expence))

        self.calculate = Button(text="Calculate", background_color=(210, 1, 0, 1))
        self.calculate.bind(on_press=self.calc_sum)
        self.add_widget(self.calculate)
        self.available_bal = TextInput(readonly=True)
        self.add_widget(self.available_bal)
        self.total_expence = TextInput(readonly=True)
        self.add_widget(self.total_expence)
        database.append((self.available_bal, self.total_expence))

    def calc_sum(self, e):
        tot_exp = 0
        tot_bal = 0
        for expence in self.expences:
            if expence.text.isnumeric():
                tot_exp += int(expence.text)
        for balance in self.Balance:
            if balance.text.isnumeric():
                tot_bal += int(balance.text)
        self.total_expence.text = str(tot_exp)
        self.available_bal.text = str(tot_bal - tot_exp)

    def on_press_clear(self, e):
        for item in self.items:
            item.text = ""
        for expence in self.expences:
            expence.text = ""
        for balance in self.Balance:
            balance.text = ""
        self.total_expence.text = ""
        self.available_bal.text = ""


class SaveScreenWidgets(GridLayout):
    """Populates widgets for save screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press_save(self, e, save_name):
        PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
        store = JsonStore("".join((PROJECT_PATH, "/assets/save.json")))

        global database

        data = []

        for item in database:
            if len(item) == 2:
                data.append({"item": "total", "bal": item[0].text, "exp": item[1].text})
            else:
                data.append({"item": item[0].text, "bal": item[1].text, "exp": item[2].text})

        time = datetime.datetime.now()
        save_name = save_name + " @ " + time.strftime("%x").replace("/", ":") + "-" + time.strftime("%X")
        store.put(save_name, objects=data)


class LoadScreenWidgets(GridLayout):
    """Populates load screen widgets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
        store = JsonStore("".join((PROJECT_PATH, "/assets/save.json")))

        self.cols = 2
        global saved_items

        saved_sheets = list(store.keys())

        for item in range(15 - len(saved_sheets)):
            saved_sheets.append("No Data")

        for wid in range(15):
            saved_item = Button(text=saved_sheets[wid], background_color=(1, 1, 1, 1))
            saved_item.bind(on_press=self.on_press_load)
            delete_item = Button(text="delete", size_hint_x=0.2, background_color=(0.24, 0.64, 0.96, 1))
            delete_item.bind(on_press=self.on_press_delete)
            self.add_widget(saved_item)
            self.add_widget(delete_item)
            saved_items.append((saved_item, delete_item))

    def on_press_load(self, e):
        PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
        store = JsonStore("".join((PROJECT_PATH, "/assets/save.json")))

        global database

        if not e.text == "No Data":
            data = store[e.text]["objects"]

            itr = 0
            for ele in data:
                item, bal, exp = (ele["item"], ele["bal"], ele["exp"])
                if item == "total":
                    database[itr][0].text = bal
                    database[itr][1].text = exp
                else:
                    database[itr][0].text = item
                    database[itr][1].text = bal
                    database[itr][2].text = exp
                itr += 1

            self.parent.parent.current = "editor"

    def on_press_delete(self, e):
        PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
        store = JsonStore("".join((PROJECT_PATH, "/assets/save.json")))

        global saved_items

        for ele in saved_items:
            if ele[1] == e:
                if not ele[0].text == "No Data":
                    store.delete(ele[0].text)
                    ele[0].text = "No Data"


class ExpenseApp(App):
    pass


if __name__ == "__main__":
    ExpenseApp().run()
