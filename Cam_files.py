
from datetime import datetime
import os
import CamSettings

class Cam_files:

    def __init__(self):
        self.day_dir = ""
        self.run_dir = ""
        self.log_file_name = ""
        self.log_folder = ""

    def re_init_folders(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H-%M-%S")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.log_folder = CamSettings.video_folder
        self.day_dir = self.log_folder + "\\" + current_date
        self.run_dir = self.log_folder + "\\" + current_date + "\\" + current_time
        self.log_file_name = self.run_dir + "\\D" + current_date + "T" + current_time + '_log.txt'

        # Check if the directory exists
        if not os.path.exists(self.run_dir):
            # If not, create the directory
            os.makedirs(self.run_dir)
            print(f"Directory '{self.run_dir}' created successfully.")
        else:
            print(f"Directory '{self.run_dir}' already exists.")


    def get_run_dir(self):
        return self.run_dir

    def get_log_file_name(self):
        return self.log_file_name

    def get_log_folder(self):
        return self.log_folder

    def get_stream_fname(self, cam_idx):
        cam_alias = CamSettings.getAlias(cam_idx)
        return (self.run_dir + "/" + cam_alias + ".h265")




