# python3_localai_cli

**Working: enough for me**

Basic LocalAI CLI, written in Python3.

*Please Note:*

This project was created for specific personal tasks. It will only be adjusted to the environment that I am using this in.

Note: It is assumed that you have the corresponding backend built for the functionality you want to use.
- For example, if you want to use Text-to-Audio, you should have Bark or Coqui configured.

## What's supported:
- Audio-to-Text     (Tested with Whisper backend)
- Image-to-Image    (Tested with [asyncdiff_localai](https://github.com/SlackinJack/asyncdiff_localai) backend)
- Image-to-Text     (Tested with Diffusers backend)
- Image-to-Video    (Tested with [asyncdiff_localai](https://github.com/SlackinJack/asyncdiff_localai) backend)
- Text-to-Audio     (Tested with Coqui backend)
- Text-to-Image     (Tested with Diffusers, [distrifuser_localai](https://github.com/SlackinJack/distrifuser_localai), [asyncdiff_localai](https://github.com/SlackinJack/asyncdiff_localai) backends)
- Text-to-Text      (Tested with llama.cpp, Transformers backends)

## Other features:
- Paste in weblinks to prompt and use it as a source (Format: https://example.com)
- Get transcripts from YouTube videos, and use it as a source (Format: https://www.youtube.com/watch?v=...)
- Read PDFs, DOCX, PPTX, XLSX, or other files (as raw text), and use it as a source (Format: '/path/to/file')
- Get audio from audio/video files, and use it as a source (Format: '/path/to/file')
- Get descriptions of images, and use it as a source (Format: '/path/to/file')
- Use an entire folder, and read each file recursively as sources (Format: '/path/to/folder')
- Search DuckDuckGo, based on generated search terms from your prompt, then answer your prompt based on what it found
- Automatically switch models, using your description of each model
- Text-streaming for outputs
- Reply to conversations, load previous conversations and continue them
- Send cURL commands
- Adjustable system prompt
- Read aloud outputs
- Microphone to input a prompt
- Continuous Audio-to-Text transcriptions

## Test environment:
- Ubuntu Server 22.04
- 4x Nvidia Tesla T4 16GB, Cuda 12.8
- 2x Xeon E5-2660 v3
- Python 3.10.12
- LocalAI 2.26.0

