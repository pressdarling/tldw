# **TL/DW: Too Long, Didnt Watch**
## Download, Transcribe & Summarize: Video+Audio+Documents+Articles & Books(WIP). All automated 
#### More: Full-Text-Search across everything ingested, Local LLM inference as part of it for those who don't want to mess with setting up an LLM, and a WebApp to interact with the script in a more user-friendly manner (all features are exposed through it).
#### The original scripts by `the-crypt-keeper` are available here: [scripts here](https://github.com/the-crypt-keeper/tldw/tree/main/tldw-original-scripts)
#### My idea is that this repo will hold 'working' versions that one can reliably use. My fork will contain the dev version (git branches? whats that?)
## [Public Demo](https://huggingface.co/spaces/oceansweep/Vid-Summarizer)
#### Demo may be broken but should be working. If it's not, let me know. (HF dev spaces is touchy...)

![License](https://img.shields.io/badge/license-apache2.0-green)

----------

### Table of Contents
- [What?](#what) | [Quickstart](#quickstart) | [Setup](#setup) | [Using tldw](#using) | [What's in the Repo / Pieces](#whatbox) | [Helpful Terms and Things to Know](#helpful) | [Setting up a Local LLM Inference Engine](#localllm) | [Credits](#credits)

----------

### <a name="what"></a> What is this (TL/DW)?
- **101**
  - The end goal of this project, is to be a personal data assistant, that ingests recorded audio, videos, articles, free form text, documents, and books as text into a SQLite DB, so that you can then search across it at any time, and be able to retrieve/extract that information, as well as be able to ask questions about it.
  - And of course, this is all open-source/free, with the idea being that this can massively help people in their efforts of research and learning.
- **Don't care, give me code**
  * `git clone https://github.com/rmusser01/tldw` -> `cd tldw` -> `python -m venv .\` -> `Linux: ./scripts/activate` / `Windows: . .\scripts\activate.ps1` -> `pip install -r requirements.txt` -> 
    * CLI usage: `python summarize.py <video_url> -api <LLM AP> -k tag_one tag_two tag_three` 
    - GUI usage: `python summarize.py -gui`
    - GUI with local LLM: `python summarize.py -gui --local_llama` (will ask you questions about which model to download)
  - Any site supported by yt-dl is supported, so you can use this with sites besides just youtube. 
    - **List of supported sites:** https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
- **Short Summary**
  - Ingest content from a URL or a local file. Can be done in batches with a text file containing a list of URLs or paths to local files as well as from the GUI.
    - (GUI only does links, no local files for videos, but it will do local audio files)
  - Transcriptions can then be shuffled off to an LLM API endpoint of your choice, whether that be local or remote. 
    - (Local LLMs are supported through llama.cpp, oobabooga/text-gen-webui, kobold.cpp, with TabbyAPI, vLLM, Triton and Aphrodite support planned)
  - Rolling summaries (i.e. chunking up input and doing a chain of summaries) is supported. 
    - The original scripts that this repo was originally based off of is here: [scripts here](https://github.com/the-crypt-keeper/tldw/tree/main/tldw-original-scripts) which to my understanding was the purpose of this project originally.
- **Longer Summary/Goal**
  - Act as a Multi-Purpose Research tool. The idea being that there is so much data one comes across, and we can store it all as text. (with tagging!)
  - Imagine, if you were able to keep a copy of every talk, research paper or article you've ever read, and have it at your fingertips at a moments notice.
  - Now, imagine if you could ask questions about that data/information(LLM), and be able to string it together with other pieces of data, to try and create sense of it all (RAG)
  - The end goal of this project, is to be a personal data assistant, that ingests recorded audio, videos, articles, free form text, documents, and books as text into a SQLite (for now, would like to build a shim for ElasticSearch/Similar) DB, so that you can then search across it at any time, and be able to retrieve/extract that information, as well as be able to ask questions about it. (Plus act as a nice way of personally tagging data for possible future training of your personal AI agent :P)
  - And of course, this is all open-source/free, with the idea being that this can massively help people in their efforts of research and learning.

For commercial API usage for use with this project: Claude Sonnet 3.5, Cohere Command R+, DeepSeek. Flipside I would say none honestly. The (largest players) will gaslight you and charge you money for it. Fun.
From @nrose 05/08/2024 on Threads:
```
No, it’s a design. First they train it, then they optimize it. Optimize it for what- better answers?
  No. For efficiency. 
Per watt. Because they need all the compute they can get to train the next model.So it’s a sawtooth. 
The model declines over time, then the optimization makes it somewhat better, then in a sort of 
  reverse asymptote, they dedicate all their “good compute” to the next bigger model.Which they then 
  trim down over time, so they can train the next big model… etc etc.
None of these companies exist to provide AI services in 2024. They’re only doing it to finance the 
 things they want to build in 2025 and 2026 and so on, and the goal is to obsolete computing in general
  and become a hidden monopoly like the oil and electric companies. 
2024 service quality is not a metric they want to optimize, they’re forced to, only to maintain some 
  directional income
```

For offline LLM usage, I recommend the following models(in no particular order past the first):
  1. Samantha-Mistral-instruct-7B-Bulleted-Notes - https://huggingface.co/cognitivetech/samantha-mistral-instruct-7b_bulleted-notes_GGUF
     * Reason being is that its 'good enough', otherwise would recommend Command-R+, either self-hosted, or through a personal API key (it's free for 1k requests a month...)
  2. Inkbot-13B-8k-0.2
     * https://huggingface.co/Tostino/Inkbot-13B-8k-0.2
  3. Microsfot Phi-3-mini-4k-Instruct
     * https://huggingface.co/microsoft/Phi-3-mini-4k-instruct / GGUF: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
     * Also the 128k Context version: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct / GGUF: https://huggingface.co/bartowski/Phi-3.1-mini-128k-instruct-GGUF
  4. Cohere Command-R+
     * https://huggingface.co/cohere-ai/Command-R-plus / GGUF: https://huggingface.co/dranger003/c4ai-command-r-plus-iMat.GGUF
  5. Phi-3-Medium-4k-Instruct
     * https://huggingface.co/microsoft/Phi-3-medium-4k-instruct / GGUF: https://huggingface.co/bartowski/Phi-3-medium-4k-instruct-GGUF
     * Also the 128k Context version: https://huggingface.co/microsoft/Phi-3-medium-128k-instruct / GGUF: https://huggingface.co/bartowski/Phi-3-medium-128k-instruct-GGUF
  6. Hermes-2-Theta-Llama-3-8B
     * https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-8B / GGUF: https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-8B-GGUF

----------

**CLI Screenshot**
- **See [Using](#using)**


**GUI Screenshot**
![tldw-summarization-gui-demo](./Tests/GUI-Front_Page.PNG)

----------

### Quickstart
  1. Update your drivers. (I.e. CUDA for Nvidia GPUs, or AMD drivers (ROCM) for AMD GPUs )
     - Windows CUDA: https://developer.nvidia.com/cuda-downloads?target_os=Windows
  2. Install Python3 for your platform - https://www.python.org/downloads/
  3. Download the repo: `git clone https://github.com/rmusser01/tldw` or manually download it (Green code button, upper right corner -> Download ZIP) and extract it to a folder of your choice.
  4. Open a terminal, navigate to the directory you cloned the repo to, or unzipped the downloaded zip file to, and run the following commands:
     - Create a virtual env: `python -m venv .\`
     - Launch/activate your virtual env: `Linux: ./scripts/activate` / `Windows: . .\scripts\activate.ps1`
       * If you don't already have cuda installed(Nvidia), `py -m pip install --upgrade pip wheel` & `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118` (Last updated 6/2024)
       * Or AMD (Windows): `pip install torch-directml`
       * Or CPU Only: `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu` (Last updated 6/2024)
     - `pip install -r requirements.txt` - may take a bit of time...
  5. **You are Ready to Go!** Check out the below sample commands: 

- **Run it as a WebApp**
  * `python summarize.py -gui` - This requires you to either stuff your API keys into the `config.txt` file, or pass them into the app every time you want to use it.
    * It exposes every CLI option, and has a nice toggle to make it 'simple' vs 'Advanced'
    * Has an option to download the generated transcript, and summary as text files from the UI.
    * Can also download video/audio as files if selected in the UI (WIP - doesn't currently work)
    - Gives you access to the whole SQLite DB backing it, with search, tagging, and export functionality
      * Yes, that's right. Everything you ingest, transcribe and summarize is tracked through a local(!) SQLite DB.
      * So everything you might consume during your path of research, tracked and assimilated and tagged.
      * All into a shareable, single-file DB that is open source and extremely well documented. (The DB format, not this project :P) 

- **Transcribe audio from a Youtube URL:**
  * `python summarize.py https://www.youtube.com/watch?v=4nd1CDZP21s`

- **Transcribe audio from a Youtube URL & Summarize it using (`anthropic`/`cohere`/`openai`/`llama` (llama.cpp)/`ooba` (oobabooga/text-gen-webui)/`kobold` (kobold.cpp)/`tabby` (Tabbyapi)) API:**
  * `python summarize.py https://www.youtube.com/watch?v=4nd1CDZP21s -api <your choice of API>`
    - Make sure to put your API key into `config.txt` under the appropriate API variable

- **Transcribe a list of Youtube URLs & Summarize them using (`anthropic`/`cohere`/`openai`/`llama` (llama.cpp)/`ooba` (oobabooga/text-gen-webui)/`kobold` (kobold.cpp)/`tabby` (Tabbyapi)) API:**
  * `python summarize.py ./ListofVideos.txt -api <your choice of API>`
    - Make sure to put your API key into `config.txt` under the appropriate API variable

- **Transcribe & Summarize a List of Videos on your local filesytem with a text file:**
  * `python summarize.py -v ./local/file_on_your/system`

- **Download a Video with Audio from a URL:**
  * `python summarize.py -v https://www.youtube.com/watch?v=4nd1CDZP21s`s

- **Perform a summarization of a longer transcript using 'Chunking'**
  * `python summarize.py -roll -detail 0.01 https://www.youtube.com/watch?v=4nd1CDZP21s`
    * Detail can go from `0.01` to `1.00`, increments at a measure of `.01`.

- **Convert an epub book to text and ingest it into the DB**
  1. Download/Install pandoc for your platform:
    * https://pandoc.org/installing.html
  2. Convert your epub to a text file:
     * `$ pandoc -f epub -t plain -o filename.txt filename.epub`
  3. Ingest your converted epub into the DB:
     * `python summarize.py path/to/your/textfile.txt --ingest_text_file --text_title "Book Title" --text_author "Author Name" -k additional,keywords`

----------
### <a name="setup"></a>Setting it up
- **Requirements**
  - Python3
  - ffmpeg
  - pandoc (for epub to markdown conversion) - https://pandoc.org/installing.html
    - `pandoc -f epub -t markdown -o output.md input.epub` -> Can then import/ingest the markdown file into the DB.
    - If done from the CLI using the `--ingest_text_file` flag, you can specify the title and author of the book, as well as any additional keywords you'd like to tag it with. (if not a regex will attempt to identify it)
    - Or just do it through the GUI, drag and drop the file into the UI, set the Title, Author, and any keywords and hit `Import Data`.
  - GPU Drivers/CUDA drivers or CPU-only PyTorch installation for ML processing
    - Apparently there is a ROCm version of PyTorch.
      - MS Pytorch: https://learn.microsoft.com/en-us/windows/ai/directml/pytorch-windows -> `pip install torch-directml`
      - Use the 'AMD_requests.txt' file to install the necessary packages for AMD GPU support. Simply rename it before use.
      - AMD Pytorch: https://rocm.docs.amd.com/projects/radeon/en/latest/docs/install/wsl/install-pytorch.html
  - API keys for the LLMs you want to use (or use the local LLM option/Self-hosted)
  - System RAM (8GB minimum, realistically 12GB)
  - Disk Space (Depends on how much you ingest, but 6GB or so should be fine for the total size of the project + DB)
    - This can balloon real quick. The whisper model used for transcription can be 1-2GB per.
    - Pytorch + other ML libraries will also cause the size to increase.
    - As such, I would say you want at least 8GB of free space on your system to devote to the app.
    - Text content itself is tiny, but the supporting libraries + ML models can be quite large.
- **Linux**
    1. Download necessary packages (Python3, ffmpeg - `sudo apt install ffmpeg / dnf install ffmpeg`, Update your GPU Drivers/CUDA drivers if you'll be running an LLM locally)
    2. Open a terminal, navigate to the directory you want to install the script in, and run the following commands:
    3. `git clone https://github.com/rmusser01/tldw`
    4. `cd tldw`
    5. Create a virtual env: `python -m venv ./`
    6. Launch/activate your virtual environment: `source ./bin/activate`
    7. Setup the necessary python packages:
       * Following is from: https://docs.nvidia.com/deeplearning/cudnn/latest/installation/linux.html
       * If you don't already have cuda installed, `py -m pip install --upgrade pip wheel` & `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118` 
       * Or CPU Only: `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu`
       * https://pytorch.org/get-started/previous-versions/#linux-and-windows-3
    8. Then see `Linux && Windows`
- **MacOS**
    1. I don't own a mac/have access to one reliably so I can't test this, but it should be the same as/similar to Linux.
- **Windows**
    1. Download necessary packages ([Python3](https://www.python.org/downloads/windows/), Update your GPU drivers/CUDA drivers if you'll be running an LLM locally, ffmpeg will be installed by the script)
    2. Open a terminal, navigate to the directory you want to install the script in, and run the following commands:
    3. `git clone https://github.com/rmusser01/tldw`
    4. `cd tldw`
    5. Create a virtual env: `python -m venv ./`
    6. Launch/activate your virtual env: PowerShell: `. .\scripts\activate.ps1` or for CMD: `.\scripts\activate.bat`
    7. Setup the necessary python packages:
       - Cuda
         * https://docs.nvidia.com/deeplearning/cudnn/latest/installation/windows.html
           * If you don't already have cuda installed, `py -m pip install --upgrade pip wheel` & `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118` 
       - CPU Only: `pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu`
           * https://pytorch.org/get-started/previous-versions/#linux-and-windows-3
       - AMD
         * `pip install torch-directml`
    8. See `Linux && Windows`
- **Linux && Windows**
    1. `pip install -r requirements.txt` - may take a bit of time...
    2. **Script Usage:**
       - Put your API keys and settings in the `config.txt` file.
         - This is where you'll put your API keys for the LLMs you want to use, as well as any other settings you want to have set by default. (Like the IP of your local LLM to use for summarization)
       - (make sure your in the python venv - Run `./bin/activate` or `.\scripts\activate.ps1` or `.\scripts\activate.bat` from the `tldw` directory)
       - Run `python ./summarize.py <video_url>` - The video URL does _not_ have to be a youtube URL. It can be any site that ytdl supports.
       - You'll then be asked if you'd like to run the transcription through GPU(1) or CPU(2).
         - Next, the video will be downloaded to the local directory by ytdl.
         - Then the video will be transcribed by faster_whisper. (You can see this in the console output)
           * The resulting transcription output will be stored as both a json file with timestamps, as well as a txt file with no timestamps.
       - Finally, you can have the transcription summarized through feeding it into an LLM of your choice.
    3. **GUI Usage:**
       - Put your API keys and settings in the `config.txt` file.
         - This is where you'll put your API keys for the LLMs you want to use, as well as any other settings you want to have set by default. (Like the IP of your local LLM to use for summarization)
       - (make sure your in the python venv - Run `source ./bin/activate` or `.\scripts\activate.ps1` or `.\scripts\activate.bat` from the `tldw` directory)
       - Run `python ./summarize.py -gui` - This will launch a webapp that will allow you to interact with the script in a more user-friendly manner.
         * You can pass in the API keys for the LLMs you want to use in the `config.txt` file, or pass them in when you use the GUI.
         * You can also download the generated transcript and summary as text files from the UI.
         * You can also download the video/audio as files from the UI. (WIP - doesn't currently work)
         * You can also access the SQLite DB that backs the app, with search, tagging, and export functionality.
    4. **Local LLM with the Script Usage:**
       - (make sure your in the python venv - Run `source ./bin/activate` or `.\scripts\activate.ps1` or `.\scripts\activate.bat` from the `tldw` directory)
       - I recognize some people may like the functionality and idea of it all, but don't necessarily know/want to know about LLMs/getting them working, so you can also have the script download and run a local model, using system RAM and llamafile/llama.cpp.
       - Simply pass `--local_llm` to the script (`python summarize.py --local-llm`), and it'll ask you if you want to download a model, and which one you'd like to download.
       - Then, after downloading and selecting a model, it'll launch the model using llamafile, so you'll have a browser window/tab opened with a frontend to the model/llama.cpp server.
       - You'll also have the GUI open in another tab as well, a couple seconds after the model is launched, like normal.
       - You can then interact with both at the same time, being able to ask questions directly to the model, or have the model ingest output from the transcript/summary and use it to ask questions you don't necessarily care to have stored within the DB. (All transcripts, URLs processed, prompts used, and summaries generated, are stored in the DB, so you can always go back and review them or re-prompt with them)

- **Setting up Epub to Markdown conversion with Pandoc**
    - **Linux / MacOS / Windows**
        - Download and install from: https://pandoc.org/installing.html
- **Converting Epub to markdown**
    - `pandoc -f epub -t markdown -o output.md input.epub`
- **Setting up PDF to Markdown conversion with Marker** (Optional - Necessary to do PDF ingestion/conversion)
    - **Linux**
        1. `sudo apt install python3-venv`
        2. `python3 -m venv ./Helper_Scripts/marker_venv`
        3. `source ./Helper_Scripts/marker_venv/bin/activate`  
        4. `pip install marker`
    - **Windows**
        1. Install python3 from https://www.python.org/downloads/
        2. `python Helper_Scripts\marker_venv\Scripts\activate\activate.ps1`
        3. `pip install marker`
- **Converting PDF to markdown**
    - Convert a Single PDF to Markdown:
        * `marker_single /path/to/file.pdf /path/to/output/folder --batch_multiplier 2 --langs English`
    - Convert a Folder of PDFs to Markdown:
        * `marker /path/to/folder/with/pdfs /path/to/output/folder --batch_multiplier 2 --langs English`
- **Ingest Converted text files en-masse**
    - `python summarize.py <path_to_text_file> --ingest_text_file --text_title "Title" --text_author "Author Name" -k additional,keywords`



----------
### <a name="using"></a>Using tldw
- Single file (remote URL) transcription
  * Single URL: `python summarize.py https://example.com/video.mp4`
- Single file (local) transcription)
  * Transcribe a local file: `python summarize.py /path/to/your/localfile.mp4`
- Multiple files (local & remote)
  * List of Files(can be URLs and local files mixed): `python summarize.py ./path/to/your/text_file.txt"`
- Download and run an LLM using only your system RAM! (Need at least 8GB Ram, realistically 12GB)
  * `python summarize.py -gui --local_llama`

Save time and use the `config.txt` file, it allows you to set these settings and have them used when ran.
```
usage: summarize.py [-h] [-v] [-api API_NAME] [-key API_KEY] [-ns NUM_SPEAKERS] [-wm WHISPER_MODEL] [-off OFFSET] [-vad] [-log {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-gui] [-demo] [-prompt CUSTOM_PROMPT] [-overwrite] [-roll] [-detail DETAIL_LEVEL] [-model LLM_MODEL]
                    [-k KEYWORDS [KEYWORDS ...]] [--log_file LOG_FILE] [--local_llm] [--server_mode] [--share_public SHARE_PUBLIC] [--port PORT] [--ingest_text_file] [--text_title TEXT_TITLE] [--text_author TEXT_AUTHOR] [--diarize]
                    [input_path]

positional arguments:
  input_path            Path or URL of the video

options:
  -h, --help            show this help message and exit
  -v, --video           Download the video instead of just the audio
  -api API_NAME, --api_name API_NAME
                        API name for summarization (optional)
  -key API_KEY, --api_key API_KEY
                        API key for summarization (optional)
  -ns NUM_SPEAKERS, --num_speakers NUM_SPEAKERS
                        Number of speakers (default: 2)
  -wm WHISPER_MODEL, --whisper_model WHISPER_MODEL
                        Whisper model (default: small)| Options: tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3, large, distil-large-v2, distil-medium.en, distil-small.en
  -off OFFSET, --offset OFFSET
                        Offset in seconds (default: 0)
  -vad, --vad_filter    Enable VAD filter
  -log {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Log level (default: INFO)
  -gui, --user_interface
                        Launch the Gradio user interface
  -demo, --demo_mode    Enable demo mode
  -prompt CUSTOM_PROMPT, --custom_prompt CUSTOM_PROMPT
                        Pass in a custom prompt to be used in place of the existing one.
                         (Probably should just modify the script itself...)
  -overwrite, --overwrite
                        Overwrite existing files
  -roll, --rolling_summarization
                        Enable rolling summarization
  -detail DETAIL_LEVEL, --detail_level DETAIL_LEVEL
                        Mandatory if rolling summarization is enabled, defines the chunk  size.
                         Default is 0.01(lots of chunks) -> 1.00 (few chunks)
                         Currently only OpenAI works.
  -model LLM_MODEL, --llm_model LLM_MODEL
                        Model to use for LLM summarization (only used for vLLM/TabbyAPI)
  -k KEYWORDS [KEYWORDS ...], --keywords KEYWORDS [KEYWORDS ...]
                        Keywords for tagging the media, can use multiple separated by spaces (default: cli_ingest_no_tag)
  --log_file LOG_FILE   Where to save logfile (non-default)
  --local_llm           Use a local LLM from the script(Downloads llamafile from github and 'mistral-7b-instruct-v0.2.Q8' - 8GB model from Huggingface)
  --server_mode         Run in server mode (This exposes the GUI/Server to the network)
  --share_public SHARE_PUBLIC
                        This will use Gradio's built-in ngrok tunneling to share the server publicly on the internet. Specify the port to use (default: 7860)
  --port PORT           Port to run the server on
  --ingest_text_file    Ingest .txt files as content instead of treating them as URL lists
  --text_title TEXT_TITLE
                        Title for the text file being ingested
  --text_author TEXT_AUTHOR
                        Author of the text file being ingested
  --diarize             Enable speaker diarization


Sample commands:
    1. Simple Sample command structure:
        summarize.py <path_to_video> -api openai -k tag_one tag_two tag_three

    2. Rolling Summary Sample command structure:
        summarize.py <path_to_video> -api openai -prompt "custom_prompt_goes_here-is-appended-after-transcription" -roll -detail 0.01 -k tag_one tag_two tag_three

    3. FULL Sample command structure:
        summarize.py <path_to_video> -api openai -ns 2 -wm small.en -off 0 -vad -log INFO -prompt "custom_prompt" -overwrite -roll -detail 0.01 -k tag_one tag_two tag_three

    4. Sample command structure for UI debug logging printed to console:
        summarize.py -gui -log DEBUG
```
- Download Audio only from URL -> Transcribe audio:
  >python summarize.py https://www.youtube.com/watch?v=4nd1CDZP21s

- Transcribe audio from a Youtube URL & Summarize it using (anthropic/cohere/openai/llama (llama.cpp)/ooba (oobabooga/text-gen-webui)/kobold (kobold.cpp)/tabby (Tabbyapi)) API:
  >python summarize.py https://www.youtube.com/watch?v=4nd1CDZP21s -api <your choice of API>
    - Make sure to put your API key into `config.txt` under the appropriate API variable

- Download Video with audio from URL -> Transcribe audio from Video:
  >python summarize.py -v https://www.youtube.com/watch?v=4nd1CDZP21s

- Download Audio+Video from a list of videos in a text file (can be file paths or URLs) and have them all summarized:
  >python summarize.py --video ./local/file_on_your/system --api_name <API_name>

- Transcribe & Summarize a List of Videos on your local filesytem with a text file:
  >python summarize.py -v ./local/file_on_your/system

- Run it as a WebApp:
  >`python summarize.py -gui

By default, videos, transcriptions and summaries are stored in a folder with the video's name under './Results', unless otherwise specified in the config file.


------------

### <a name="helpful"></a> Helpful Terms and Things to Know
- Purpose of this section is to help bring awareness to certain concepts and terms that are used in the field of AI/ML/NLP, as well as to provide some resources for learning more about them.
- Also because some of those things are extremely relevant and important to know if you care about accuracy and the effectiveness of the LLMs you're using.
- Some of this stuff may be 101 level, but I'm going to include it anyways. This repo is aimed at people from a lot of different fields, so I want to make sure everyone can understand what's going on. Or at least has an idea.
- LLMs 101(coming from a tech background): https://vinija.ai/models/LLM/
- LLM Fundamentals / LLM Scientist / LLM Engineer courses(Free): https://github.com/mlabonne/llm-course
- **Phrases & Terms**
  - **LLM** - Large Language Model - A type of neural network that can generate human-like text.
  - **API** - Application Programming Interface - A set of rules and protocols that allows one software application to communicate with another.
  - **API Wrapper** - A set of functions that provide a simplified interface to a larger body of code.
  - **API Key** - A unique identifier that is used to authenticate a user, developer, or calling program to an API.
  - **GUI** - Graphical User Interface
  - **CLI** - Command Line Interface
  - **DB** - Database
  - **SQLite** - A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.
  - **Prompt Engineering** - The process of designing prompts that are used to guide the output of a language model.
  - **Quantization** - The process of converting a continuous range of values into a finite range of discrete values.
  - **GGUF Files** - GGUF is a binary format that is designed for fast loading and saving of models, and for ease of reading. Models are traditionally developed using PyTorch or another framework, and then converted to GGUF for use in GGML. https://github.com/ggerganov/ggml/blob/master/docs/gguf.md
  - **Inference Engine** - A software system that is designed to execute a model that has been trained by a machine learning algorithm. Llama.cpp and Kobold.cpp are examples of inference engines.
- **Papers & Concepts**
  1. `Lost in the Middle: How Language Models Use Long Contexts`
    - https://arxiv.org/abs/2307.03172
    - `We analyze the performance of language models on two tasks that require identifying relevant information in their input contexts: multi-document question answering and key-value retrieval. We find that performance can degrade significantly when changing the position of relevant information, indicating that current language models do not robustly make use of information in long input contexts. In particular, we observe that performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models`
  2. `RULER: What's the Real Context Size of Your Long-Context Language Models?`
    - https://arxiv.org/abs/2404.06654
    - `The needle-in-a-haystack (NIAH) test, which examines the ability to retrieve a piece of information (the "needle") from long distractor texts (the "haystack"), has been widely adopted to evaluate long-context language models (LMs). However, this simple retrieval-based test is indicative of only a superficial form of long-context understanding. To provide a more comprehensive evaluation of long-context LMs, we create a new synthetic benchmark RULER with flexible configurations for customized sequence length and task complexity. RULER expands upon the vanilla NIAH test to encompass variations with diverse types and quantities of needles. Moreover, RULER introduces new task categories multi-hop tracing and aggregation to test behaviors beyond searching from context. We evaluate ten long-context LMs with 13 representative tasks in RULER. Despite achieving nearly perfect accuracy in the vanilla NIAH test, all models exhibit large performance drops as the context length increases. While these models all claim context sizes of 32K tokens or greater, only four models (GPT-4, Command-R, Yi-34B, and Mixtral) can maintain satisfactory performance at the length of 32K. Our analysis of Yi-34B, which supports context length of 200K, reveals large room for improvement as we increase input length and task complexity.`
  3. `Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models`
     - https://arxiv.org/abs/2402.14848
     - `Our findings show a notable degradation in LLMs' reasoning performance at much shorter input lengths than their technical maximum. We show that the degradation trend appears in every version of our dataset, although at different intensities. Additionally, our study reveals that the traditional metric of next word prediction correlates negatively with performance of LLMs' on our reasoning dataset. We analyse our results and identify failure modes that can serve as useful guides for future research, potentially informing strategies to address the limitations observed in LLMs.`
  4. Abliteration (Uncensoring LLMs)
     - [Uncensor any LLM with abliteration - Maxime Labonne(2024)](https://huggingface.co/blog/mlabonne/abliteration)
  5. Retrieval-Augmented-Generation
        - [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)
        - https://arxiv.org/abs/2312.10997
        - `Retrieval-Augmented Generation (RAG) has emerged as a promising solution by incorporating knowledge from external databases. This enhances the accuracy and credibility of the generation, particularly for knowledge-intensive tasks, and allows for continuous knowledge updates and integration of domain-specific information. RAG synergistically merges LLMs' intrinsic knowledge with the vast, dynamic repositories of external databases. This comprehensive review paper offers a detailed examination of the progression of RAG paradigms, encompassing the Naive RAG, the Advanced RAG, and the Modular RAG. It meticulously scrutinizes the tripartite foundation of RAG frameworks, which includes the retrieval, the generation and the augmentation techniques. The paper highlights the state-of-the-art technologies embedded in each of these critical components, providing a profound understanding of the advancements in RAG systems. Furthermore, this paper introduces up-to-date evaluation framework and benchmark. At the end, this article delineates the challenges currently faced and points out prospective avenues for research and development. `
  6. Prompt Engineering
     - Prompt Engineering Guide: https://www.promptingguide.ai/ & https://github.com/dair-ai/Prompt-Engineering-Guide
- **Tools & Libraries**
  1. `llama.cpp` - A C++ inference engine. Highly recommend. 
     * https://github.com/ggerganov/llama.cpp
  2. `kobold.cpp` - A C++ inference engine. GUI wrapper of llama.cpp with some tweaks. 
     * https://github.com/LostRuins/koboldcpp
  3. `sillytavern` - A web-based interface for text generation models. Supports inference engines. Ignore the cat girls and weebness. This software is _powerful_ and _useful_. Also supports just about every API you could want.
     * https://github.com/SillyTavern/SillyTavern
  4. `llamafile` - A wrapper for llama.cpp that allows for easy use of local LLMs.
     * Uses libcosomopolitan for cross-platform compatibility. 
     * Can be used to run LLMs on Windows, Linux, and MacOS with a single binary wrapper around Llama.cpp.
  5. `pytorch` - An open-source machine learning library based on the Torch library.
  6. `ffmpeg` - A free software project consisting of a large suite of libraries and programs for handling video, audio, and other multimedia files and streams.
  7. `pandoc` - A free and open-source document converter, widely used as a writing tool (especially by scholars) and as a basis for publishing workflows. 
     * https://pandoc.org/
  8. `marker` - A tool for converting PDFs(and other document types) to markdown. 
     * https://github.com/VikParuchuri/marker
  9. `faster_whisper` - A fast, lightweight, and accurate speech-to-text model. 
      * https://github.com/SYSTRAN/faster-whisper

------------

### <a name="localllm"></a>Setting up a Local LLM Inference Engine
- **Setting up Local LLM Runner**
  - **Llama.cpp**
    - **Linux & Mac**
      1. `git clone https://github.com/ggerganov/llama.cpp`
      2. `make` in the `llama.cpp` folder 
      3. `./server -m ../path/to/model -c <context_size>`
    - **Windows**
      1. `git clone https://github.com/ggerganov/llama.cpp`
      2. Download + Run: https://github.com/skeeto/w64devkit/releases
      3. cd to `llama.cpp` folder make` in the `llama.cpp` folder
      4. `server.exe -m ..\path\to\model -c <context_size>`
  - **Kobold.cpp** - c/p'd from: https://github.com/LostRuins/koboldcpp/wiki
    - **Windows**
      1. Download from here: https://github.com/LostRuins/koboldcpp/releases/latest
      2. `Double click KoboldCPP.exe and select model OR run "KoboldCPP.exe --help" in CMD prompt to get command line arguments for more control.`
      3. `Generally you don't have to change much besides the Presets and GPU Layers. Run with CuBLAS or CLBlast for GPU acceleration.`
      4. `Select your GGUF or GGML model you downloaded earlier, and connect to the displayed URL once it finishes loading.`
    - **Linux**
      1. `On Linux, we provide a koboldcpp-linux-x64 PyInstaller prebuilt binary on the releases page for modern systems. Simply download and run the binary.`
        * Alternatively, you can also install koboldcpp to the current directory by running the following terminal command: `curl -fLo koboldcpp https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp-linux-x64 && chmod +x koboldcpp`
      2. When you can't use the precompiled binary directly, we provide an automated build script which uses conda to obtain all dependencies, and generates (from source) a ready-to-use a pyinstaller binary for linux users. Simply execute the build script with `./koboldcpp.sh dist` and run the generated binary.
  - **oobabooga - text-generation-webui** - https://github.com/oobabooga/text-generation-webui
    1. Clone or download the repository.
      * Clone: `git clone https://github.com/oobabooga/text-generation-webui`
      * Download: https://github.com/oobabooga/text-generation-webui/releases/latest -> Download the `Soruce code (zip)` file -> Extract -> Continue below.
    2. Run the `start_linux.sh`, `start_windows.bat`, `start_macos.sh`, or `start_wsl.bat` script depending on your OS.
    3. Select your GPU vendor when asked.
    4. Once the installation ends, browse to http://localhost:7860/?__theme=dark.
  - **Exvllama2**
- **Setting up a Local LLM Model**
  1. microsoft/Phi-3-mini-128k-instruct - 3.8B Model/7GB base, 4GB Q8 - https://huggingface.co/microsoft/Phi-3-mini-128k-instruct
    * GGUF Quants: https://huggingface.co/pjh64/Phi-3-mini-128K-Instruct.gguf
  2. Meta Llama3-8B - 8B Model/16GB base, 8.5GB Q8  - https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
    * GGUF Quants: https://huggingface.co/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF


----------


### <a name="pieces"></a>Pieces & What's in the original repo?
- **What's in the Repo currently?**
  1. `summarize.py` - Main script for downloading, transcribing, and summarizing videos, audio files, books and documents.
  2. `config.txt` - Config file used for settings for main app.
  3. `requirements.txt` - Packages to install for Nvidia GPUs
  4. `AMD_requirements.txt` - Packages to install for AMD GPUs
  5. `llamafile` - Llama.cpp wrapper for local LLM inference, is multi-platform and multi-LLM compatible.
  6. `media_summary.db` - SQLite DB that stores all the data ingested, transcribed, and summarized.
  7. `prompts.db` - SQLite DB that stores all the prompts.
  8. `App_Function_Libraries` Folder - Folder containing the applications function libraries
  9. `Tests` Folder - Folder containing tests for the application (ha.)
  10. `Helper_Scripts` - Folder containing helper scripts for the application
  11. `models` - Folder containing the models for the speaker diarization LLMs
  12. `tldw-original-scripts` - Original scripts from the original repo
- **What's in the original repo?**
  - `summarize.py` - download, transcribe and summarize audio
    1. First uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download audio(optionally video) from supplied URL
    2. Next, it uses [ffmpeg](https://github.com/FFmpeg/FFmpeg) to convert the resulting `.m4a` file to `.wav`
    3. Then it uses [faster_whisper](https://github.com/SYSTRAN/faster-whisper) to transcribe the `.wav` file to `.txt`
    4. After that, it uses [pyannote](https://github.com/pyannote/pyannote-audio) to perform 'diarorization'
    5. Finally, it'll send the resulting txt to an LLM endpoint of your choice for summarization of the text.
  - `chunker.py` - break text into parts and prepare each part for LLM summarization
  - `roller-*.py` - rolling summarization
    - [can-ai-code](https://github.com/the-crypt-keeper/can-ai-code) - interview executors to run LLM inference
  - `compare.py` - prepare LLM outputs for webapp
  - `compare-app.py` - summary viewer webapp

------------
### Similar/Other projects:
- https://github.com/Dicklesworthstone/bulk_transcribe_youtube_videos_from_playlist/tree/main
- https://github.com/akashe/YoutubeSummarizer
- https://github.com/fmeyer/tldw
- https://github.com/pashpashpash/vault-ai <-- Closest I've found open source to what I'm looking to build, though I'm not looking to add RAG for a while, and I'm focused on just accumulation, I figure at some point in the future can tackle chunking of hte longer form items in a manner that makes sense/is effective, but until then, data storage is cheap and text is small. And SQLite is easy to share with people. Also, no commercial aspects, this project's goal is to be able to be ran completely offline/free from outside influence.
- https://github.com/bugbakery/transcribee
- https://github.com/fedirz/faster-whisper-server
- https://github.com/transcriptionstream/transcriptionstream
- Commercial offerings:
  * Bit.ai 
  * typeset.io/
------------

### <a name="credits"></a>Credits
- [The original version of this project by @the-crypt-keeper](https://github.com/the-crypt-keeper/tldw)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://github.com/FFmpeg/FFmpeg)
- [faster_whisper](https://github.com/SYSTRAN/faster-whisper)
- [pyannote](https://github.com/pyannote/pyannote-audio)
- Thank you cognitivetech for the system prompt: https://github.com/cognitivetech/llm-long-text-summarization/tree/main?tab=readme-ov-file#one-shot-prompting
- [Fabric](https://github.com/danielmiessler/fabric)
- [Llamafile](https://github.com/Mozilla-Ocho/llamafile) - For the local LLM inference engine
- [Mikupad](https://github.com/lmg-anon/mikupad) - Because I'm not going to write a whole new frontend for non-chat writing.
- The people who have helped me get to this point, and especially for those not around to see it(DT & CC).

### 
