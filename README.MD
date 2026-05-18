# Face Detect App

Alpha version of a face recognition and camera management system for Linux.

Created for “Bakhakats Educational School” (Real School Goris).

---

## Features

- Face recognition
- USB camera support
- RTSP camera support
- Multi-camera support
- Camera auto-detection
- Dataset collection
- Logging system
- Face encoding generator

---

## Requirements

- Ubuntu 24.04+
- Python 3.10+
- Webcam or RTSP camera
- Internet connection
- Enough disk space

Tested on:
- SmartNet Camera V380 Q16S-1
- USB Camera 


----------------------
|Installation and Run|
----------------------

Open Terminal  ( ctrl + alt + t ) , and type this command

1. Install required python3.10 & libs
``` sh
sudo ./install.sh
```

2. Clone repository
   ``` sh
   git clone https://github.com/Ordyan777/Face_Detect_App
   ```

3. Now go to cloned directory and run venv
     ``` sh
      cd Face_Detect_App 
      python3.10 -m venv .venv
    source .venv/bin/activate
    ```

4. Installing Requirements libs for Face_Detect_Script
   ``` py
   pip3.10 install -r requirements.txt
   ```

5. Test Virtual Environment
   ``` py
   python3.10 venv_test.py
   ```

---==== Advanced Control Panel for USB/RTSP Cameras ===---


Advanced Control Panel for All Cameras ( RTSP/USB ) 
``` py
python3.10 main_menu.py
```


