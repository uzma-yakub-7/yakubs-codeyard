# NovaAssist Writing Engine — Setup Guide for Windows

nova-ai chatbot/

├── venv/

├── .env

├── .gitignore

├── langgraph_backend.py              
├── langgraph_database_backend.py     
├── langgraph_tool_backend.py         
├── langgraph_mcp_backend.py          
├── langraph_rag_backend.py           
├── streamlit_frontend.py             
├── streamlit_frontend_streaming.py   
├── streamlit_frontend_database.py    
├── streamlit_frontend_threading.py   
├── streamlit_frontend_mcp.py         
├── streamlit_rag_frontend.py         
└── requirements.txt

## Prerequisites
Before starting, make sure you have the following installed on your PC.

---

## Install Git
- Go to https://git-scm.com/install/windows


## Install VS Code
- Go to https://code.visualstudio.com
- Download and install VS Code for Windows
- Launch VS Code after installation

---

## Install Python
- Go to https://www.python.org/downloads
- Navigate to "Or  get the standalone installer for Python 3.14.4"
- Click on Python 3.14.4 Link. Only if you want to choose exactly where (which drive/folder) to install it.
- Go to Downloads
- Run the installer
- Select Customize Installation 
- During installation, check the box that says:
  ✅ "Add Python to PATH"
- This is very important — do not skip it!

---

## Restart Your PC
- After installation, restart your PC
- This makes sure PATH changes take effect

---

## Test Python in Terminal
- Open Command Prompt
- Type:
  python --version
- You should see something like: Python 3.11.x
- If you see a version number, Python is installed correctly ✅

---

## Install Python Extension in VS Code
- Open VS Code
- Press Ctrl + Shift + X to open Extensions
- Search for "Python"
- Install the one by Microsoft ✅

---

## Set Up Your Project Folder
Choose one of these two methods:

### Method A — Create folder manually:
- Open File Explorer
- Choose a drive (e.g. E:)
- Create a new folder (e.g. name-ai chatbot)
- Open VS Code
- Go to File → Add Folder to Workspace
- Select your folder
- Open VS Code terminal (Ctrl + backtick)
- Change terminal to Command Prompt
- Type:
  git init
- Press Enter to initialize git
- Type:
  code .
- Press Enter

### Method B — Clone from GitHub:
- Open VS Code (Command Prompt terminal)
- Change location. D: —> Press Enter
- Type:
  git clone https://github.com/your-repo-link
- Press Enter
- GitHub repo will appear in VS code as folder. And folder will automatically be saved to the drive you choose.
- Edit the files Or Create New File. Do not Forget to Save Your Files. 

---

## Get API Key
- Go to https://console.groq.com
- Sign up with your Google account
- Click "API Keys" on the left sidebar
- Click "Create API Key"
- Copy the key

---

## Create .env File
- Inside your project folder, create a file called .env
- Add this inside:
  GROQ_API_KEY=paste_your_key_here
- Save the file

---

## Create Virtual Environment
- Open VS Code terminal ( Command Prompt)
- Navigate to your project folder:
  cd ai-chatbot
- Create virtual environment:
  python -m venv venv
- Activate it:
  venv\Scripts\activate
- You should see (venv) in your terminal ✅
- Keep this Terminal Open to Run and Test

---

## Install Required Packages
- Make sure (venv) is active in your terminal
- Run:
   - pip install langchain-groq. Press Enter.
   - pip install langgraph langchain langchain-groq streamlit python-dotenv duckduckgo-search langchain-community faiss-cpu pypdf langgraph-checkpoint-sqlite. Enter
   - pip install -U ddgs. Enter
- Wait for each installation to complete ✅

---

## Create .gitignore File
- Inside your project folder, create a file called .gitignore
- Add this inside:
  - venv/
  - .env
  - __pycache__/
  - *.db
- Save the file

---

## Select Python Interpreter in VS Code
- Press Ctrl + Shift + P
- Type: Select Interpreter
- Choose the one that says:
  Python (venv) .\venv\Scripts\python.exe
- This auto activates venv every time you open terminal ✅

---

## Run the App
- In your terminal, run:
  streamlit run streamlit_frontend_threading.py
- Your browser will open automatically
- NovaAssist Writing Engine is live! 🎉

---

## Screen Recording
- If your PC has TWO ports (green + pink):
    - Green = speakers/headphones (sound out)
    - Pink = microphone (sound in).

- Install Screen Recorder
    - Go to Browser. Search for Bandicam
    - Install Bandicam to your device:
    - Plug in mic (pink port). 
    - If using headset: Plug into green + pink ports (desktop).
  
- Set mic in Windows:
  - Right-click 🔊 sound icon (bottom right)
  - Click Sound settings.
  - Under Input: Choose your microphone (e.g., “Headset Mic”)
  - Speak → check if bar moves ✅

- Setup Bandicam audio:
   - Open Bandicam
   - Go to Video tab → Settings
   - Under Sound: 
       - Primary Sound Device → Speakers (your PC sound)
       - Secondary Sound Device → Your Microphone
   - Click OK
 
- Test: 
   - Go to Bandicam. Click REC. Speak
   - Stop and play → confirm voice recorded
 
## Struggling With Recording Your Voice? 
- Here's an alternative:
     - Open your phone
     - Use Voice Recorder app (default app)
     - Open Bandicam
     - Select screen recording mode and turn on screen recording
     - Record your voice while watching your project on the Desktop Screen (Monitor).
     - Save the screen recording and  audio file
     - Go to Canva or Capcut. Upload Screen Recording (from your desktop). Upload audio file (from your phone). Adjust, edit either from Desktop or from your pc.
     - Save the file:
          - If edited from phone, save the file to Downloads. Go to GitHub. Select Your Repo. Press on 3 dots beside the green colored Code button. Press on Upload file. Press on Choose Your File. Navigate to your downloaded file and upload the file. Commit: Added file via upload. Press on Commit Changes. 
         - If edited from the desktop, save it to your project folder. Go to VS Code. Open Terminal Command Prompt. Push the screen recording to Github


## Pushing to GitHub
- Open GitBash Terminal in VS Code. 
- Tell Git who you are:
    - git config --global user.name "your-github-profile-username" . Enter
    - git config --global user.email "your-email-in-github" . Enter
- Check if it worked:  git config --global --list
- Check repo status: git status
- You should see your project files
- Stage Files: git add .
- Confirm Stagging: git status
- You should now see:"Changes to be committed: (many files)"
- Commit files:
    - git commit -m "Added Files" . Enter
    - git push. Enter

 ---

 ## Adding Images to README.md
 - Inside your project create a folder named images.
 - Upload images to that folder. Image type can be png,jpg or jpeg. You can Also upload videos to that folder.
 - Inside < />, type: img src="images/demo.png" width="50%"
 - Save the file.


## Hosting Online (Streamlit Cloud)
- Push your code to GitHub
- Go to https://streamlit.io/cloud
- Sign in with GitHub
- Click "New App"
- Select your repo and file: streamlit_frontend_threading.py
- Add your GROQ_API_KEY in the secrets section
- Click Deploy 🚀

---

## Notes
- Never share your .env file
- Never push .env to GitHub
- Always activate venv before running the app
- nova_memory.db is auto created — no need to create manually

## Got Stuck?
- Feel free to reach out to uzmayakub27@gmail.com

## Happy Coding 😊🚀
