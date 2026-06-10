# Face Detect App

Beta version of a face recognition and camera management system for Linux.

Created for Real School Goris.



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
- Boost FPS on ( REC / FACE ) 
- NEW Telegram Bot notifications ( soon ... ) 

---

## Requirements

- Ubuntu 24.04+
- Python 3.10+
- USB Webcam or RTSP camera
- Internet connection
- Enough disk space - ~1GB

Tested on:
- SmartNet Camera V380 Q16S-1 ( Real quality 720P , don't show faces , only small pixels )
- USB Camera 


----------------------
|Installation and Run|
----------------------

Open Terminal  ( ctrl + alt + t ) , and type this command

1. Install required ( Special Python3.10 ) & library's
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

4. Installing Requirements library's
   ``` py
   pip3.10 install -r requirements.txt
   ```

5. Testing Virtual Environment
   ``` py
   python3.10 old_python_files/venv_test.py
   ```

---==== Advanced Control Panel for USB/RTSP Cameras ===---


Advanced Control Panel for All Cameras ( RTSP/USB ) 
``` sh
./start.sh
```


