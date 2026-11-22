# Marketplace

A full-stack e-commerce marketplace platform connecting buyers, sellers, and administrators. Built with a React single-page frontend and a Django REST Framework backend powered by serverless PostgreSQL (Neon), Clerk authentication, Cloudflare R2 storage, and Resend email.

---

## Features

### 🛍️ Buyers

- **Product Discovery**: Fast catalog search with full-text search, multi-attribute filtering (category, brand, price, rating), and pagination.
- **Cart & Checkout**: Cart management with server-side pricing and stock verification, tax and shipping calculation, and bulk discount support.
- **Order Tracking**: Order status tracking and confirmation emails.
- **Social & Support**: Direct buyer-seller chat messaging and product reviews with verified purchase flags.

### 🏪 Sellers

- **Store Management**: Custom store profile, branding (logo and banner), and verified seller badges.
- **Inventory & Catalog**: Product lifecycle management, low-stock threshold alerts, and batch import/export via CSV.
- **Analytics Dashboard**: Revenue, total distinct order counts, sales velocity, customer breakdown, and inventory forecasting.
- **Order Processing**: Order status transitions (processing, shipped, delivered).

### ⚙️ Administrators

- **Platform Analytics**: Aggregate counts, active stores, order volumes, and platform commission metrics.
- **User Management**: Search, filter by role (customer, seller, admin), and account administration.
- **Store & Product Oversight**: Store verification, activation/suspension, and catalog moderation.
- **Platform Settings**: Configurable tax rates, shipping fees, and per-order transaction fees.

---

## Tech Stack

| Domain                    | Technology                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Frontend**              | React 19, React Router v7, Context API, CSS Variables, Cloudflare Pages                                      |
| **Backend**               | Django 5, Django REST Framework, Python 3.10+, Gunicorn                                                       |
| **Database**              | PostgreSQL on [Neon](https://neon.tech) via `psycopg2-binary` connection pool with SSL enforcement            |
| **Authentication**        | [Clerk](https://clerk.com) — Session tokens, email verification, social SSO, MFA                             |
| **Media Storage**         | [Cloudflare R2](https://www.cloudflare.com/developer-platform/r2/) via Boto3 (presigned direct uploads)       |
| **Transactional Email**   | [Resend](https://resend.com)                                                                                  |
| **Validation & Security** | DRF Serializers, CORS headers, Parameterized SQL queries, Role-based permissions                             |
| **Testing & Linting**     | Django test suite, React Testing Library, ESLint, Prettier                                                   |

---

## Project Structure

```text
Marketplace/
├── backend/
│   ├── api/                # Django application (models, serializers, views, permissions, authentication)
│   ├── marketplace/        # Django project configuration (settings.py, urls.py, wsgi.py)
│   ├── migrations/         # PostgreSQL schema definition (0001_init.sql)
│   ├── check_api.py        # API verification test script
│   ├── manage.py           # Django CLI management utility
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Backend environment configuration
├── frontend/
│   ├── public/             # Static assets, Cloudflare Pages _headers and _redirects
│   └── src/
│       ├── components/     # Reusable UI components (Navbar, ChatBox, Common, Admin)
│       ├── context/        # React contexts (AuthContext, CartContext)
│       ├── hooks/          # Custom React hooks (useDocumentTitle)
│       ├── pages/          # Route views (Home, Products, Seller, Admin, Customer, Auth)
│       └── services/       # Axios API client configured with Clerk token provider
├── package.json            # Workspace root scripts
└── render.yaml             # Render deployment blueprint
```

---

## Getting Started

### Prerequisites

- **Python** >= 3.10 and **pip**
- **Node.js** >= 18.x and **npm** >= 9.x
- A **PostgreSQL** database (e.g., [Neon Serverless Postgres](https://neon.tech))
- A **Clerk** application account ([dashboard.clerk.com](https://dashboard.clerk.com))
- _(Optional)_ Cloudflare R2 bucket for uploads and Resend API key for emails

### 1. Installation

Install dependencies across root, backend, and frontend:

```bash
npm run install-all
```

### 2. Environment Configuration

#### Backend (`backend/.env`)

Create `backend/.env` with your credentials (see `backend/.env.example` for reference):

```env
DJANGO_SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-sample.us-east-2.aws.neon.tech/neondb?sslmode=require

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_...

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: Cloudflare R2 for Image Uploads
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=marketplace
R2_PUBLIC_URL=https://pub-<hash>.r2.dev

# Optional: Resend for Transactional Email
RESEND_API_KEY=re_...
RESEND_FROM=Marketplace <onboarding@resend.dev>
```

#### Frontend (`frontend/.env.local`)

Create `frontend/.env.local` (see `frontend/.env.example` for reference):

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_...
```

### 3. Run Development Servers

Start both backend and frontend concurrently:

```bash
npm run dev
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:5000/api](http://localhost:5000/api)

---

## Available Scripts

| Command                 | Action                                                    |
| ----------------------- | --------------------------------------------------------- |
| `npm run dev`           | Run backend and frontend concurrently in development mode |
| `npm run server`        | Start Django backend development server on port 5000      |
| `npm run client`        | Start React frontend development server                   |
| `npm run build`         | Build frontend production bundle and prepare backend      |
| `npm test`              | Run tests across backend and frontend                     |
| `npm run test:backend`  | Run Django API integration checks                         |
| `npm run test:frontend` | Run frontend React Testing Library tests                  |
| `npm run lint`          | Run ESLint on frontend                                    |
| `npm run lint:fix`      | Automatically fix ESLint warnings and errors              |
| `npm run deploy:pages`  | Build and deploy frontend to Cloudflare Pages             |

---

## Production & Security Hardening

- **Django ORM & Parameterized Queries**: All database queries are executed via Django ORM using parameterized SQL to eliminate SQL injection risks.
- **Role-Based Access Control**: View-level permissions (`IsAuthenticated`, `IsAdmin`, `IsSeller`, `IsCustomer`) validate identity and roles.
- **Session Security**: Authentication is verified by Clerk via bearer session tokens decoded and validated with Clerk API.
- **Direct-to-R2 Uploads**: Media files can upload directly from client browsers to Cloudflare R2 using short-lived presigned PUT URLs via Boto3.
- **Unified Response Contract**: Custom exception handler ensures consistent `{ success: false, message, code }` payloads across all endpoints.

---

## License

Licensed under the [MIT License](./package.json).
