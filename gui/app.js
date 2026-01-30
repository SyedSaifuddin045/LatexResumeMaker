// App Logic

// Navigation
function navigate(viewId) {
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    document.getElementById('view-' + viewId).classList.add('active');

    // Highlight nav item
    const navIndex = viewId === 'generate' ? 0 : 1;
    document.querySelectorAll('.nav-item')[navIndex].classList.add('active');
}

// Settings Toggle
function toggleAiSettings() {
    const provider = document.getElementById('ai-provider').value;
    const isLocal = provider === 'ollama';
    const isGoogle = provider === 'google';

    // Toggle API Key visibility
    document.getElementById('group-api-key').style.display = isLocal ? 'none' : 'block';

    // Adjust logic for model inputs/placeholders
    if (isLocal) {
        document.getElementById('model-name').value = "llama3:latest";
    } else if (isGoogle) {
        document.getElementById('model-name').value = "gemini-3-flash-preview";
    } else {
        document.getElementById('model-name').value = "gpt-4o-mini";
    }
}

function toggleTemplateEditor() {
    const val = document.getElementById('template-select').value;
    const isCustom = val === 'custom';
    document.getElementById('template-editor-group').style.display = isCustom ? 'block' : 'none';
}

// Tab Switching
function switchRightTab(mode) {
    // Buttons
    document.getElementById('tab-pdf').style.fontWeight = mode === 'pdf' ? 'bold' : 'normal';
    document.getElementById('tab-pdf').style.borderBottom = mode === 'pdf' ? '2px solid var(--accent)' : 'none';
    document.getElementById('tab-pdf').style.color = mode === 'pdf' ? 'white' : 'var(--text-muted)';

    document.getElementById('tab-source').style.fontWeight = mode === 'source' ? 'bold' : 'normal';
    document.getElementById('tab-source').style.borderBottom = mode === 'source' ? '2px solid var(--accent)' : 'none';
    document.getElementById('tab-source').style.color = mode === 'source' ? 'white' : 'var(--text-muted)';

    // Views
    document.getElementById('view-pdf').style.display = mode === 'pdf' ? 'block' : 'none';
    document.getElementById('view-source').style.display = mode === 'source' ? 'flex' : 'none';

    document.getElementById('btn-compile').style.display = mode === 'source' ? 'block' : 'none';
}

// Advanced Settings Toggles
function toggleAdvanced(type) {
    const id = type === 'resume' ? 'advanced-settings-resume' : 'advanced-settings-fix';
    const arrowId = type === 'resume' ? 'adv-arrow-resume' : 'adv-arrow-fix';

    const el = document.getElementById(id);
    const arrow = document.getElementById(arrowId);
    const isVisible = el.style.display === 'block';
    el.style.display = isVisible ? 'none' : 'block';
    arrow.textContent = isVisible ? '▶' : '▼';
}

// Error Console
function toggleErrorConsole(forceState = null) {
    const el = document.getElementById('error-console');
    const icon = document.getElementById('err-toggle-icon');

    const isExpanded = el.classList.contains('expanded');
    let shouldExpand = forceState !== null ? forceState : !isExpanded;

    if (shouldExpand) {
        el.style.display = 'flex';
        // tiny delay to allow display block to render before transition
        setTimeout(() => el.classList.add('expanded'), 10);
        icon.textContent = '▼';
    } else {
        el.classList.remove('expanded');
        setTimeout(() => el.style.display = 'none', 300); // match transition
        icon.textContent = '▲';
    }
}

async function resetDefaultPrompt(type) {
    try {
        if (type === 'resume') {
            const val = await pywebview.api.get_default_prompt();
            if (val) document.getElementById('system-prompt').value = val;
        } else if (type === 'fix') {
            const val = await pywebview.api.get_default_fix_prompt();
            if (val) document.getElementById('system-prompt-fix').value = val;
        }
    } catch (e) {
        console.error("Error getting default prompt", e);
    }
}

// Save Settings
async function saveSettings() {
    const config = {
        provider: document.getElementById('ai-provider').value,
        apiKey: document.getElementById('api-key').value,
        model: document.getElementById('model-name').value,
        system_prompt: document.getElementById('system-prompt').value,
        system_prompt_fix: document.getElementById('system-prompt-fix').value
    };

    try {
        const response = await pywebview.api.save_settings(config);
        document.getElementById('status-text').textContent = 'Settings saved';
        alert("Configuration Saved!");
    } catch (e) {
        alert("Error saving settings: " + e);
    }
}

// --- STOP LOGIC ---
let currentTaskToken = null;

function startTask(type) {
    // type: 'gen' or 'fix'
    document.getElementById('loader').style.display = 'block';

    // Toggle buttons
    if (type === 'gen') {
        document.getElementById('btn-generate').style.display = 'none';
        document.getElementById('btn-stop-gen').style.display = 'inline-block';
    } else if (type === 'fix') {
        document.getElementById('btn-fix').style.display = 'none';
        document.getElementById('btn-stop-fix').style.display = 'inline-block';
    } else if (type === 'compile') {
        document.getElementById('btn-compile').style.display = 'none';
        document.getElementById('btn-stop-compile').style.display = 'inline-block';
    }

    currentTaskToken = Date.now();
    return currentTaskToken;
}

async function stopCurrentTask(event) {
    if (event) event.stopPropagation();

    if (currentTaskToken) {
        currentTaskToken = null; // Invalidate current token

        // Notify backend (best effort)
        try {
            await pywebview.api.cancel_generation();
        } catch (e) { console.log("Cancel signal err", e); }

        resetUI('All');
        document.getElementById('status-text').textContent = 'Stopped';
        document.getElementById('progress-msg').textContent = '';
    }
}

function resetUI(type) {
    document.getElementById('loader').style.display = 'none';

    if (type === 'gen' || type === 'All') {
        document.getElementById('btn-generate').style.display = 'block';
        document.getElementById('btn-stop-gen').style.display = 'none';
    }
    if (type === 'fix' || type === 'All') {
        document.getElementById('btn-fix').style.display = 'inline-block';
        document.getElementById('btn-stop-fix').style.display = 'none';
    }
    if (type === 'compile' || type === 'All') {
        document.getElementById('btn-compile').style.display = 'block';
        document.getElementById('btn-stop-compile').style.display = 'none';
    }
}

// Generate LaTeX Source (Step 1)
async function generateLatexSource() {
    // Reset UI state first
    document.getElementById('error-msg').textContent = '';
    toggleErrorConsole(false);
    document.getElementById('status-text').textContent = 'Generating...';

    const myToken = startTask('gen');

    const jobDesc = document.getElementById('job-desc').value;
    const templateSelect = document.getElementById('template-select').value;

    if (!jobDesc) {
        alert("Please provide a Job Description.");
        resetUI('gen');
        return;
    }

    const payload = {
        job_description: jobDesc,
        template_name: templateSelect,
        user_data: document.getElementById('resume-data').value,
        custom_template_content: templateSelect === 'custom' ? document.getElementById('custom-template').value : null,
    };

    try {
        const result = await pywebview.api.generate_latex_source(payload);

        // Check cancellation
        if (currentTaskToken !== myToken) {
            console.log("Task ignored (cancelled)");
            return;
        }

        if (result.success) {
            document.getElementById('generated-latex').value = result.tex_content;
            document.getElementById('status-text').textContent = 'Source Generated! Review & Compile.';
            switchRightTab('source');
        } else {
            // If backend says cancelled but we missed it logic-wise
            if (result.error === 'Cancelled') {
                document.getElementById('status-text').textContent = 'Stopped';
            } else {
                document.getElementById('error-msg').textContent = "Generation Failed: " + result.error;
                document.getElementById('status-text').textContent = 'Error';
            }
        }
    } catch (e) {
        if (currentTaskToken === myToken)
            document.getElementById('error-msg').textContent = "System Error: " + e;
    } finally {
        if (currentTaskToken === myToken) resetUI('gen');
        // If cancelled, resetUI('All') was already called by stopCurrentTask
    }
}

// Compile PDF (Step 2)
async function compilePdf() {
    const texContent = document.getElementById('generated-latex').value;
    if (!texContent) {
        alert("No LaTeX source found. Please generate it first.");
        return;
    }

    // Compile is fast/local, so no stop button needed usually, but we could add if needed.
    // User requested "api calls", compile runs 'pdflatex' locally.
    // We'll keep standard loader.
    document.getElementById('status-text').textContent = 'Compiling PDF...';
    document.getElementById('error-msg').textContent = '';
    toggleErrorConsole(false);

    const myToken = startTask('compile');

    try {
        const result = await pywebview.api.compile_pdf(texContent);

        if (currentTaskToken !== myToken) return;

        if (result.success) {
            const pdfData = "data:application/pdf;base64," + result.pdf_base64;
            const iframe = document.getElementById('pdf-preview');
            iframe.src = pdfData;

            document.getElementById('pdf-missing').style.display = 'none';
            iframe.style.display = 'block';

            document.getElementById('status-text').textContent = 'Done!';
            switchRightTab('pdf');
        } else {
            document.getElementById('status-text').textContent = 'Compilation Error';

            const rawError = result.error || "Unknown Error";
            document.getElementById('error-body').innerText = rawError;
            window.lastErrorLog = rawError;

            toggleErrorConsole(true);
            switchRightTab('source');

            if (result.no_latex) {
                document.getElementById('error-msg').innerHTML = "<b>Critical:</b> pdflatex not found. See Error Console for details.";
            } else {
                document.getElementById('error-msg').innerText = "Compilation failed. Check Error Console below.";
            }
        }
    } catch (e) {
        if (currentTaskToken === myToken)
            document.getElementById('error-msg').textContent = "System Exception: " + e;
    } finally {
        if (currentTaskToken === myToken) resetUI('compile');
    }
}

async function fixWithAI(event) {
    if (event) event.stopPropagation();

    if (!window.lastErrorLog) {
        alert("No recent errors to fix.");
        return;
    }

    document.getElementById('status-text').textContent = 'AI is fixing LaTeX...';

    const myToken = startTask('fix');
    const source = document.getElementById('generated-latex').value;

    const payload = {
        source: source,
        error: window.lastErrorLog
    };

    try {
        const result = await pywebview.api.fix_latex(payload);

        if (currentTaskToken !== myToken) return; // Cancelled

        if (result.success) {
            document.getElementById('generated-latex').value = result.fixed_content;
            document.getElementById('status-text').textContent = 'Fixed! Try Compiling Again.';
            toggleErrorConsole(false);
            alert("AI has applied a fix. Please review and compile.");
        } else {
            if (result.error === 'Cancelled by user') {
                document.getElementById('status-text').textContent = 'Stopped';
            } else {
                alert("AI Fix Failed: " + result.error);
                document.getElementById('status-text').textContent = 'Fix Error';
            }
        }
    } catch (e) {
        if (currentTaskToken === myToken)
            alert("System Error during Fix: " + e);
    } finally {
        if (currentTaskToken === myToken) resetUI('fix');
    }
}

function openPdf() {
    pywebview.api.open_current_pdf();
}

async function savePdf() {
    try {
        const result = await pywebview.api.save_pdf();
        if (result.success) {
            alert("Saved to: " + result.path);
        } else {
            if (result.error !== 'Cancelled') {
                alert("Save Failed: " + result.error);
            }
        }
    } catch (e) {
        alert("Error saving: " + e);
    }
}

// Init
window.addEventListener('pywebviewready', async function () {
    console.log("Bridge Ready");
    switchRightTab('source');
    const settings = await pywebview.api.load_settings();
    if (settings) {
        document.getElementById('ai-provider').value = settings.provider || 'openai';
        document.getElementById('api-key').value = settings.apiKey || '';
        document.getElementById('model-name').value = settings.model || 'gpt-4o-mini';
        document.getElementById('system-prompt').value = settings.system_prompt || '';
        document.getElementById('system-prompt-fix').value = settings.system_prompt_fix || '';
        toggleAiSettings();
    }
    if (!document.getElementById('system-prompt').value) resetDefaultPrompt('resume');
    if (!document.getElementById('system-prompt-fix').value) resetDefaultPrompt('fix');
});
