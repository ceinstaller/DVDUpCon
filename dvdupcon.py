import subprocess
import os
import shutil
import sys
import json
import time
import logging
import configparser
from math import gcd
from PIL import ImageFile,Image

# Allow PIL to load poorly formated PNG file (Missing header)
ImageFile.LOAD_TRUNCATED_IMAGES = True

###########
# Classes #
###########

class Utils:
    def __init__(self):
        pass


     # Check for NVidia GPU, if no GPU exit.
    def gpu():
        try:
            subprocess.run("nvidia-smi", capture_output=True)
            gpu_check = 1
        except:
            print("It looks like you don't have NVidia drivers installed.")
            gpu_check = 0

        if gpu_check == 1:
            gpu = subprocess.run("nvidia-smi --query-gpu=name,power.limit,power.default_limit --format=csv,noheader", capture_output=True, text=True)
            global gpu_name
            gpu_stats = gpu.stdout.split(", ")
            gpu_name = gpu_stats[0]
            gpu_current_power = gpu_stats[1]
            gpu_max_power = gpu_stats[2]
            print("It looks like you have an " + gpu_name + ".  Nice.")
            print("Current power: " + gpu_current_power)
            print("Default power: "+ gpu_max_power)
        else:
            print("Please install the NVidia drivers.\n")
            sys.exit()

    
    # Delete files from list of directories
    def scrub(directory):
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Deleting working files...")
        logging.info("Deleting Files")
        for dir in directory:
            if(dir == '/' or dir == "\\"):
                return
            else:
                for root, dirs, files in os.walk(dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))


class DVD_Source:
    def __init__(self):
        pass


    # Check if dvd source file exists and is a video file.  If not, exit
    def dvd_check(self,dvd_source):    
        if os.path.isfile(dvd_source):
            check_dvd_file = subprocess.run(".\\tools\\ffmpeg\\ffprobe -v error " + dvd_source, capture_output=True, text=True)             
            check_dvd_file_result = check_dvd_file.stderr
            if check_dvd_file_result.find("Invalid") > 0:
                print("\nIt looks like that isn't a video file.\n")
            else:
                logging.info(f"File - {dvd_source}")
                return 1
        else:
            print("\nIt looks like that file doesn't exist.\n")
            

    # Collect basic dvd source file properties and display them
    def dvd_properties(self,dvd_source):
        dvd_source_properties_json = subprocess.run(".\\tools\\ffmpeg\\ffprobe -v error -select_streams v:0 -show_entries format=filename:stream:stream=codec_name,width,height,display_aspect_ratio,duration,r_frame_rate -of json " + "\"" + dvd_source + "\"", capture_output=True, text=True)
        dvd_source_properties = json.loads(dvd_source_properties_json.stdout)

        global dvd_source_filename
        global dvd_source_codec
        global dvd_source_size_width
        global dvd_source_size_height
        global dvd_source_aspect_ratio
        global dvd_source_duration
        global dvd_source_frame_rate
        
        dvd_source_filename = dvd_source_properties.get('format').get('filename','Unknown')
        dvd_source_codec = dvd_source_properties.get('streams')[0].get('codec_name','Unknown')
        dvd_source_size_width = dvd_source_properties.get('streams')[0].get('width','Unknown')
        dvd_source_size_height = dvd_source_properties.get('streams')[0].get('height','Unknown')
        dvd_source_aspect_ratio = dvd_source_properties.get('streams')[0].get('display_aspect_ratio','Unknown')
        dvd_source_duration = dvd_source_properties.get('streams')[0].get('duration','Unknown') 
        dvd_source_frame_rate = eval(dvd_source_properties.get('streams')[0].get('r_frame_rate','Unknown'))
        
        # If no aspect ratio, calculate from size
        if dvd_source_aspect_ratio == "Unknown":
            aspect_gcd = gcd(dvd_source_size_width, dvd_source_size_height)
            aspect_width = int(dvd_source_size_width/aspect_gcd)
            aspect_height = int(dvd_source_size_height/aspect_gcd)
            dvd_source_aspect_ratio = str(aspect_width) + ":" + str(aspect_height)
        
        # Convert duration seconds into minutes
        if dvd_source_duration != "Unknown":
            dvd_source_duration = str(round(int(float(dvd_source_duration))/60, 1)) + " minutes"
        else:
            dvd_source_duration = "Unknown"

        # Log source file values
        logging.info(f"GPU - {gpu_name}")
        logging.info(f"Codec - {dvd_source_codec}")
        logging.info(f"Width - {dvd_source_size_width}")
        logging.info(f"Height - {dvd_source_size_height}")
        logging.info(f"Aspect Ratio - {dvd_source_aspect_ratio}")
        logging.info(f"Duration - {dvd_source_duration}")
        logging.info(f"Source Frame Rate - {dvd_source_frame_rate}")
        
        # Display values
        print()
        print("File Info")
        print("=========")
        print("File Name: " + dvd_source_filename)
        print("Codec: " + dvd_source_codec)
        print("Size: " + str(dvd_source_size_width) + " x " + str(dvd_source_size_height))
        print("Aspect Ratio: " + dvd_source_aspect_ratio)
        print("Length: " + dvd_source_duration)
        print("Frame Rate: " + str(round(dvd_source_frame_rate,2)))
        print()    
        

class DVD_Process:
    # Begin processing the source dvd
    def __init__(self):
        pass


    def extract_frames(self,dvd_source):
        # Use ffmpeg to extract frames from source file
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Extracting frames...")
        logging.info("Extracting frames")
        cmd = ".\\tools\\ffmpeg\\ffmpeg -v quiet -hwaccel auto -y -i " + "\"" + dvd_source + "\"" + " -pix_fmt rgb24 extract\\extracted_%08d.png"
        logging.info(cmd)
        dvd_extract = subprocess.run(cmd, capture_output=True, text=True)
        
        # Get precise number of frames extracted (ffprobe doesn't return actual number of frames extracted by ffmpeg)
        dvd_source_frames = os.listdir("extract")
        # Remove 1 from frame count to account for the recovery directory.
        frame_count = len(dvd_source_frames) - 1
        
        logging.info(f"Frame Count - {frame_count}")
        
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frames: " + str(frame_count))
        print()


    def srmd_upscale_frames(self,settings,scale_factor,mode): 
        # Use SRMD to upscale extracted frames
        noise = settings["SRMD"]["Noise"]
        tile = settings["SRMD"]["Tile"]
        gpu = settings["SRMD"]["GPU"]
        threads = settings["SRMD"]["Threads"]
        tta = settings["SRMD"]["TTA"]
        if tta == "Yes":
            tta = " -x "
        else:
            tta = ""
        
        if mode == "N":
            # Start normal mode upscale process            
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Upscaling frames with SRMD...")
            logging.info("Beginning upscale process")
            cmd = ".\\tools\\srmd\\srmd-ncnn-vulkan" + tta + " -n " + noise + " -s " + str(scale_factor) + " -t " + tile + " -m .\\tools\\srmd\\models-srmd -g " + gpu + " -j " + threads + " -f png -i .\\extract -o .\\upscale"
            logging.info(cmd)
            dvd_upscale = subprocess.run(cmd)
            
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame upscale complete")
            print()
        else:
            # Start recovery mode upscale process
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Upscaling frames with SRMD...")
            logging.info("Beginning upscale process")
            
            # Get frame count of upscaled images
            upscale_file_count = len(os.listdir("upscale"))

            # Figure out what the last upscaled file is
            last_file = "extracted_" + ("00000000" + str(upscale_file_count))[-8:] + ".png"

            # If it exists, delete last file in case it's corrupt
            os.remove("upscale\\" + last_file)

            # Get frame count of extracted images
            extract_file_count = len(os.listdir("extract"))
            
            # Copy remaining files to recovery directory
            for x in range(upscale_file_count, extract_file_count):            
                shutil.copyfile("extract\\extracted_" + ("00000000" + str(x))[-8:] + ".png", "extract\\recovery\\extracted_" + ("00000000" + str(x))[-8:])    
            
            # Upscale remaining exctracted images
            cmd = ".\\tools\\srmd\\srmd-ncnn-vulkan" + tta + " -n " + noise + " -s " + str(scale_factor) + " -t " + tile + " -m .\\tools\\srmd\\models-srmd -g " + gpu + " -j " + threads + " -f png -i .\\extract\\recovery -o .\\upscale"
            logging.info(cmd)
            dvd_upscale = subprocess.run(cmd)

            # Delete frames from recovery direcory
            path = "extract\\recovery\\"

            folder = os.fsencode(path)

            for file in os.listdir(folder):
                filename = os.fsdecode(file)
                print(path + filename)
                os.remove(path + filename)

            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame upscale complete")
            print()


    def realsr_upscale_frames(self,scale_factor,mode):
        # Use RealSR to upscale extracted frames
        tile = settings["RealSR"]["Tile"]
        gpu = settings["RealSR"]["GPU"]
        threads = settings["RealSR"]["Threads"]
        tta = settings["RealSR"]["TTA"]
        if tta == "Yes":
            tta = " -x "
        else:
            tta = ""
  
        if mode == "N":
            # Start normal mode upscale process
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Upscaling frames with RealSR...")
            logging.info("Beginning upscale process")
            cmd = ".\\tools\\realsr\\realsr-ncnn-vulkan" + tta + " -s 4 -t " + tile + " -m .\\tools\\realsr\\models-DF2K -g " + gpu + " -j " + threads + " -f png -i .\\extract -o .\\upscale"
            logging.info(cmd)
            dvd_upscale = subprocess.run(cmd)
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame upscale complete")
        else:
            # Start recovery mode upscale process
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Upscaling frames with RealSR...")
            logging.info("Beginning upscale process")
            
            # Get frame count of upscaled images
            upscale_file_count = len(os.listdir("upscale"))

            # Figure out what the last upscaled file is
            last_file = "extracted_" + ("00000000" + str(upscale_file_count))[-8:] + ".png"

            # Delete last file in case it's corrupt
            os.remove("upscale\\" + last_file)

            # Get frame count of extracted images
            extract_file_count = len(os.listdir("extract"))
            
            # Copy remaining files to recovery directory
            for x in range(upscale_file_count, extract_file_count):            
                shutil.copyfile("extract\\extracted_" + ("00000000" + str(x))[-8:] + ".png", "extract\\recovery\\extracted_" + ("00000000" + str(x))[-8:])    

            # Upscale remaining exctracted images
            cmd = ".\\tools\\realsr\\realsr-ncnn-vulkan" + tta + " -s 4 -t " + tile + " -m .\\tools\\realsr\\models-DF2K -g " + gpu + " -j " + threads + " -f png -i .\\extract\\recovery -o .\\upscale"
            logging.info(cmd)
            dvd_upscale = subprocess.run(cmd)

            # Delete frames from recovery direcory
            path = "extract\\recovery\\"

            folder = os.fsencode(path)

            for file in os.listdir(folder):
                filename = os.fsdecode(file)
                print(path + filename)
                os.remove(path + filename)

            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame upscale complete")
        
        # RealSR can only scale 4x, if 2x scale is selected, downsize upscaled frames
        if scale_factor == "2":
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Downsizing frames...")
            logging.info("Beginning frame downsizing process")
            path = ".\\upscale\\"
            images = os.listdir(path)

            for item in images:
                im = Image.open(path+item)
                (width, height) = (im.width // 2, im.height // 2)
                f,e = os.path.splitext(path+item)
                imResize = im.resize((width,height), Image.LANCZOS)
                imResize.save(f + ".png", "PNG")
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame downsizing complete...")
            logging.info("Frame downsizing complete")
        print()

    
    def add_frames(self,settings):
        # Use RIFE to add interpolated frames.
        gpu = settings["RIFE"]["GPU"]
        threads = settings["RIFE"]["Threads"]

        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Adding frames...")
        logging.info("Begining interpolation process")
        cmd = ".\\tools\\rife\\rife-ncnn-vulkan -i .\\upscale -o .\\insert -g " + gpu + " -j " + threads + " -f extracted_%08d.png"
        logging.info(cmd)
        add_frames = subprocess.run(cmd)
    
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Frame interpolation complete")
        print()


    def assemble_frames(self,dvd_source_frame_rate,dvd_source_aspect_ratio,use_interpolation):
        # Stitch upscaled frames back into an intermediate video file
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Assembling frames...")
        logging.info("Assembling upscaled frames")
        
        # Did we use frame interpolation?  If so, we should double the frame rate of output video and use the doubled frames
        if use_interpolation == "Y":
            dvd_source_frame_rate = dvd_source_frame_rate * 2
            frame_source = "insert"
        else:
            frame_source = "upscale"
        
        # Update aspect ratio string to work with ffmpeg
        aspect_ratio = dvd_source_aspect_ratio.replace(":", "/")

        cmd = ".\\tools\\ffmpeg\\ffmpeg -v quiet -r " + str(dvd_source_frame_rate) + " -hwaccel auto -y -f image2 -i .\\" + frame_source + "\\extracted_%08d.png -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 17 -vf pad=ceil(iw/2)*2:ceil(ih/2)*2,setdar=" + aspect_ratio + " -tune film .\\stage\\intermediate.mkv"
        logging.info(cmd)
        frame_assembly = subprocess.run(cmd)
        print()


    def assemble_video(self,dvd_short_name,dvd_source):
        # Add audio from original video to upscaled video
        print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Assembling video...")
        logging.info("Assembling video")
        cmd = ".\\tools\\ffmpeg\\ffmpeg -v quiet -hwaccel auto -y -i .\\stage\\intermediate.mkv -i " + "\"" + dvd_source + "\"" + " -map 0:v? -map 1:a? -map 1:s? -map 1:d? -map 1:t? -c copy -map_metadata 0 -movflags use_metadata_tags " + "\"" + ".\\output\\"  + dvd_short_name + "_output.mkv" + "\"" 
        logging.info(cmd)
        video_assembly = subprocess.run(cmd)
        print()


class DVD_Restart:
    # Restart a failed upconversion
    def __init__(self):
        pass


    def restart():
        print("It looks like a previous job didn't finish.  Let's see what happened.")
        print()
    
        # Process log file
        with open('dvdupcon.log') as log:
            for line in log.readlines():
                if 'File' in line:
                    log_file = line.split(" - ",3)[3].strip()
                if 'Aspect Ratio' in line:
                    log_aspect = line.split(" - ",3)[3].strip()    
                if 'Source Frame Rate' in line:
                    log_framerate = line.split(" - ",3)[3].strip()
                if 'Upscaler' in line:
                    log_upscaler = line.split(" - ",3)[3].strip()
                if 'Scale Factor' in line:
                    log_scalefactor = line.split(" - ",3)[3].strip()
                if 'Interpolation' in line:
                    log_interpolation = line.split(" - ",3)[3].strip()
                if 'Frame Count' in line:
                    log_framecount = int(line.split(" - ",3)[3].strip())
                    break
                else:
                    log_framecount = "NA"

        # Get directory file counts
        extracted_count = int(len(os.listdir("extract"))) -1   # Minus one for the recovery directory
        upscaled_count = int(len(os.listdir("upscale")))
        inserted_count = int(len(os.listdir("insert")))
        stage_count = int(len(os.listdir("stage")))
        output_count = int(len(os.listdir("output")))

        # Display settings logged for failed run and file counts
        print("Log Analysis")
        print("============")
        print("File: " + log_file)
        print("Aspect Ratio: " + log_aspect)
        print("Frame Rate: {:.2f}".format(float(log_framerate)))
        print("Upscaler: " + log_upscaler)
        print("Scale Factor: " + log_scalefactor)
        print("Interpolation: " + log_interpolation)
        print("Frame Count: " + str(log_framecount))
        print() 
        print("File Analysis")
        print("=============")
        print("Extracted Frames: " + str(extracted_count))
        print("Upscaled Frames: " + str(upscaled_count))
        print("Inserted Frames: " + str(inserted_count))
        print("Stage Files: " + str(stage_count) + " of 1")
        print("Output Files: " + str(output_count) + " of 2")
        print()
        
        # Show the status of each step and set status variable so we know where to restart
        if log_framecount == extracted_count:
            print("It looks like we finished the frame extraction process.")
            restart_step = 0

        if log_framecount == "NA":
            print("It looks like we didn't finish the frame extraction process.")
            restart_step = 5
        
        if upscaled_count != extracted_count:
            print("It looks like we didn't finish the upscaling process.")
            if restart_step > 4:
                restart_step
            else:
                restart_step = 4
        elif upscaled_count == extracted_count:
            print("It looks like we finished the upscale process.")
        
        if log_interpolation.strip() == "Y" and ((upscaled_count * 2) != inserted_count or upscaled_count == 0):
            print("It looks like we didn't finish the frame interpolation process.")
            if restart_step > 3:
                restart_step
            else:
                restart_step = 3
        elif log_interpolation.strip() == "Y" and (upscaled_count * 2) == inserted_count:
            print("It looks like we finished the frame interpolation process.")

        if stage_count == 0:
            print("It looks like we didn't finish the frame assembly process.")
            if restart_step > 2:
                restart_step
            else:
                restart_step = 2
        elif stage_count == 1:
            print("It looks like we finished the frame assembly process.")
        
        if output_count < 2:
            print("It looks like we didn't finish the final assembly process.")
            if restart_step > 1:
                restart_step
            else:
                restart_step = 1
        elif output_count == 2:
            print("It looks like we finished the final assembly process.")
           
        print()
        if log_interpolation == "Y":
            print("Steps needed to complete recovery: " + str(restart_step))
        else:
            print("Steps needed to complete recovery: " + str(restart_step - 1))
        print()

        while True:
            restart = input("Would you like to recover the previous run or exit and restart? (R)ecover or (E)xit: ")

            if restart.upper() not in {"R", "E"}:
                print("Please enter R or E.")
                continue
            else:
                break
        print()
        
        if restart.upper() == "E":
            # Delete files from working directories
            if settings["General"]["SaveFiles"] == "No":
                Utils.scrub(["extract", "upscale", "insert", "stage"])
                os.remove("dvdupcon.log")
            
            # Exit recovery process
            sys.exit()

        else:
            # Set mode to Recovery
            mode = "R"

            # Open log to append new entries
            logging.basicConfig(level=logging.INFO, filename="dvdupcon.log", filemode="a",
                                format="%(asctime)s - %(levelname)s - %(message)s")
            logging.info("Restarting upscale from interrupted job.")
            
            # Extract Frames
            if restart_step >= 5:
                DVD_Process().extract_frames(log_file)

            # Upscale Frames
            if restart_step >= 4:
                if log_upscaler[0] == "S":
                    DVD_Process().srmd_upscale_frames(settings,log_scalefactor,mode)
                else:
                    DVD_Process().realsr_upscale_frames(log_scalefactor,mode)
            
            # If requested, add interpolated frames
            if restart_step >= 3:
                if log_interpolation == "Y":
                    DVD_Process().add_frames(settings)
            
            # Assemble Upscale Frames
            if restart_step >= 2:
                DVD_Process().assemble_frames(float(log_framerate),log_aspect,log_interpolation)

            # Assemble final video
            if restart_step >= 1:
                # Get short name from log file
                log_short_name = os.path.splitext(os.path.basename(log_file))[0]
                
                # Apply audio to upscaled video to create final product
                DVD_Process().assemble_video(log_short_name,log_file)

            # Delete files from working directories
            if settings["General"]["SaveFiles"] == "No":
                Utils.scrub(["extract", "upscale", "insert", "stage"])

            # Add final log entry, close log file and move to output directory
            logging.info("Processing complete from recovered job!")
            logging.shutdown()
            os.rename("dvdupcon.log", ".\\output\\" + log_short_name + ".log")
            
            # Done!
            print()
            print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Done!")
            print()
            print("Be sure to move your video and log file out of the output directory!")
            print()

            # Exit from recovery
            sys.exit()


################
# Let's begin! #
################

# Read in values from settings.ini file
settings = configparser.ConfigParser()
settings.read("settings.ini")

# Print friendly welcome message.
print()
print("Welcome to DVDUpCon!")
print("======= v1.0 =======")
print()

# Check for existing log file on startup.  If exists, assume process failed and begin recovery
if os.path.isfile("dvdupcon.log"):
    DVD_Restart.restart()

# Check for files in the output directory.
output_file_count = int(len(os.listdir("output")))
if output_file_count > 0:
    print("It looks like you have files left in the output directory. Please clear those out and start again!") 
    print()
    sys.exit()

# Open log file
logging.basicConfig(level=logging.INFO, filename="dvdupcon.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Begin processing:") 

# Check for GPU
Utils.gpu()

# Fetch source file to upconvert
dvd_source_file = input("Enter full path to source file: ")

# Check that file exists and is an actual video file
dvd = DVD_Source().dvd_check(dvd_source_file)

# If we fail file check quit, otherwise get short filename for final filename
if dvd != 1:
    print("Looks like we ran into an issue. Please try again!\n")
    sys.exit()
else:
    dvd_short_name = os.path.splitext(os.path.basename(dvd_source_file))[0]        

# If we pass file check show quick summary of file attributes
DVD_Source().dvd_properties(dvd_source_file)

# Ask if we want to proceed with the upconversion
while True:
    dvd_go_nogo = input("Would you like to proceed with the upconversion? (Yes/No): ")

    if dvd_go_nogo.upper() not in {"YES", "Y", "NO", "N"}:
        print("Please enter Yes or No.")
        continue
    else:
        break

# If not, delete log file and quit
if "N" in dvd_go_nogo.upper():
    print("\nOK, maybe next time!\n")
    logging.shutdown()
    os.remove("dvdupcon.log")
    sys.exit()


###############################################################
# We've decided to continue, let's begin processing the file! #
###############################################################

# Set mode to Normal
mode = "N"

# Ask what upscaler we want to use
while True:
    upscale_method = input("Which upscaler method would you like to use? (S)RMD or (R)ealSR: ")

    if upscale_method.upper() not in {"S", "R"}:
        print("Please enter S or R.")
        continue
    else:
        if upscale_method.upper() == "S":
            upscale_method = "S"
            logging.info("Upscaler - SRMD")
        else:
            upscale_method = "R"
            logging.info("Upscaler - RealSR")
        break

# Ask what scale factor we want to use
while True:
    scale_factor = input("What scale factor would you like to use? (2/4): ")

    if scale_factor not in {"2", "4"}:
        print("Please enter 2 or 4.")
        continue
    else:
        logging.info(f"Scale Factor - {scale_factor}" )
        break

# Ask if we want to use frame interpolation
while True:
    use_interpolation = input("Would you like to use frame interpolation? (Yes/No): ")

    if use_interpolation.upper() not in {"YES", "Y", "NO", "N"}:
        print("Please enter Yes or No.")
        continue
    else:
        logging.info("Interpolation - " + use_interpolation.upper())
        break

if "N" in use_interpolation.upper():
    use_interpolation = "N"
else:
    use_interpolation = "Y"

print()

# Extract Frames
DVD_Process().extract_frames(dvd_source_file)

# Upscale Frames
if upscale_method == "S":
    DVD_Process().srmd_upscale_frames(settings,scale_factor,mode)
else:
    DVD_Process().realsr_upscale_frames(scale_factor,mode)

# If requested, add interpolated frames
if use_interpolation == "Y":
    DVD_Process().add_frames(settings)    

# Assemble Upscale Frames
DVD_Process().assemble_frames(dvd_source_frame_rate,dvd_source_aspect_ratio,use_interpolation)

# Apply audio to upscaled video to create final product
DVD_Process().assemble_video(dvd_short_name,dvd_source_file)

# Delete files from working directories
if settings["General"]["SaveFiles"] == "No":
    Utils.scrub(["extract", "upscale", "insert", "stage"])

# Add final log entry, close log file and move to output directory
logging.info("Processing complete!")
logging.shutdown()
os.rename("dvdupcon.log", ".\\output\\" + dvd_short_name + ".log")

# Done!
print()
print(time.strftime("%Y-%m-%d %I:%M:%S %p") + " - Done!")
print()
print("Be sure to move your video and log file out of the output directory!")
print()
