# Udaan

Production-ready MVP monorepo for an online Arts teaching platform.

## Structure
- `backend`: FastAPI + SQLAlchemy + Alembic + ReportLab
- `frontend`: Next.js App Router + TypeScript + Tailwind

## Quick Start
```bash
docker compose up --build
```

Apps:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

## Default Seeded Admin
Loaded from backend env values:
- Email: `admin@udaan.local`
- Password: `Admin@123`

Change these in `backend/.env.example` or by runtime env override.

## Local Dev Without Docker
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## API Coverage
Implemented routes include:
- Auth: `/auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password`
- Profile: `/me`
- Admin: courses/lectures CRUD, upload, students, student progress, enrollments, certificates, certificate settings
- Student: browse courses, enroll, course detail, lecture play/progress/complete, progress, certificates, certificate download
- AI: `/ai/transform`, `/ai/history`

## Certificates
- Generated with ReportLab on course completion.
- Completion occurs when all lectures in a course are marked completed for that student.
- Certificate template settings:
  - Teacher name
  - Optional signature image
- Settings managed at `/admin/settings`.

## AI Reference Image Transformation
Current MVP implementation uses a local image pipeline (`Pillow`) with presets:
- pencil sketch outline
- charcoal shading
- watercolor wash reference
- simplified shapes (block-in)
- value map (3-5 tonal values)

### Swapping to OpenAI Image API
Replace internals of `backend/app/services/ai_service.py` with an adapter that:
1. Uploads/reads source image
2. Calls OpenAI image edit/generation endpoint
3. Saves output to storage provider
4. Returns saved output path

No route changes required because `/ai/transform` already isolates the interface.

## Video Delivery + Signed Access
- Lecture playback API returns signed, expiring URL.
- Media stream endpoint validates token, expiry, and enrollment.
- Compatible with HLS if the URL points to `.m3u8`; frontend uses `hls.js` automatically.
- HLS packaging script example: `backend/scripts/hls_pack_example.sh`.

## Content Protection Reality Check
Web video cannot be made fully record-proof.

Practical best-effort controls in this MVP:
- Signed expiring video URLs
- Token-validated stream access
- Watermark overlay with learner identity + timestamp
- Basic friction controls (disable right click, devtools key deterrence)
- Pause on tab hidden (visibility change)

Limits you must assume:
- Browser/web cannot guarantee blocking all screen recording
- Determined users can capture via external devices or low-level methods

For stronger protection in production, combine:
- DRM-enabled streaming (where available)
- Dynamic forensic watermarking
- Monitoring, takedown, legal/policy enforcement

## Tests
Backend tests:
```bash
cd backend
pytest -q
```

Includes basic auth and course listing coverage.
