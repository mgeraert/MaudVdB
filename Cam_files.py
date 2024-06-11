
from datetime import datetime
import os
import shutil
import time
import CamSettings
from playsound import playsound

class Cam_files:

    def __init__(self):
        self.day_dir = ""
        self.run_dir = ""
        self.log_file_name = ""
        self.log_folder = ""
        self.re_init_folders()

    def re_init_folders(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H-%M-%S")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.log_folder = CamSettings.video_folder
        self.day_dir = self.log_folder + "\\" + current_date
        self.run_dir = self.log_folder + "\\" + current_date + "\\" + current_time
        self.log_file_name = self.run_dir + "\\D" + current_date + "T" + current_time + '_log.txt'

        if CamSettings.FilesNeed2BeCopied():
            self.copy_2_dir = CamSettings.video_copy_to_folder + "\\" + current_date + "\\" + current_time
        else:
            self.copy_2_dir = False


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
        if not CamSettings.FilesNeed2BeCopied():
            return self.log_folder
        else:
            return self.copy_2_dir

    def get_stream_fname(self, cam_idx):
        cam_alias = CamSettings.getAlias(cam_idx)
        return (self.run_dir + "/" + cam_alias + ".h265")

    def copy_files(self):

        app_dir = os.path.dirname(os.path.abspath(__file__))

        sound_path = os.path.join(app_dir, 'Resources', 'Sounds', 'game-warning-quick-notification.wav')
        playsound(sound_path)

        if self.copy_2_dir:
            src_dir = self.run_dir
            dest_dir = self.copy_2_dir

            try:
                # Ensure the destination directory exists
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                # List all files in the source directory
                files = os.listdir(src_dir)

                # Copy each file from the source to the destination
                for file_name in files:
                    full_file_name = os.path.join(src_dir, file_name)
                    if os.path.isfile(full_file_name):
                        shutil.copy(full_file_name, dest_dir)

                # Verify that all files were copied
                copied_files = os.listdir(dest_dir)
                if set(files).issubset(set(copied_files)):
                    print("All files copied successfully.")
                    # Delete the original files in the source directory
                    for file_name in files:
                        os.remove(os.path.join(src_dir, file_name))
                    print("Original files deleted.")
                else:
                    print("Error: Not all files were copied successfully.")
                sound_path = os.path.join(app_dir, 'Resources', 'Sounds', 'fast-sci-fi-bleep.wav')
                playsound(sound_path)
                time.sleep(8)

                # Check if the directory is empty before attempting to delete
                remaining_items = os.listdir(src_dir)
                if not remaining_items:  # Check if the directory is empty
                    os.rmdir(src_dir)
                    print("Original directory deleted.")
                else:
                    print("Original directory is not empty, remaining items:", remaining_items)


                sound_path = os.path.join(app_dir, 'Resources', 'Sounds', 'interface-hint-notification.wav')
                playsound(sound_path)

            except Exception as e:
                print(f"An error occurred: {e}")




