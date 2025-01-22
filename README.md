# Heart Plaque Detection API

A Flask-based REST API for detecting and analyzing heart plaque in medical images using computer vision techniques.

## Overview

This API provides endpoints for processing medical images to detect and analyze heart plaque, helping medical professionals in their diagnostic process. The system uses OpenCV and NumPy for image processing and analysis.

## Features

- Image upload and processing
- Heart plaque detection
- Analysis results in JSON format
- Secure file handling
- Environment-based configuration

## Prerequisites

- Python 3.x
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/git-dariel/heart-plaque-detection-api.git
cd heart-plaque-detection-api
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory and add necessary configurations.

## Usage

1. Start the server:

```bash
python run.py
```

2. The API will be available at `http://[local_server_ip_address]:5000`

## API Documentation

The API documentation is available via Swagger. Once the application is running, you can access the Swagger UI at:
`http://[local_server_ip_address]:5000/apidocs`

## Project Structure

```
heart-plaque-detection-api/
├── app/
│   ├── utils/
│   │   └── image_utils.py
│   └── ...
├── .env
├── requirements.txt
└── run.py
```

## API Endpoints

Documentation for API endpoints will be available at the server root when running in debug mode.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contact & Social Media

- LinkedIn: [https://www.linkedin.com/in/darielavila/]
- GitHub: [git-dariel](https://github.com/git-dariel)
- Facebook: [Dariel Avila][https://www.facebook.com/dariel.avila.129]

Feel free to reach out for questions, suggestions, or collaborations!
