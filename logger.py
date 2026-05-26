import json
import os
import datetime

class Logger:
    def __init__(self, filepath="history_log.json"):
        self.filepath = filepath
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def log_move(self, move_num, player, coords, is_capture, check_state):
        log_entry = {
            "move_number": move_num,
            "player": player,
            "coords": coords,
            "capture": is_capture,
            "state": check_state,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            
        data.append(log_entry)
        
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def clear(self):
        with open(self.filepath, 'w') as f:
            json.dump([], f)
