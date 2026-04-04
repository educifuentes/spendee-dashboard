# Release & Deployment Process

Since this boilerplate is intended to be generic, the release process is centered around keeping a clean standard git flow.

## 1. Branching Strategy
- `main` represents the stable staging or production environment.
- Feature branches `feature/description` are used for developing new models.
- Hotfixes `hotfix/description` for rapid deployment patching.

## 2. Pull Requests
1. Open a pull request against `main`.
2. Ensure you have run local testing including rendering out your dataframes locally or using a test fixture in `tests/`.
3. Check UI integrations in the `.streamlit` framework by running `npm run dev` or `streamlit run app.py` locally. 

## 3. Deployment
- Releasing to `main` triggers cloud pipelines (e.g. via `cloudbuild.yaml` or AWS CodeBuild).
- Valid cloud configurations will automatically stand up the latest dashboard.
