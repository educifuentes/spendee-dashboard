# Local Environment Setup

Follow these steps to configure your local development environment:

### 1. Create a Virtual Environment
```bash
python3 -m venv .venv
```

### 2. Activate the Environment
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

> [!TIP]
> **Productivity Tip: Set up Aliases**
> 
> You can speed up your workflow by adding the following aliases to your shell configuration file (e.g., `~/.zshrc` or `~/.bashrc`):
> 
> ```bash
> alias createenv='python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt'
> alias activate='source .venv/bin/activate'
> alias install='pip install -r requirements.txt'
> alias runapp='streamlit run app.py'
> ```
> 
> After adding them, simply type `createenv`, `activate`, `install`, or `runapp` in your terminal to execute the respective commands instantly.
