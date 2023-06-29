import time
import sys
import os

project_path = '/'.join( __file__.split('/')[:-2] )+'/'
sys.path.append(project_path)

# Very simple logger that can be toggled on and off for games and globally
class GameLogger:
    def __init__(self):
        self.logfile_name = None
        self.logfile = None
        self.save_log = False
        self.active = False
        self.print_log = False
        self.debug = False

    def __del__(self):
        self.close_log()

    def __get_full_log_file_name__(self):
        time_str = time.strftime('%Y%m%d_%H%M%S')
        path = project_path
        log_path = path+'data/logs/'
        os.makedirs(log_path,exist_ok=True)
        return log_path+'game_log_'+time_str+'.log'

    def __repr__(self):
        out_str = "Logger status:\n"
        for key in self.__dict__:
            out_str += "\t{:25s} =\t{}\n".format(key,self.__dict__[key])
        return out_str

    def start_logger(self,debug=False):
        self.save_log = True
        self.debug = debug
        self.logfile_name = self.__get_full_log_file_name__()
        self.logfile = open( self.logfile_name, 'a' )

    def close_log(self):
        if ( self.save_log ):
            self.logfile.close()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def activate_print_log(self):
        self.print_log = True

    def deactivate_print_log(self):
        self.print_log = False

    def log(self,message,debug=False):
        if ( debug and !self.debug ):
            return
        if ( self.active ):
            if ( self.print_log ):
                print(message)
            if ( self.save_log ):
                self.logfile.write(message+"\n")
                self.logfile.flush()
        return


game_logger = GameLogger()
