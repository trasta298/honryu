# 🌊 Honryu

Honryu (翻流) is a screen capture and translation tool designed for Windows. It allows users to capture a portion of their screen and instantly transcribe and translate the text within the image.

## ✨ Features

- Screen area selection for capture
- Automatic text recognition from captured images
- Translation between Japanese and English
- Real-time display of transcription and translation results

## 🖥️ Requirements

- Windows operating system
- API key for the Gemini API
- [astral-sh/uv](https://github.com/astral-sh/uv#installation)

## 🚀 Installation

1. Clone the repository:
   ```
   git clone https://github.com/trasta298/honryu.git
   cd honryu
   ```

2. Install the required dependencies:
   ```
   uv sync
   ```

3. Set up your Gemini API key and optionally specify the model:
   - Create a `.env` file in the project root directory
   - Add your API key to the file:
     ```
     GENAI_API_KEY=your_api_key_here
     ```
   - (Optional) Specify a different model by adding:
     ```
     GENAI_MODEL=gemini-1.5-pro-002
     ```

4. (Optional) Create a shortcut:
   - Right-click on `honryu.vbs` and select "Create shortcut"
   - Move the shortcut to a convenient location (e.g., desktop)
   - You can rename the shortcut for easier access

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This application currently only works on Windows.
