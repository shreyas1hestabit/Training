### installation and setup

**_ 1. Activate Virtual Enviornment _**

```bash
source venv/bin/activate
```

**_ 2. write requirements.txt _**

contains all the dependencies and libraries that need to be installed. We have used a pre-compiled version of `llama-cpp-python` to ensure compatibilty with cpu. install all the dependencies in requirements.txt with

```bash
pip install -r requirements.txt
```

**_ 3. run the FastAPI server _**

```bash
uvicorn deploy.app:app --reload
```
