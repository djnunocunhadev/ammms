# Advanced Music Metadata Management System (AMMMS)

A comprehensive macOS application for music metadata management and analysis, featuring advanced audio processing capabilities and an intuitive interface inspired by Sononym.

## Features

- 🎵 Advanced audio analysis and feature extraction
- 🏷️ Comprehensive metadata management from multiple sources
- 🔍 Intelligent similarity search
- 📊 High-resolution waveform visualization
- 🎨 Modern, responsive interface
- 🔄 Real-time processing updates
- 🎛️ Advanced filtering and organization tools

## Tech Stack

### Backend
- FastAPI for RESTful API
- SQLAlchemy ORM
- PostgreSQL/SQLite database
- Redis for caching
- Celery for task processing
- Librosa for audio analysis
- PyAcoustID for fingerprinting
- TensorFlow/PyTorch for audio classification

### Frontend
- Electron.js
- Vue.js
- Tailwind CSS
- Web Audio API

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+ (optional, SQLite available for simplified deployment)
- Redis 6+

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/djnunocunhadev/ammms.git
cd ammms
```

2. Set up the Python virtual environment:
```bash
./scripts/setup_venv.sh venv
source venv/bin/activate
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start development servers:
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Building for Production

```bash
./scripts/build_macos.sh
```

The built application will be available in the `dist` directory.

## API Documentation

Once the backend server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [Sononym](https://www.sononym.net)
- Uses various open-source audio processing libraries
- Community contributions welcome!