import os
import time

#if __name__ == "__main__":
#    if os.name != "nt":
#        time.sleep(20)

import launchpad_py as lppy
from event_emitter import EventEmitter
from control_screen import HomeScreen
import traceback

# control goes from 0-63 for colors

emitter = EventEmitter()

if __name__ == "__main__":
    lp = lppy.LaunchpadMk2()
    lp.Open()

    views = []

    def button_ev_handler(evname):
        views[len(views) - 1].button_event(evname)

    def push_view_handler(nview):
        views.append(nview)
        views[len(views) - 1].invalidate()

    def pop_view_handler():
        views.pop()
        views[len(views) - 1].invalidate()

    emitter.on("button_event", button_ev_handler)
    emitter.on("push_view", push_view_handler)
    emitter.on("pop_view", pop_view_handler)
    
    push_view_handler(HomeScreen(lp, emitter))

    try:
        while True:
            b_state = lp.ButtonStateXY()
            triplets = [(b_state[i], b_state[i+1], b_state[i+2]) for i in range(0, len(b_state), 3)]
            for ev in triplets:
                pref = f"{ev[0]}_{ev[1]}"
                if ev[2] > 0:
                    emitter.emit("button_event", f"{pref}_down")
                else:
                    emitter.emit("button_event", f"{pref}_up")
    except Exception as e:
        print(e)
        traceback.print_exc()

    emitter.lcd.stop()
