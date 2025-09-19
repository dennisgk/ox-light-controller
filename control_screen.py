import launchpad_py
from event_emitter import EventEmitter
import math

from lcd_control import EARG_CHRISTMAS, EARG_COLOR, EARG_COLOR_WIPE, EARG_POLICE, EARG_SECTION_WIPE, EARG_STROBE, EARG_THEATER_CHASE

class ControlScreen():
    def __init__(self, lp: launchpad_py.LaunchpadMk2, emitter: EventEmitter):
        self.lp = lp
        self.emitter = emitter
        self.registered = {}

    def button_event(self, ev_name):
        ev = self.registered.get(ev_name, None)
        if ev is not None:
            ev()

    def invalidate(self):
        coords = []
        for x in range(0, 8):
            coords.append((x, 0))

        for y in range(1, 9):
            for x in range(0, 9):
                coords.append((x, y))

        for coord in coords:
            act_buff = self.draw(coord[0], coord[1])
            self.lp.LedCtrlXY(coord[0], coord[1], act_buff[0], act_buff[1], act_buff[2])

    def draw(self, x, y):
        raise NotImplementedError()

    def register_button(self, x, y, callable_down = None, callable_up = None):
        pref = f"{x}_{y}"
        if callable_down is not None:
            self.registered[f"{pref}_down"] = callable_down
        if callable_up is not None:
            self.registered[f"{pref}_up"] = callable_up

class ColorScreen(ControlScreen):
    def __init__(self, lp, emitter, xoff):
        super().__init__(lp, emitter)

        self.xoff = xoff
        self.new_col = [*self.emitter.config["colors"][self.emitter.config["pageIndex"]][self.xoff]]

        self.register_button(6, 1, lambda: self.emitter.emit("pop_view"))
        self.register_button(7, 1, self.save_color_and_pop)

        for y in range(0, 2):
            for x in range(0, 8):
                self.register_button(x, y + 3, lambda x=x, y=y: self.set_col(0, 1 + x + (8 * y)))
                self.register_button(x, y + 5, lambda x=x, y=y: self.set_col(1, 1 + x + (8 * y)))
                self.register_button(x, y + 7, lambda x=x, y=y: self.set_col(2, 1 + x + (8 * y)))

    def set_col(self, ind, num):
        new_col_val = (4 * num) - 1
        if self.new_col[ind] == new_col_val:
            self.new_col[ind] = 0
        else:
            self.new_col[ind] = new_col_val
        self.invalidate()

    def save_color_and_pop(self):
        self.emitter.config["colors"][self.emitter.config["pageIndex"]][self.xoff] = self.new_col
        self.emitter.update_config()
        self.emitter.emit("pop_view")

    def draw(self, x, y):
        if y == 1:
            if x == 6:
                return (63, 0, 0)

            if x == 7:
                return (0, 63, 0)
            
        if x == 8:
            return (0, 0, 0)
        
        if y == 2:
            return self.new_col
            
        rdiv = math.floor((self.new_col[0] + 1) / 4)
        gdiv = math.floor((self.new_col[1] + 1) / 4)
        bdiv = math.floor((self.new_col[2] + 1) / 4)
        
        if y == 3:
            if x + 1 <= rdiv:
                return (63, 0, 0)
            else:
                return (4, 4, 4)
            
        if y == 4:
            if x + 9 <= rdiv:
                return (63, 0, 0)
            else:
                return (4, 4, 4)
            
        if y == 5:
            if x + 1 <= gdiv:
                return (0, 63, 0)
            else:
                return (4, 4, 4)
            
        if y == 6:
            if x + 9 <= gdiv:
                return (0, 63, 0)
            else:
                return (4, 4, 4)
            
        if y == 7:
            if x + 1 <= bdiv:
                return (0, 0, 63)
            else:
                return (4, 4, 4)
            
        if y == 8:
            if x + 9 <= bdiv:
                return (0, 0, 63)
            else:
                return (4, 4, 4)

        return (0, 0, 0)

class HomeScreen(ControlScreen):
    def __init__(self, lp, emitter):
        super().__init__(lp, emitter)

        self.laction = emitter.lcd.action
        self.ldata = emitter.lcd.adata

        for x in range(0, 8):
            self.register_button(x, 0, lambda x=x: self.set_cursor(x))

        for y in range(1, 5):
            self.register_button(8, y, lambda y=y: self.set_func_page(y - 1))

        for y in range(5, 9):
            self.register_button(8, y, lambda y=y: self.set_page(y - 5))
        
        for x in range(0, 8):
            self.register_button(x, 1, lambda x=x: self.emitter.emit("push_view", ColorScreen(self.lp, self.emitter, x)))

        self.function_buttons = {
            0: {
                0: {
                    2: [lambda: self.get_cursor_color(0), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(0)), None],
                    3: [lambda: self.get_cursor_color(1), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(1)), None],
                    4: [lambda: self.get_cursor_color(2), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(2)), None],
                    5: [lambda: self.get_cursor_color(3), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(3)), None],
                    6: [lambda: self.get_cursor_color(4), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(4)), None],
                    7: [lambda: self.get_cursor_color(5), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(5)), None],
                    8: [lambda: (10, 10, 10), lambda: self.emitter.lcd.dispatch(EARG_COLOR, (0, 0, 0)), None]
                },
                1: {
                    2: [lambda: self.get_cursor_color(0), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(0)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    3: [lambda: self.get_cursor_color(1), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(1)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    4: [lambda: self.get_cursor_color(2), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(2)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    5: [lambda: self.get_cursor_color(3), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(3)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    6: [lambda: self.get_cursor_color(4), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(4)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    7: [lambda: self.get_cursor_color(5), lambda: self.emitter.lcd.dispatch(EARG_COLOR, self.get_cursor_color(5)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)],
                    8: [lambda: (10, 10, 10), lambda: self.emitter.lcd.dispatch(EARG_COLOR, (0, 0, 0)), lambda: self.emitter.lcd.dispatch(self.laction, self.ldata)]
                },
                3: {
                    3: [lambda: (24, 58, 28), lambda: self.emitter.lcd.dispatch(EARG_CHRISTMAS, [(255, 0, 0), (0, 255, 0)]), None],
                    4: [lambda: (23, 1, 82), lambda: self.emitter.lcd.dispatch(EARG_COLOR_WIPE), None],
                    5: [lambda: (26, 21, 55), lambda: self.emitter.lcd.dispatch(EARG_POLICE), None],
                    6: [lambda: (0, 19, 34), lambda: self.emitter.lcd.dispatch(EARG_SECTION_WIPE), None]
                },
                4: {
                    3: [lambda: (12, 46, 51), lambda: self.emitter.lcd.dispatch(EARG_STROBE), None],
                    4: [lambda: (34, 45, 12), lambda: self.emitter.lcd.dispatch(EARG_THEATER_CHASE), None]
                }
            }
        }

        for x in range(0, 8):
            for y in range(2, 9):
                self.register_button(x, y, lambda x=x, y=y: self.run_func(x, y, True), lambda x=x, y=y: self.run_func(x, y, False))

    def run_func(self, x, y, is_down):
        func_val = self.function_buttons.get(self.emitter.config["funcPageIndex"], {}).get(x, {}).get(y, None)
        
        if func_val is not None:
            if is_down:
                if func_val[1] is not None:
                    self.laction, self.ldata = func_val[1]()
            else:
                if func_val[2] is not None:
                    self.laction, self.ldata = func_val[2]()

    def get_cursor_color(self, offset):
        att_cols = self.emitter.config["colors"][self.emitter.config["pageIndex"]]
        len_col = len(att_cols)
        return att_cols[(self.emitter.config["cursorIndex"] + offset) % len_col]

    def set_cursor(self, x):
        self.emitter.config["cursorIndex"] = x
        self.emitter.update_config()
        self.invalidate()

    def set_func_page(self, y):
        self.emitter.config["funcPageIndex"] = y
        self.emitter.update_config()
        self.invalidate()

    def set_page(self, y):
        self.emitter.config["pageIndex"] = y
        self.emitter.update_config()
        self.invalidate()

    def draw(self, x, y):
        if y == 0:
            if x == self.emitter.config["cursorIndex"]:
                return (63, 63, 63)
            else:
                return (0, 0, 0)

        if x == 8:
            if y - 1 == self.emitter.config["funcPageIndex"]:
                return (63, 63, 63)
            elif y - 5 == self.emitter.config["pageIndex"]:
                return (63, 63, 63)
            else:
                return (0, 0, 0)

        if y == 1:
            return (self.emitter.config["colors"][self.emitter.config["pageIndex"]][x])
        
        func_val = self.function_buttons.get(self.emitter.config["funcPageIndex"], {}).get(x, {}).get(y, None)

        if func_val is not None:
            return func_val[0]()

        return (0, 0, 0)