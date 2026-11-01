# The Choice — Architecture v1

## Project overview

The Choice is an interactive, Matrix-inspired branching voting experience. Visitors begin with a Red Pill / Blue Pill decision and follow an individual sequence of questions determined by their previous answers.

When a visitor completes the journey, the application evaluates their complete answer path and presents a personalized prophecy from The Prophet. Community statistics are revealed only after the prophecy.

## Functional requirements

- Anonymous individual journeys.
- Branching questions with answer-dependent navigation.
- One response per question per journey.
- Complete-path-based prophecy selection.
- Persistent journey and response storage.
- Community statistics based only on completed journeys.
- Community statistics revealed after the prophecy.
- No user registration or personal information required.

## Application architecture

### Web application
- Python and Flask.
- Serves the frontend and application API.
- Manages anonymous sessions and journey progression.
- Validates submitted answers.
- Resolves completed paths to prophecies.
- Provides aggregate community statistics.

### Frontend
- HTML, CSS and JavaScript.
- Displays questions, choices and progression.
- Presents the final prophecy.
- Requests community statistics only after prophecy delivery.

### Database
- PostgreSQL.
- Stores questions, options, journeys, responses and prophecies.
- Maintains referential integrity and prevents duplicate responses within a journey.

## Database entities

- `questions`: question text and starting-question information.
- `options`: available answers and next-question relationships.
- `journeys`: anonymous visitor journeys and completion status.
- `responses`: ordered answers belonging to journeys.
- `prophecies`: final messages and outcomes.
- `prophecy_routes`: mapping between complete answer paths and prophecies.

Each option either points to another question or terminates the journey. Every valid completed path must map to a prophecy.

## Prophecy logic

The application reconstructs the ordered sequence of answers for a completed journey. A deterministic path signature identifies the corresponding prophecy.

The same complete answer path always produces the same prophecy. No generative AI is required.

## Community statistics

Statistics are calculated from completed journeys. For each question, percentages use only completed journeys that reached that question.

Statistics are inaccessible through the visitor interface until the prophecy has been revealed. The results page may refresh aggregate statistics periodically.

## Infrastructure

- Local development: RHEL / WSL2 and Python virtual environment.
- Application containerization: Docker-compatible Dockerfile, tested with Podman.
- Local orchestration: Docker Compose.
- Database: PostgreSQL.
- Cloud platform: Azure Kubernetes Service.
- Registry: Azure Container Registry.

## CI/CD and GitOps

- Source code and Kubernetes manifests: GitHub.
- Continuous Integration: Azure Pipelines.
- Container image publishing: Azure Container Registry.
- Continuous Delivery: Argo CD.
- GitOps source of truth: GitHub repository.
- Azure Pipelines publishes images and updates image references in Git.
- Argo CD synchronizes the desired configuration to AKS.

## Kubernetes design

The web application runs as a stateless Deployment with an internal Service and an external access mechanism.

PostgreSQL runs as a StatefulSet with persistent storage and an internal Service.

Application configuration is separated from application images. Credentials must not be committed to Git as plaintext.

## Deliberately excluded from version 1

Redis, a separate background worker, a separate Node.js results service, user accounts and AI-generated prophecies are excluded because they are not required by the initial application functionality.

They may be considered in later versions if a concrete requirement justifies them.