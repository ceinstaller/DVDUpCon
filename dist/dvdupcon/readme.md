# DVDUpCon

DVDUpCon is an open source tool for upconverting video files.

## What and Why

After using other open source and commercial tools, I was stymied by two issues.  First was the incorrect handling of DAR (Display Aspect Ratio), the second was smooth recovery from failed runs.  In order to address these issues, I decided to write my own program in Python.  My initial focus is real world video versus anime but future versions may include other upscalers.  For version 1.0 image upscaling is handled by SRMD or RealSR, interpolation is achieved using RIFE.

## Requirements

Testing was done using Windows 10 & 11 with an NVidia GPU.  A check for an NVidia GPU is done at program startup.  AMD GPU testing is on my list of things to do for a future version.  

## Usage

Version 1.0 is command line only.  

## Known Issues

If the upscaler settings are pushed too far, you may see the 'vkQueueSubmit failed -4' error in the terminal and see black images in the output file.  If the default settings are used, this shouldn't be an issue.

## Other Open Source Projects Used

FFMPEG (https://ffmpeg.org/)

SRMD NCNN Vulkan (https://github.com/nihui/srmd-ncnn-vulkan)

RealSR NCNN Vulkan (https://github.com/nihui/realsr-ncnn-vulkan)

RIFE NCNN Vulkan (https://github.com/nihui/rife-ncnn-vulkan)
