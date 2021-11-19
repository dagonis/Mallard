``` 
 ____ ____ ____ ____ ____ ____ ____ 
||M |||A |||L |||L |||A |||R |||D ||
||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|

``` 


# Mallard
Ducky Script Decoder and More!

Absolutely requires Python3.7+ (go dataclasses!). Will break on anything older.

## Introduction
I love Keyboards and HID attacks. As such, one of my favorite devices of all time is the [USB Rubber Ducky](https://hak5.org/products/usb-rubber-ducky-deluxe). 

Inspiration struck me one night (last night, if you are reading this on Nov 18 2021), to write a decoder with some basic analysis features. This was a challenge I had thought about undertaking all year, and now was the right time.

I asked myself "Does the world need another DuckyScript decoder?", and the answer was "Probably Not". I also asked "Do *I* need to write a DuckyScript decoder?" and the answer was a resounding "Absolutely Yes". So here we are. The idea to add analysis was inspired by my love of enriching data quickly to help save as many seconds as possible for security professionals.

I took this time to tinker with dataclasses and focus on a composition based design pattern. I had a lot of fun! I love objects and breaking stuff down to the tiniest constituents parts (I feel connected to the [Ancient Greek Atomists](https://plato.stanford.edu/entries/atomism-ancient/) in this way). I will admit, the code got away from me a bit. The `__post_init__` of the `DuckyScript` object is a particularly terrifying. None the less, I had a great time putting this together, and I look forward to continuing to add some analysis features. 


## Usage

```
$ python3 mallard --help 
usage: mallard [-h] [--file FILE] [--no_analyze] [--output_file OUTPUT_FILE] [--analysis_file ANALYSIS_FILE] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  The file to decode, default: inject.bin
  --no_analyze, -A      Include this switch to turn off analysis of the duckyfile
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        File to save decoded ducky script to. Default will print duckyfile to screen.
  --analysis_file ANALYSIS_FILE
                        Location to output analysis. Default will print analysis to screen.
  --debug               Enable Debug Logging.
```

### Basic
```
$ python3 mallard
STRING Hello
ENTER
STRING World
GUI SPACE
ENTER
STRING terminal
ENTER


Mallard Analysis and Commentary
================================
Spotlight opened (GUI SPACE) - Possible Mac Attack
```

### Provide a Specific File
```
$ python3 mallard -f test_files/wifi_password_grabber.bin
DELAY 2000
GUI d
GUI r
DELAY 500
STRING cmd
ENTER
DELAY 1000
STRING cd "%USERPROFILE%\Desktop"
[SNIP]
```
