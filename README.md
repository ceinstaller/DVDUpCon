<div align="center">

<img src="./images/DVDUpCon_Logo.png" alt="DVDUpCon Logo" width="488" height="132"/>

![GitHub top language](https://img.shields.io/github/languages/top/ceinstaller/DVDUpCon)
![GitHub last commit](https://img.shields.io/github/last-commit/ceinstaller/DVDUpCon)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

DVDUpCon is an open source tool for upconverting video files.

</div>

## About

After using other open source and commercial tools, I was stymied by two issues.  First was the incorrect handling of DAR (Display Aspect Ratio), the second was smooth recovery from failed runs.  In order to address these issues, I decided to write my own program in Python.  My initial focus is real world video versus anime but future versions may include other upscalers.  For version 1.0 image upscaling is handled by SRMD or RealSR, interpolation is achieved using RIFE.

## Requirements

Testing was done using Windows 10 & 11 with an NVidia GPU.  A check for an NVidia GPU is done at program startup.  AMD GPU testing is on my list of things to do for a future version.  

## Usage

Open a terminal (cmd) window and run dvdupcon.exe.  When promopted, enter the path to the file to be upconverted.  Answer a few questions about how you would like the upconversion to be handled.  (Which upscaler to use, scale factor, weather to use frame interpolation.)  The upconversion process will run and drop the upconverted video and the corresponding log file into the output directory.  Please see the manual for more information.

## Known Issues

If the upscaler settings are pushed too far, you may see the 'vkQueueSubmit failed -4' error in the terminal and see black images in the output file.  If the default settings are used, this shouldn't be an issue.  Please see the manual for more information.

## To Do List

 - Create Windows GUI for ease of use.
 - More robust error handling
 - Ability to operate on a directory of video files
 - Add additional scalers and models

## License

Distributed under the MIT License

## Open Source Projects Used

FFMPEG (https://ffmpeg.org/)

SRMD NCNN Vulkan (https://github.com/nihui/srmd-ncnn-vulkan)

RealSR NCNN Vulkan (https://github.com/nihui/realsr-ncnn-vulkan)

RIFE NCNN Vulkan (https://github.com/nihui/rife-ncnn-vulkan)
