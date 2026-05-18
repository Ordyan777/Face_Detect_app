# Face Detect App/Script
# Alpha version of a face recognition and camera management system.

Created for the “Bakhakats Educational School”
(Real School Goris)

Designed for Linux systems (Ubuntu recommended).


- Minimum Requirements

Ubuntu 24.04+
Python 3.10+
Internet connection
Webcam or RTSP Camera
Enough disk space for dependencies


- Features

 Face Recognition
 USB Camera Support
 RTSP Camera Support
 Camera Auto Detection
 Dataset Collection
 Face Encoding Generator
 Low Delay Stream Mode
 Multi-Camera Support
 Logging System


----------------------
|Installation and Run|
----------------------

Open Terminal  ( ctrl + alt + t ) , and type this command

1. Install required libs
``` sh
sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
```
 

2. Write this command on terminal
   ``` sh
   git clone https://github.com/Ordyan777/Face_Detect_App
   ```

3. Now go to cloned directory and run venv
     ``` sh
      cd Face_Detect_App 
      python3.10 -m venv .venv
    source .venv/bin/activate
    ```
3.1 If You Using Fish , Try This Command
``` sh
source .venv/bin/activate.fish
```

4. Installing Requirements libs for Camera
   ``` py
   pip3.10 install -r requirements.txt
   ```

# all python files are located in this folder old_pythons_files #

5. For a test write
   ``` py
   python3.10 venv_test.py
   ```

---==== Advanced Control Panel for USB/RTSP Cameras ===---


For a test ,write And Check Your Camera 
``` py
python3.10 toolsV0.1.py
```


