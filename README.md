# Face Detect App/Script Beta 
Created for Bakhakats Educational School a.k.a. ( Real School Goris )

FOR LINUX ( Ubuntu default )


| Minimum Requirements for test |
- Python3.10
- Ubuntu 24.10+
- And have enough space to install scripts.
- Tested on the SmartNet Camera V380 model.Q16S-1


| Does work with Python 3.9- |
---------------------------------

# Copy this script , and paste in the terminal , and press enter

``` sh
curl -s https://pastebin.com/raw/0XdmpDkm | bash
```
- That Python3.10 install script ( That not a virus ) 


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
      python3.10 -m venv .venv310
    source .venv310/bin/activate
    ```
3.1 If You Using Fish , Try This Command
``` sh
source .venv310/bin/activate.fish
```

4. Installing Requirements libs for Camera
   ``` py
   pip3.10 install -r requirements.txt
   ```

6. For a test write
   ``` py
   python3.10 venv_test.py
   ```

8. If venv_test.py working , write
   ``` py
   face_detect.py *and select photo*
   ```

---==== Multitool for RTSP Camera ===---


For a test write And Check Your Camera 
``` py
python3.10 tools.py
```

