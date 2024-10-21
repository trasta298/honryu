# Honryu

Honryu (翻流) is an open-source screen capture and translation tool designed for Windows. It allows users to capture a portion of their screen and instantly transcribe and translate the text within the image.

## Features

- Screen area selection for capture
- Automatic text recognition from captured images
- Translation between Japanese and English
- Real-time display of transcription and translation results

## Requirements

- Windows operating system
- Python 3.10 or higher
- API key for the Gemini API

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/honryu.git
   cd honryu
   ```

2. Install the required dependencies:
   ```
   uv sync
   ```

3. Set up your Gemini API key:
   - Create a `.env` file in the project root directory
   - Add your API key to the file:
     ```
     GENAI_API_KEY=your_api_key_here
     ```

4. Configure the VBS script:
   - Open `honryu.vbs` in a text editor
   - Modify the following line to point to your Python interpreter:
     ```vbs
     WshShell.Run "C:\Path\To\Your\Python\python.exe main.py", 0, False
     ```
   - Replace `C:\Path\To\Your\Python\python.exe` with the actual path to your Python executable
   - Save the changes

5. (Optional) Create a shortcut:
   - Right-click on `honryu.vbs` and select "Create shortcut"
   - Move the shortcut to a convenient location (e.g., desktop)
   - You can rename the shortcut for easier access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This application currently only works on Windows.

