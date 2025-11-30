# Debugging Guide

## Remote Debugging with VS Code

The FastAPI application runs with debugpy enabled on port 5678.

### Setup:

1. **Start the containers:**
   ```bash
   docker compose up --build
   ```

2. **In VS Code:**
   - Open the Run and Debug panel (Cmd+Shift+D / Ctrl+Shift+D)
   - Select "Python: Remote Attach" from the dropdown
   - Click the green play button (or press F5)

3. **Set breakpoints:**
   - Open any Python file (e.g., `app/main.py`, `app/routers/sessions.py`)
   - Click in the gutter to the left of line numbers to set breakpoints

4. **Trigger the code:**
   - Make a request to your API: `curl http://localhost/health`
   - Or visit http://localhost/docs and test endpoints there
   - Execution will pause at your breakpoints

### Alternative: Local Debugging (without Docker)

Use the "Python: FastAPI" configuration to run the app locally:
1. Install dependencies: `uv pip install -e .`
2. Select "Python: FastAPI" and press F5
3. App runs locally on port 80 with full debugging

### Tips:

- **Watch variables:** Hover over variables to see their values
- **Debug console:** Execute Python code in the context of the paused execution
- **Step through:** Use F10 (step over), F11 (step into), Shift+F11 (step out)
- **Call stack:** See the full call stack in the debug panel
- **Restart:** Ctrl+Shift+F5 to restart debugging session

### Ports:
- **80** - FastAPI application
- **5678** - Debugpy remote debugging
- **3306** - MySQL database

### Common Issues:

**"Cannot connect to debugger":**
- Ensure containers are running: `docker compose ps`
- Check logs: `docker compose logs web`
- Verify port 5678 is exposed and not blocked

**Breakpoints not hitting:**
- Ensure you're attached to the debugger (green status bar)
- Verify the code you're debugging is actually executed
- Check pathMappings in launch.json match your project structure
