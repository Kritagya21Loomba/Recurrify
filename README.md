# Recurrify

A full-stack recurrence relation solver, explainer, and verifier built for algorithm students. Enter any recurrence relation and get step-by-step solutions using multiple methods, rendered in beautiful LaTeX math.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![SymPy](https://img.shields.io/badge/SymPy-Symbolic_Math-3B5526)

## Features

- **Multi-method solving** — Master Theorem, Recursion Tree, Iteration, and Characteristic Equation
- **Step-by-step derivations** — Every solution shows the full reasoning chain with LaTeX-rendered math
- **Pattern recognition** — Shows concrete expansions before introducing summation notation
- **Symbolic verification** — Substitutes closed forms back into the recurrence to prove correctness
- **Numeric verification** — Computes actual recurrence values and compares with the formula
- **Guided reasoning mode** — Interactive Q&A that walks students through the solving process
- **8 built-in examples** — Merge Sort, Binary Search, Karatsuba, Strassen, Fibonacci, and more

## Supported Recurrence Types

| Type | Example | Methods |
|------|---------|---------|
| Divide & Conquer | `T(n) = 2T(n/2) + n` | Master Theorem, Recursion Tree, Iteration |
| Non-integer division | `T(n) = 3T(2n/3) + 1` | Master Theorem, Recursion Tree, Iteration |
| Linear Homogeneous | `T(n) = T(n-1) + T(n-2)` | Characteristic Equation |
| Linear Non-homogeneous | `T(n) = 2T(n-1) + n` | Characteristic Equation, Iteration |
| Telescoping | `T(n) = T(n-1) + n` | Iteration |

## Tech Stack

### Backend
- **Python 3.11** with **FastAPI** for the API layer
- **SymPy** for symbolic mathematics (simplification, limits, LaTeX generation)
- **Pydantic** for request/response validation
- Hand-written **recursive descent parser** (tokenizer → parser → AST → extractor)

### Frontend
- **React 18** with **TypeScript** and **Vite**
- **KaTeX** for fast browser-side LaTeX rendering
- Dark theme with glassmorphism-inspired design

## Project Structure

```
Recurrify/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── requirements.txt
│   ├── recurrify/
│   │   ├── parser/
│   │   │   ├── tokenizer.py             # Regex-based lexer
│   │   │   ├── parser.py                # Recursive descent parser
│   │   │   └── extractor.py             # AST → SymPy bridge
│   │   ├── models/
│   │   │   ├── ast_nodes.py             # Frozen dataclass AST nodes
│   │   │   └── api_models.py            # Pydantic request/response schemas
│   │   ├── classifier/
│   │   │   └── classifier.py            # Recurrence type detection
│   │   ├── solvers/
│   │   │   ├── base.py                  # BaseSolver ABC + data classes
│   │   │   ├── master_theorem.py        # Master Theorem (3 cases)
│   │   │   ├── recursion_tree.py        # Recursion Tree with level-cost table
│   │   │   ├── iteration.py             # Iteration/telescoping with pattern display
│   │   │   └── characteristic.py        # Characteristic equation for linear recurrences
│   │   ├── verifier/
│   │   │   └── verifier.py              # Symbolic + numeric verification
│   │   ├── guided/
│   │   │   ├── prompts.py               # Question bank per recurrence type
│   │   │   └── session.py               # State machine for guided Q&A
│   │   └── api/
│   │       ├── routes_solve.py          # POST /solve
│   │       ├── routes_parse.py          # POST /parse
│   │       └── routes_guided.py         # POST /guided/start, /guided/{id}/answer
│   └── tests/
│       ├── test_tokenizer.py            # 4 tests
│       ├── test_parser.py               # 10 tests
│       ├── test_solvers.py              # 14 tests
│       └── test_api.py                  # 9 async integration tests
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx                      # Main app with solve/guided flow
│       ├── main.tsx                     # React entry point
│       ├── api/
│       │   └── client.ts               # Axios instance
│       ├── types/
│       │   └── models.ts               # TypeScript interfaces
│       ├── components/
│       │   ├── InputPanel.tsx           # Recurrence input + example chips
│       │   ├── SolutionDisplay.tsx      # Classification + method tabs + steps
│       │   ├── StepCard.tsx             # Timeline-style step rendering
│       │   ├── MethodSelector.tsx       # Pill-style method tabs
│       │   ├── VerificationBadge.tsx    # Expandable pass/fail verification
│       │   ├── common/
│       │   │   ├── MathBlock.tsx        # KaTeX wrapper component
│       │   │   └── ErrorAlert.tsx       # Error display with icon
│       │   └── GuidedMode/
│       │       ├── GuidedPanel.tsx      # Guided reasoning container
│       │       ├── QuestionCard.tsx     # Interactive question + feedback
│       │       └── ProgressTracker.tsx  # Progress bar
│       └── styles/
│           └── index.css               # Complete dark theme stylesheet
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs on `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173`.

### Run Tests

```bash
cd backend
pytest tests/ -v
```

All 37 tests should pass.

## API Endpoints

### `POST /solve`

Solve a recurrence relation with all applicable methods.

**Request:**
```json
{
  "input": "T(n) = 2T(n/2) + n",
  "base_cases": { "1": 1 }
}
```

**Response:**
```json
{
  "input": "T(n) = 2T(n/2) + n",
  "classification": {
    "recurrence_type": "divide_and_conquer",
    "applicable_methods": ["Master Theorem", "Recursion Tree", "Iteration"],
    "preferred_method": "Master Theorem",
    "reasoning": "Divide-and-conquer form with a=2, b=2, f(n)=n."
  },
  "solutions": [
    {
      "method": "Master Theorem",
      "applicable": true,
      "steps": [ ... ],
      "closed_form": "T(n) = \\Theta(n \\log n)",
      "verification": {
        "passed": true,
        "symbolic_check": "...",
        "numeric_checks": [
          { "n": 1, "recurrence_value": 1, "formula_value": 1 }
        ]
      }
    }
  ]
}
```

### `POST /parse`

Parse and classify a recurrence without solving.

**Request:**
```json
{ "input": "T(n) = T(n-1) + T(n-2)" }
```

### `POST /guided/start`

Start a guided reasoning session.

**Request:**
```json
{ "input": "T(n) = 2T(n/2) + n" }
```

### `POST /guided/{session_id}/answer`

Submit an answer to the current guided question.

**Request:**
```json
{ "answer": "2" }
```

## How It Works

### Parser Pipeline

```
"T(n) = 2T(n/2) + n"
        │
        ▼
   ┌──────────┐
   │ Tokenizer │  →  [IDENT:T, LPAREN, IDENT:n, RPAREN, EQUALS, NUM:2, ...]
   └──────────┘
        │
        ▼
   ┌────────┐
   │ Parser │  →  Recurrence(func_name="T", var_name="n", rhs=BinOp(...))
   └────────┘
        │
        ▼
   ┌───────────┐
   │ Extractor │  →  RecurrenceInfo(a=2, b=2, f(n)=n, type=DIVIDE_AND_CONQUER)
   └───────────┘
```

### Solver Pipeline

```
RecurrenceInfo
     │
     ├── Classifier → [Master Theorem, Recursion Tree, Iteration]
     │
     ├── MasterTheoremSolver.solve() → steps + closed form
     ├── RecursionTreeSolver.solve() → steps + closed form
     └── IterationSolver.solve()     → steps + closed form
                                           │
                                           ▼
                                      Verifier.verify()
                                      ├── symbolic substitution
                                      └── numeric evaluation
```

## Deployment

### Frontend → Cloudflare Pages

1. Connect your GitHub repo to [Cloudflare Pages](https://pages.cloudflare.com)
2. Set build configuration:
   - **Build command:** `cd frontend && npm install && npm run build`
   - **Build output directory:** `frontend/dist`
3. Add environment variable:
   - `VITE_API_URL` = your backend URL (e.g. `https://recurrify-api.up.railway.app`)

### Backend → Railway / Render

**Railway:**
1. Connect GitHub repo at [railway.app](https://railway.app)
2. Set root directory to `backend`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add CORS origin for your Cloudflare Pages domain

**Render:**
1. Create a new Web Service at [render.com](https://render.com)
2. Set root directory to `backend`, start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

After deploying the backend, update `frontend/src/api/client.ts` to use the deployed URL (or use `VITE_API_URL` env var).

## License

MIT
