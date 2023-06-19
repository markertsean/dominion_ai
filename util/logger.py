import time
import sys
import os

project_path = '/'.join( __file__.split('/')[:-2] )+'/'
sys.path.append(project_path)
print(project_path)

# Very simple logger that can be toggled on and off for games and globally
class GameLogger:
    def __init__(self,run_logging):
        self.logfile_name = self.__get_full_log_file_name__()
        self.save_log = run_logging
        self.active = True
        if ( self.save_log ):
            self.logfile = open( self.logfile_name, 'a' )

    def __del__(self):
        self.close_log()

    def __get_full_log_file_name__(self):
        time_str = time.strftime('%Y%m%d_%H%M%S')
        path = project_path
        log_path = path+'data/logs/'
        os.makedirs(log_path,exist_ok=True)
        return log_path+'game_log_'+time_str+'.log'

    def close_log(self):
        if ( self.save_log ):
            self.logfile.close()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def log(self,message):
        if ( self.save_log and self.active ):
            self.logfile.write(message+"\n")
            self.logfile.flush()
