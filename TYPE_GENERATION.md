# Type Generation Workflow

This project uses an automated type generation system to maintain type consistency between the Python backend and TypeScript frontend.

## Overview

**Single Source of Truth**: Python Pydantic models → JSON Schema → TypeScript types

```
backend/models/core/  →  shared/schemas/  →  shared/generated-types/
    (Pydantic)           (JSON Schema)         (TypeScript)
```

## Quick Start

### Generate All Types
```bash
cd frontend
npm run generate:all
```

### Generate Only Schemas (from Python)
```bash
cd frontend
npm run generate:schemas
```

### Generate Only TypeScript (from schemas)
```bash
cd frontend  
npm run generate:types
```

## Directory Structure

```
shared/
├── schemas/                    # Generated JSON schemas
│   ├── CustomUser.json
│   ├── GameState.json
│   ├── index.json
│   └── ...
├── generated-types/           # Generated TypeScript types
│   ├── CustomUser.ts
│   ├── GameState.ts
│   ├── index.ts
│   └── ...
└── types/                     # Manual types (legacy - to be removed)
    └── core/
        ├── User.ts
        ├── Game.ts
        └── ...

backend/
├── models/
│   └── core/                  # Centralized Pydantic models
│       ├── user.py           # User, Player, Profile models
│       ├── game.py           # Game state, matchmaking models
│       ├── question.py       # Question, test case models
│       ├── socket.py         # Socket event models
│       ├── api.py            # API request/response models
│       └── __init__.py       # Exports all models
└── scripts/
    └── export_schemas.py     # JSON schema export script

frontend/
└── scripts/
    └── generate-types.js     # TypeScript generation script
```

## How It Works

### 1. Backend Models (Source of Truth)
Python Pydantic models defined in `backend/models/core/`:

```python
# backend/models/core/user.py
class CustomUser(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
```

### 2. JSON Schema Export
The `export_schemas.py` script uses Pydantic's built-in `model_json_schema()`:

```bash
cd backend
python scripts/export_schemas.py
```

### 3. TypeScript Generation
The `generate-types.js` script uses `json-schema-to-typescript`:

```bash
cd frontend
node scripts/generate-types.js
```

### 4. Generated TypeScript
```typescript
// shared/generated-types/CustomUser.ts
export interface CustomUser {
  id: string;
  name?: string | null;
  email?: string | null;
  username?: string | null;
  [k: string]: any;
}
```

## Adding New Models

### 1. Create Pydantic Model
```python
# backend/models/core/user.py
class NewModel(BaseModel):
    id: str
    name: str
    value: Optional[int] = None
```

### 2. Export in __init__.py
```python
# backend/models/core/__init__.py
from .user import NewModel

__all__ = [
    # ... existing exports
    "NewModel"
]
```

### 3. Update Export Script
```python
# backend/scripts/export_schemas.py
from models.core import (
    # ... existing imports
    NewModel
)

models = [
    # ... existing models
    NewModel
]
```

### 4. Regenerate Types
```bash
cd frontend
npm run generate:all
```

### 5. Use in Frontend
```typescript
import { NewModel } from '@/shared/generated-types';

const example: NewModel = {
  id: "123",
  name: "Example"
};
```

## Best Practices

### ✅ Do
- Define all data models in `backend/models/core/`
- Use Pydantic BaseModel for all models
- Add proper type hints and Field constraints
- Generate types after any model changes
- Import generated types in frontend

### ❌ Don't
- Edit generated TypeScript files manually
- Create duplicate interfaces in frontend
- Skip type generation after backend changes
- Mix manual and generated types

## Migration from Manual Types

The project is transitioning from manual shared types to generated types:

1. **Generated types** are in `shared/generated-types/`
2. **Legacy manual types** are in `shared/types/core/`
3. Gradually replace imports from `@/shared/types` to `@/shared/generated-types`

## Troubleshooting

### Schema Export Fails
- Check Python dependencies: `pip install pydantic`
- Verify all imports in `backend/models/core/__init__.py`
- Run script from `backend/` directory

### TypeScript Generation Fails
- Check Node dependencies: `npm install json-schema-to-typescript`
- Verify schemas exist in `shared/schemas/`
- Check for circular references in models

### Type Mismatches
- Regenerate types: `npm run generate:all`
- Check Pydantic model definitions
- Verify field types and constraints

## Integration with Development

### Pre-commit Hook (Optional)
Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd frontend
npm run generate:all
git add shared/schemas/ shared/generated-types/
```

### CI/CD Integration
Add to build pipeline:

```yaml
# Example GitHub Actions
- name: Generate Types
  run: |
    cd frontend
    npm run generate:all
    
- name: Check for Changes
  run: git diff --exit-code shared/
```

## Benefits

✅ **Single Source of Truth** - Python models define all data structures  
✅ **Runtime Validation** - Pydantic provides backend validation  
✅ **Type Safety** - Generated TypeScript ensures frontend type safety  
✅ **Auto-sync** - Types automatically stay in sync  
✅ **Developer Experience** - IDE autocomplete and error checking  
✅ **Reduced Duplication** - No manual interface maintenance  

This system ensures that backend and frontend types are always synchronized, reducing bugs and improving developer productivity.