# CrimeJournal - AI-Powered Legal Case Research Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-green.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)

**CrimeJournal** is a zero-cost, AI-powered legal case research platform built for independent lawyers and small law firms. It provides instant access to millions of legal cases with AI-generated summaries, entity extraction, and similarity search - at 1/10th the cost of traditional services like Westlaw.

## Key Features

- **Smart Search** - Natural language search across millions of legal cases from CourtListener
- **AI Summaries** - MiniMax-powered case summarization for quick understanding
- **Entity Extraction** - Automatically extract parties, dates, statutes, and legal terms
- **Similar Cases** - AI-powered similarity search to find related precedents
- **Search History** - Track and revisit your research
- **Favorites** - Save important cases for quick access
- **Responsive Design** - Works on desktop and mobile

## Architecture

```
+---------+     +---------+     +--------+
| Browser|---->| Vercel  |---->| Render |
| React  |     |Frontend |     | FastAPI|
+---------+     +---------+     +----+---+
                                   |
                    +--------------+---------------+
                    |              |               |
                    v              v               v
              +----------+  +-------------+  +-----------+
              | MiniMax  |  |CourtListener|  | PostgreSQL|
              |   API    |  |    API     |  | (Supabase)|
              +----------+  +-------------+  +-----------+
```

## Tech Stack

### Backend
- **Python 3.11+** - FastAPI, SQLAlchemy, Pydantic
- **AI Services** - MiniMax (unified AI service)
- **Database** - PostgreSQL (Supabase) + SQLite (local)
- **Cache** - Redis (Upstash)
- **Embeddings** - Sentence-Transformers (local, free)

### Frontend
- **React 18** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **React Router** - Navigation

### Deployment
- **Frontend** - Vercel (free)
- **Backend** - Render (free tier)
- **Database** - Supabase PostgreSQL (500MB free)
- **CI/CD** - GitHub Actions (auto-deploy)

## Quick Start

### Prerequisites

1. **Accounts Required** (all free):
   - [GitHub](https://github.com) - Code hosting
   - [Vercel](https://vercel.com) - Frontend deployment
   - [Render](https://render.com) - Backend deployment
   - [Supabase](https://supabase.com) - Database
   - [CourtListener](https://www.courtlistener.com) - Legal data
   - [MiniMax](https://platform.minimax.chat) - AI API

2. **Local Environment**:
   - Python 3.11+
   - Node.js 18+
   - Git

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/your-username/CrimeJournal.git
cd CrimeJournal

# 2. Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit .env with your API keys
uvicorn app.main:app --reload --port 8000

# 3. Setup Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `backend/.env` with:

```env
# MiniMax (for summaries, entities, keywords)
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-02

# CourtListener (free legal data)
COURTLISTENER_API_TOKEN=your_token

# Database
DATABASE_URL=sqlite:///./crimejournal.db

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Embedding Model (local, free)
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get token |
| GET | `/api/auth/me` | Get current user |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search` | Search cases |
| GET | `/api/cases/{id}` | Get case details |
| POST | `/api/cases/{id}/summarize` | AI summary |
| POST | `/api/cases/{id}/entities` | Extract entities |
| POST | `/api/cases/{id}/keywords` | Extract keywords |
| GET | `/api/cases/{id}/similar` | Find similar cases |

### History & Favorites
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/history` | Get search history |
| DELETE | `/api/history/{id}` | Delete history item |
| GET | `/api/favorites` | Get favorites |
| POST | `/api/favorites` | Add to favorites |
| DELETE | `/api/favorites/{id}` | Remove from favorites |

## Deployment

### Automated Deployment (Recommended)

1. Push code to GitHub
2. Connect repo to Vercel (frontend) and Render (backend)
3. Add secrets to GitHub Actions:
   - `RENDER_API_KEY`
   - `VERCEL_TOKEN`
   - `MINIMAX_API_KEY`
   - `COURTLISTENER_API_TOKEN`
4. GitHub Actions will auto-deploy on push

### Manual Deployment

**Backend (Render)**:
```bash
# Create render.yaml or deploy via dashboard
render deploy
```

**Frontend (Vercel)**:
```bash
cd frontend
vercel --prod
```

## Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| Free | $0/mo | 10 searches/day, basic info |
| Pro | $50/mo | Unlimited, AI summaries, similarity |
| Enterprise | $500/mo | Pro + API access, team accounts |

## Project Structure

```
CrimeJournal/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   │   ├── ai/       # MiniMax AI service
│   │   │   ├── courtlistener.py
│   │   │   └── cache.py
│   │   ├── utils/        # Utilities
│   │   ├── main.py       # FastAPI app
│   │   └── config.py     # Configuration
│   ├── tests/            # Test files
│   ├── migrations/       # DB migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── lib/          # Utilities
│   │   ├── App.tsx       # Main app
│   │   └── main.tsx      # Entry point
│   ├── package.json
│   └── vite.config.ts
├── .github/workflows/     # CI/CD
├── render.yaml           # Backend deployment
├── vercel.json           # Frontend deployment
└── README.md
```

## Running Tests

```bash
cd backend
pytest --cov=app --cov-report=html
```

## Cost Analysis

| Service | Monthly Cost |
|---------|-------------|
| Vercel (Frontend) | $0 |
| Render (Backend) | $0 |
| Supabase (Database) | $0 |
| MiniMax API | ~$3-8 |
| **Total** | **$3-8/mo** |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [CourtListener](https://www.courtlistener.com) - Free legal case data
- [MiniMax](https://platform.minimax.chat) - AI capabilities
- [Supabase](https://supabase.com) - Database infrastructure
- [Vercel](https://vercel.com) - Frontend hosting
- [Render](https://render.com) - Backend hosting
