# Khmer-English Transliteration 🌏📝

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-orange.svg)](https://www.tensorflow.org/)
[![GitHub stars](https://img.shields.io/github/stars/RozaVong/Khmer-Transliteration?style=social)](https://github.com/RozaVong/Khmer-Transliteration)
[![GitHub issues](https://img.shields.io/github/issues/RozaVong/Khmer-Transliteration)](https://github.com/RozaVong/Khmer-Transliteration/issues)

> A cutting-edge machine learning-powered application for converting English words into Khmer script, making Khmer language learning accessible and fun! This project bridges the gap between Romanized English and authentic Khmer characters, supporting both transliteration and Romanized display for educational purposes.

## 📋 Table of Contents

- [✨ Features](#-features)
- [📸 Screenshots](#-screenshots)
- [📖 Example](#-example)
- [🛠️ Installation](#️-installation)
- [ Usage](#-usage)
- [👥 Team](#-team)


## ✨ Features

- 🚀 **Fast Transliteration**: Convert English inputs to Khmer script in real-time with sub-second response times
- 🤖 **AI-Powered**: Utilizes advanced machine learning models (Keras/TensorFlow) for accurate predictions
- 🌐 **Web Interface**: Sleek, responsive frontend built with vanilla HTML/CSS/JS
- 🔄 **Bidirectional Support**: Handles Romanized Khmer for better understanding and learning
- 📊 **Logging & Monitoring**: Comprehensive logging for predictions, errors, and system health
- 🐳 **Containerized**: Fully Dockerized with Docker Compose for easy deployment
- 🧪 **Tested**: Includes comprehensive unit tests and integration tests
- 🔒 **Secure**: Implements authentication and security best practices
- 📈 **Scalable**: Built with FastAPI for high-performance async operations
- 🎯 **User Feedback**: Integrated feedback system for continuous improvement

## 📸 Screenshots

### Deployment Interface 
![Deployment Screenshot 1](https://github.com/RozaVong/Khmer-Transliteration/blob/main/photo_2026-01-23_15-57-12.jpg)

![Deployment Screenshot 2](https://github.com/RozaVong/Khmer-Transliteration/blob/main/photo_2026-01-23_15-57-21.jpg)

*Experience the seamless transliteration process through our intuitive web interface.*

### Tech Stack

- **Backend**: FastAPI, Python 3.8+, Uvicorn
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **ML**: TensorFlow/Keras, Scikit-learn
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker, Docker Compose, Nginx
- **Testing**: Pytest, Unittest
- **Monitoring**: Custom logging, health checks

## 🤖 Model Details

Our transliteration model is a sequence-to-sequence (Seq2Seq) neural network designed specifically for English-to-Khmer character-level transliteration. The model uses an encoder-decoder architecture to handle the complex mapping between English phonetics and Khmer script.

### How the Model Works

1. **Input Processing**: English text is tokenized into character sequences
2. **Encoding**: The encoder processes the input sequence and creates a context vector
3. **Decoding**: Character by character, the decoder generates Khmer script output
4. **Post-processing**: The output is detokenized back to readable Khmer text

### Model Architecture

- **Framework**: TensorFlow/Keras
- **Input**: English text (character-level tokenization)
- **Output**: Khmer script (character-level tokenization)
- **Model Formats**:
  - `.keras`: Main model file (Keras HDF5 format)
  - `.pkl`: Serialized tokenizers and metadata (English tokenizer, Khmer tokenizer, max lengths)

### Components

#### Encoder
- **LSTM**: Processes input sequence to create context representations
- **Embedding Layer**: Converts character indices to dense vectors
- **Purpose**: Creates rich representations of English input sequences

#### Decoder
- **Dense Output Layer**: Predicts next Khmer character probabilities

#### Tokenizers
- **English Tokenizer**: Maps English characters to integer indices
- **Khmer Tokenizer**: Maps Khmer characters to integer indices
- **Special Tokens**: Handles padding (`<pad>`), start-of-sequence (`<sos>`), end-of-sequence (`<eos>`)

### Key Hyperparameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Encoder Layers | 2 | LSTM layers |
| Decoder Layers | 2 | LSTM layers |
| Units per Layer | 512 | Hidden units in LSTM cells |
| Embedding Dimension | 256 | Character embedding size |
| Vocabulary Size (English) | 28 | Unique English character combinations |
| Vocabulary Size (Khmer) | 81 | Unique Khmer character combinations |
| Max Sequence Length | 50 | Maximum input/output character length |
| Dropout Rate | 0.2 | Applied to LSTM layers for regularization |

### Model Files Structure

```
model/
├── khmer_Glish.keras    # Main Keras model (weights & architecture)
└── khmer_Glish.pkl      # Pickle file containing:
    ├── eng_tokenizer    # English character tokenizer
    ├── khm_tokenizer    # Khmer character tokenizer
    ├── max_eng_len      # Maximum English sequence length
    └── max_khm_len      # Maximum Khmer sequence length
```

### Inference Process

During prediction:
1. Input text is preprocessed and tokenized using the English tokenizer
2. Sequences are padded to `max_eng_len`
3. The encoder processes the input to create context vectors
4. The decoder generates output character-by-character using greedy decoding
5. Generation stops when `<eos>` token is predicted or max length is reached
6. Output is detokenized back to Khmer text

This architecture enables accurate transliteration while handling variable-length inputs and maintaining contextual relationships between characters.

## 📁 Project Structure

```
khmer-transliteration/
├── .env                          # Environment variables
├── docker-compose.yml            # Docker services configuration
├── main.py                       # Application entry point
├── nginx.conf                    # Nginx configuration for backend
├── nginx-frontend.conf           # Nginx configuration for frontend
├── requirements.txt              # Python dependencies
├── run.bat                       # Windows batch script for running
├── setup_database.py             # Database initialization script
├── setup.sh                      # Setup script for Linux/Mac
├── test_fix.py                   # Test fixes script
├── .pytest_cache/                # Pytest cache directory
├── .venv/                        # Virtual environment
├── backend/                      # Backend application
│   ├── Dockerfile                # Backend Docker configuration
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       ├── endpoints.py      # API endpoints
│   │       └── routes.py         # API routes
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration settings
│   │   └── security.py           # Security utilities
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py         # Database connection
│   │   ├── migrations.py         # Database migrations
│   │   └── migrations/           # Migration files
│   │       └── 001_initial_schema.sql
│   ├── logs/                     # Application logs
│   │   ├── .gitignore
│   │   ├── access.log
│   │   ├── app.log
│   │   ├── error.log
│   │   └── predictions.log
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── feedback.py           # Feedback model
│   │   └── prediction.py         # Prediction model
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── monitoring.py         # Monitoring service
│   │   └── translation.py        # Translation service
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── data_preprocessing.py # Data preprocessing utilities
│       ├── helpers.py            # Helper functions
│       └── model_loader.py       # Model loading utilities
├── frontend/                     # Frontend application
│   ├── Dockerfile                # Frontend Docker configuration
│   ├── index.html                # Main HTML page
│   ├── script.js                 # Frontend JavaScript
│   ├── style.css                 # Frontend styles
│   └── assets/                   # Static assets
│       └── README.md
├── model/                        # Machine learning models
│   ├── khmer_Glish.keras         # Keras model file
│   └── khmer_Glish.pkl           # Tokenizers and metadata
└── tests/                        # Test suite
    ├── __init__.py
    ├── test_api.py               # API tests
    ├── test_database.py          # Database tests
    └── test_model.py             # Model tests
```

## 📖 Example

```python
# English input
"brodae"

# Predicted Khmer output
"ប្រដែ"

# Optional Romanized display
"brodae" → "ប្រដែ"
```

## 🛠️ Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.8+ (for local development)
- Git
- 4GB+ RAM recommended

### Quick Start with Docker 🚀
1. **Clone the repository**:
   ```bash
   git clone https://github.com/RozaVong/Khmer-Transliteration.git
   cd Khmer-Transliteration
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Start the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the app**:
   Open your browser to `http://localhost:8080`

### Local Development 🧑‍💻
1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   ```bash
   python setup_database.py
   ```

4. **Load the ML model**:
   ```bash
   python -c "from backend.utils.model_loader import load_model; load_model()"
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## 🚀 Usage

### API Endpoints
- `POST /api/v1/transliterate`: Transliterate English text to Khmer
  - Body: `{"text": "hello"}`
  - Response: `{"khmer": "ហេឡូ", "romanized": "hello"}`
- `GET /api/v1/health`: Check system health
- `POST /api/v1/feedback`: Submit user feedback

### Frontend
Access the web interface at `http://localhost:8080` to:
- Input English words or phrases
- View instant Khmer transliterations
- Toggle between Khmer script and Romanized display
- Submit feedback for model improvement

### CLI Usage
```bash
# Run tests
pytest tests/

# Run with custom config
python main.py --config config.yaml

# Database migrations
python backend/database/migrations.py
```

## 👥 Team 4

We are a diverse team of passionate developers working on this innovative project!

| Avatar | Role | Name | GitHub | Specialty |
|--------|------|------|--------|-----------|
| 👨‍💻 | Backend Developer | Vey Sreypich | [Sreypich999](https://github.com/sreypich999) | API development, database management, security |
| 🎨 | Frontend Developer |Vang Roza | [RozaVong](https://github.com/RozaVong) | UI/UX design, JavaScript development, responsive design |
| 🤖 | ML Engineer |Vanna Juuka | [vannajuuka](https://github.com/vannajuuka) | Model training, data preprocessing, algorithm optimization |
| 🐳 | DevOps Engineer | Sek Somunineath | [MunineathSek](https://github.com/MunineathSek) | Docker, CI/CD, infrastructure, monitoring |
| 🧪 | QA Engineer |Veng MengSoklin | [mengsoklin](https://github.com/mengsoklin) | Testing, quality assurance, automation |
| 📚 | Documentation Specialist |Ton chamnan | [Tnannz](https://github.com/Tnannz) | Technical writing, project documentation, user guides |

