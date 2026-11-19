# Contributing Guidelines

Thank you for your interest in contributing to this project!

## How to Contribute

1. **Fork the Repository**: Create your own fork of this project on GitHub.
2. **Clone Locally**: Clone your fork to your local machine:
   ```bash
   git clone https://github.com/<your-username>/youtube-downloader.git
   cd youtube-downloader
   ```
3. **Create a Branch**: Create a feature branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set Up Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Make Changes**: Implement your improvements or bug fixes.
6. **Test**: Run `python app.py` and verify all options function correctly.
7. **Commit & Push**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**: Submit your pull request on GitHub with a clear summary of what was changed and why.

## Reporting Issues

If you encounter bugs or have feature suggestions, please open an Issue with:
- Operating system version
- Steps to reproduce
- Error trace or terminal output (if applicable)
