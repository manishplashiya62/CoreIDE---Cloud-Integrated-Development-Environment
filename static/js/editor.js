// Monaco Editor & Workspace Actions Manager

window.activeFileId = null;
window.openTabs = {}; // Map of fileId -> { name, language, content, model, viewState }
let editorInstance = null;
let autoSaveTimeout = null;

// Initialize Monaco Editor
function initMonaco() {
    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        // Register custom themes if needed or use vs-dark
        editorInstance = monaco.editor.create(document.getElementById('monaco-editor'), {
            value: '/* Select or create a file to start coding */',
            language: 'javascript',
            theme: 'vs-dark',
            automaticLayout: true,
            fontSize: 14,
            minimap: { enabled: false },
            padding: { top: 10, bottom: 10 }
        });

        // Listen for content changes for auto-save
        editorInstance.onDidChangeModelContent(() => {
            if (window.activeFileId) {
                // Update current file content in tab dictionary
                window.openTabs[window.activeFileId].content = editorInstance.getValue();
                triggerAutoSave(window.activeFileId, editorInstance.getValue());
            }
        });

        // Load project files
        if (window.tree) {
            window.tree.load();
        }
    });
}

// Map database languages to Monaco language identifiers
function getMonacoLanguage(lang) {
    if (!lang) return 'plaintext';
    lang = lang.toLowerCase();
    if (lang === 'python') return 'python';
    if (lang === 'javascript') return 'javascript';
    if (lang === 'c' || lang === 'cpp') return 'cpp';
    if (lang === 'java') return 'java';
    if (lang === 'html') return 'html';
    if (lang === 'css') return 'css';
    return 'plaintext';
}

// Open File in Editor
async function openFileInEditor(fileId, name, language) {
    if (window.activeFileId === fileId) return;

    // Save previous active file's view state
    if (window.activeFileId && window.openTabs[window.activeFileId]) {
        window.openTabs[window.activeFileId].viewState = editorInstance.saveViewState();
    }

    window.activeFileId = fileId;
    
    // Check if file is already loaded in tabs
    if (!window.openTabs[fileId]) {
        try {
            const res = await fetch(`/api/files/${fileId}`);
            if (!res.ok) throw new Error("Could not retrieve file contents.");
            const fileData = await res.json();
            
            // Create a Monaco model
            const monacoLang = getMonacoLanguage(language);
            const model = monaco.editor.createModel(fileData.content || "", monacoLang);
            
            window.openTabs[fileId] = {
                name: name,
                language: language,
                content: fileData.content,
                model: model,
                viewState: null
            };
        } catch (e) {
            showToast(e.message, 'danger');
            return;
        }
    }

    // Set model in Monaco Editor
    const tabData = window.openTabs[fileId];
    editorInstance.setModel(tabData.model);
    
    // Restore view state if it exists
    if (tabData.viewState) {
        editorInstance.restoreViewState(tabData.viewState);
    }
    
    editorInstance.focus();

    // Render tabs on UI
    renderTabs();
}

// Render Tabs UI
function renderTabs() {
    const tabBar = document.getElementById('tab-bar');
    tabBar.innerHTML = '';
    
    Object.keys(window.openTabs).forEach(fileId => {
        const id = parseInt(fileId);
        const tabData = window.openTabs[id];
        
        const tabDiv = document.createElement('div');
        tabDiv.className = `tab ${window.activeFileId === id ? 'active' : ''}`;
        tabDiv.onclick = () => openFileInEditor(id, tabData.name, tabData.language);
        
        const nameSpan = document.createElement('span');
        nameSpan.innerText = tabData.name;
        
        const closeSpan = document.createElement('span');
        closeSpan.className = 'tab-close';
        closeSpan.innerHTML = '&times;';
        closeSpan.onclick = (e) => {
            e.stopPropagation();
            closeTab(id);
        };
        
        tabDiv.appendChild(nameSpan);
        tabDiv.appendChild(closeSpan);
        tabBar.appendChild(tabDiv);
    });
}

// Close Editor Tab
function closeTab(fileId) {
    if (!window.openTabs[fileId]) return;
    
    // Dispose model to free memory
    if (window.openTabs[fileId].model) {
        window.openTabs[fileId].model.dispose();
    }
    
    delete window.openTabs[fileId];
    
    // If we closed the active tab, switch to another
    if (window.activeFileId === fileId) {
        const remainingTabIds = Object.keys(window.openTabs);
        if (remainingTabIds.length > 0) {
            const nextId = parseInt(remainingTabIds[0]);
            const nextTab = window.openTabs[nextId];
            openFileInEditor(nextId, nextTab.name, nextTab.language);
        } else {
            window.activeFileId = null;
            editorInstance.setModel(null);
            editorInstance.setValue('/* Select or create a file to start coding */');
        }
    }
    renderTabs();
}

// Update tab name dynamically (triggered from rename)
function updateTabName(fileId, newName) {
    if (window.openTabs[fileId]) {
        window.openTabs[fileId].name = newName;
        renderTabs();
    }
}

// Trigger Debounced Auto Save
function triggerAutoSave(fileId, content) {
    const saveIndicator = document.getElementById('save-status');
    if (saveIndicator) {
        saveIndicator.innerText = 'Saving...';
    }
    
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`/api/files/${fileId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            if (res.ok && saveIndicator) {
                saveIndicator.innerText = 'Saved';
            }
        } catch (e) {
            if (saveIndicator) saveIndicator.innerText = 'Save Error';
        }
    }, 1000);
}

// Font Size Adjustments
function changeFontSize(action) {
    if (!editorInstance) return;
    const currentSize = editorInstance.getOption(monaco.editor.EditorOption.fontSize);
    let newSize = currentSize;
    if (action === 'increase') newSize += 2;
    if (action === 'decrease' && currentSize > 8) newSize -= 2;
    editorInstance.updateOptions({ fontSize: newSize });
}

// Theme Toggles
function setTheme(themeName) {
    if (!editorInstance) return;
    monaco.editor.setTheme(themeName);
}

// --- Run Code Execution ---
async function executeCode() {
    if (!window.activeFileId) {
        showToast("Please open a file to execute code.", "warning");
        return;
    }
    
    const activeFile = window.openTabs[window.activeFileId];
    const language = activeFile.language;
    
    if (['python', 'javascript', 'c', 'cpp', 'java'].indexOf(language) === -1) {
        showToast(`Running code for "${language}" is not supported yet.`, "warning");
        return;
    }
    
    const runBtn = document.getElementById('run-btn');
    const consoleOutput = document.getElementById('console-output');
    const stdinText = document.getElementById('stdin-input').value;
    const statsTimer = document.getElementById('stats-timer');
    const statsMemory = document.getElementById('stats-memory');
    
    runBtn.disabled = true;
    runBtn.innerHTML = '⚡ Running...';
    consoleOutput.innerText = 'Compiling & Running...\n';
    consoleOutput.classList.remove('error');
    
    try {
        const res = await fetch('/api/compiler/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                language: language,
                source_code: editorInstance.getValue(),
                stdin_data: stdinText
            })
        });
        
        if (!res.ok) throw new Error("Compilation network request failed.");
        const result = await res.json();
        
        if (result.compile_error) {
            consoleOutput.classList.add('error');
            consoleOutput.innerText = `[COMPILATION ERROR]\n${result.compile_error}`;
            statsTimer.innerText = '0.00s';
            statsMemory.innerText = '0.0MB';
        } else {
            let output = result.stdout;
            if (result.stderr) {
                output += `\n[STDERR]\n${result.stderr}`;
            }
            if (!output.trim()) {
                output = "[Process finished with no output]";
            }
            consoleOutput.innerText = output;
            statsTimer.innerText = `${result.execution_time}s`;
            statsMemory.innerText = `${result.memory_usage}MB`;
        }
    } catch (e) {
        consoleOutput.classList.add('error');
        consoleOutput.innerText = `Runner error: ${e.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '⚡ Run Code';
    }
}

// Clear Terminal Console
function clearConsole() {
    document.getElementById('console-output').innerText = '';
    document.getElementById('stats-timer').innerText = '0.00s';
    document.getElementById('stats-memory').innerText = '0.0MB';
}

// --- AI Coding Assistant ---
async function askAI(promptText = '') {
    if (!editorInstance) return;
    const code = editorInstance.getValue();
    const chatHistory = document.getElementById('ai-chat-history');
    const inputField = document.getElementById('ai-prompt-input');
    
    const query = promptText || inputField.value;
    if (!query.trim()) return;
    
    // Add user message to UI
    appendAIMessage(query, 'user');
    if (!promptText) inputField.value = '';
    
    // Add typing loader
    const loaderId = appendAIMessage('Thinking...', 'assistant loader');
    
    try {
        const res = await fetch('/api/compiler/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: query,
                code: code
            })
        });
        
        const loader = document.getElementById(loaderId);
        if (loader) loader.remove();
        
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || "AI API request failed.");
        }
        
        const result = await res.json();
        appendAIMessage(result.response, 'assistant');
    } catch (e) {
        const loader = document.getElementById(loaderId);
        if (loader) loader.remove();
        appendAIMessage(`**Connection Error**: ${e.message}`, 'assistant');
    }
}

function appendAIMessage(text, type) {
    const chatHistory = document.getElementById('ai-chat-history');
    const msgDiv = document.createElement('div');
    const msgId = 'ai-msg-' + Math.random().toString(36).substr(2, 9);
    msgDiv.id = msgId;
    msgDiv.className = `ai-message ${type}`;
    
    if (type.includes('assistant')) {
        // Format markdown codes simply
        msgDiv.innerHTML = text.replace(/`([^`]+)`/g, '<code>$1</code>')
                               .replace(/```([\s\S]+?)```/g, '<pre>$1</pre>')
                               .replace(/\n/g, '<br>');
    } else {
        msgDiv.innerText = text;
    }
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return msgId;
}


// Global hook up
window.openFileInEditor = openFileInEditor;
window.closeTab = closeTab;
window.updateTabName = updateTabName;
window.initMonaco = initMonaco;
window.executeCode = executeCode;
window.clearConsole = clearConsole;
window.changeFontSize = changeFontSize;
window.setTheme = setTheme;
window.askAI = askAI;
