# OCD-Organizer

OCD-Organizer is a powerful desktop application that uses artificial intelligence to help you organize your files efficiently. It analyzes your directory structure and suggests optimal organization strategies based on file types, naming conventions, and content.

## Features

- Analyze directory structures
- Generate AI-powered organization suggestions
- Preview and apply file reorganization
- Undo recent reorganizations
- Plugin system for extensibility
- Multiple AI backend options (OpenAI, HuggingFace, Local, Perplexity, Bing)
- User-friendly GUI built with PyQt5

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/michael-rapoport/OCD-Organizer.git
   cd OCD-Organizer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the `config.json.example` file to `config.json`:
   ```
   cp config.json.example config.json
   ```

2. Edit `config.json` and add your API keys for the AI services you plan to use.

## Usage

To run OCD-Organizer execute the following command:

```
python main.py
```

The application will open, and you can use the GUI to select directories, analyze them, and reorganize your files.

## Adding Plugins

To add a new plugin:

1. Create a new Python file in the `plugins` directory.
2. Implement the `register_plugin()` function that returns a dictionary with plugin information.
3. Implement the main functionality of your plugin.

See the `plugins/file_stats.py` for an example.

## Contributing

Contributions are welcome! You can send crypto to :
BTC 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
