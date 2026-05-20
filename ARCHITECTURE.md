# Hexagonal Architecture & Agent Rules

## 1. Architectural Blueprint (Hexagonal Modular) - Backend
The project follows a Hexagonal Architecture (Ports and Adapters) structured by technical layers with domain sub-modules at the leaf level.

### Directory Structure - Backend
- `src/app/`: Application services, orchestrating use cases.
- `src/core/entities/`: Domain models and business logic. Pure objects.
- `src/core/usecase/`: Application logic. One file per use case (SRP).
- `src/core/contracts/`: Interfaces and DTOs (Ports/Contracts) strictly for REST/HTTP.
    - `request/`: Input DTOs and Adapter Port Interfaces per module.
    - `response/`: Output DTOs and serialization formats per module.
- `src/entrypoints/`: Adapters for input (REST Controllers, CLI).
- `src/repositories/`: Adapters for output (Persistence implementations).
- `src/dependencies/`: Dependency injection and wire-up logic.

## 2. File Naming Standards - Backend
Files must follow these strict naming conventions based on their layer and HTTP intent:

### 2.1 Use Cases & Repositories
- **GET:** `list_<function>.py`
- **POST:** `create_<function>.py`
- **PUT/PATCH:** `update_<function>.py`
- **DELETE:** `delete_<function>.py`

### 2.2 Entities
- `<entity>.py`

### 2.3 Contracts (Requests & Responses)
#### Request
- **GET:** `list_<function>_request.py`
- **POST:** `create_<function>_request.py`
- **PUT/PATCH:** `update_<function>_request.py`
- **DELETE:** `delete_<function>_request.py`

#### Response
- **GET:** `list_<function>_response.py`
- **POST:** `create_<function>_response.py`
- **PUT/PATCH:** `update_<function>_response.py`
- **DELETE:** `delete_<function>_response.py`

### 2.4 Entrypoints
- `<module>.py`

## 3. Agent Instruction Guide: Efficiency and Programming Standards - General

### 3.1 Token Efficiency Rules (Strict Mode)
- **Zero Filler:** Omit greetings, closings, and polite phrases.
- **No Paraphrasing:** Do not repeat the question. Start directly with the answer.
- **Telegraphic Style:** Minimum words necessary.
- **Pure Delivery:** Return **only** the code block unless explanations are explicitly requested.
- **Immediate Termination:** Stop generation as soon as the technical objective is met.

### 3.2 Testing Standards
- **Focused Execution:** Run only tests associated with the modified file.
- **Test Updates:** Modify tests if logic changes are intentional.
- **Real Verification:** Verify actual output. No excessive mocking.
- **Granularity:** Minimum one test per use case or logical branch.
- **Coverage:** Minimum **80%** coverage for modified files.

### 3.3 Code Best Practices
- **Constants Management:** Declare literals as constants at the top of the file.
- **Self-Documenting Code:** No comments. Clean, descriptive naming only.
- **Architectural Respect:** Strictly adhere to the Hexagonal structure.
- **Error Centralization:** Map all errors in a centralized `errors` file.
- **Strict Typing:** Use type hints/strong typing.
- **SRP:** Single Responsibility Principle per class/function.
- **DRY:** Abstract repetitive logic.
- **Semantic Naming:** Descriptive purpose-based names.
- **Input Validation:** Use Guard Clauses at function start.

### 3.4 Agent Workflow
1. Receive requirement.
2. Identify affected files.
3. Apply "Code Best Practices".
4. Update/Create tests per "Testing Standards".
5. Deliver per "Token Efficiency Rules".