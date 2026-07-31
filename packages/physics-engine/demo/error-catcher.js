/**
 * AEGIS LENS - Error Catcher
 * Comprehensive error capturing system for Physics Engine validation
 * Captures ALL errors, warnings, logs, and exceptions
 */

class ErrorCatcher {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.logs = [];
        this.originalConsole = {
            error: console.error.bind(console),
            warn: console.warn.bind(console),
            log: console.log.bind(console),
            info: console.info.bind(console)
        };
        this.panel = null;
        this.isVisible = false;
        this.init();
    }

    init() {
        // Override console methods
        this.overrideConsole();
        
        // Capture unhandled exceptions
        window.addEventListener('error', (event) => this.handleGlobalError(event));
        
        // Capture promise rejections
        window.addEventListener('unhandledrejection', (event) => this.handleUnhandledRejection(event));
        
        // Capture WASM errors
        this.captureWASMErrors();
        
        // Capture network errors
        this.captureNetworkErrors();
        
        // Create UI panel
        this.createPanel();
    }

    overrideConsole() {
        console.error = (...args) => {
            this.addError('CONSOLE_ERROR', args);
            this.originalConsole.error(...args);
        };

        console.warn = (...args) => {
            this.addWarning('CONSOLE_WARN', args);
            this.originalConsole.warn(...args);
        };

        console.log = (...args) => {
            this.addLog('CONSOLE_LOG', args);
            this.originalConsole.log(...args);
        };

        console.info = (...args) => {
            this.addLog('CONSOLE_INFO', args);
            this.originalConsole.info(...args);
        };
    }

    handleGlobalError(event) {
        this.addError('GLOBAL_ERROR', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error ? event.error.stack : 'No stack trace'
        });
    }

    handleUnhandledRejection(event) {
        this.addError('UNHANDLED_REJECTION', {
            reason: event.reason,
            promise: event.promise
        });
    }

    captureWASMErrors() {
        // WebAssembly instantiation errors
        const originalWebAssemblyInstantiate = WebAssembly.instantiate;
        WebAssembly.instantiate = async (...args) => {
            try {
                return await originalWebAssemblyInstantiate.apply(WebAssembly, args);
            } catch (error) {
                this.addError('WASM_INSTANTIATE', {
                    message: error.message,
                    stack: error.stack
                });
                throw error;
            }
        };
    }

    captureNetworkErrors() {
        // Override fetch to capture network errors
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch.apply(window, args);
                if (!response.ok) {
                    this.addWarning('NETWORK_ERROR', {
                        url: args[0],
                        status: response.status,
                        statusText: response.statusText
                    });
                }
                return response;
            } catch (error) {
                this.addError('NETWORK_ERROR', {
                    url: args[0],
                    message: error.message,
                    stack: error.stack
                });
                throw error;
            }
        };
    }

    addError(type, data) {
        const entry = {
            timestamp: new Date().toISOString(),
            type: 'ERROR',
            severity: 'CRITICAL',
            category: type,
            message: this.formatMessage(data),
            data: data
        };
        this.errors.push(entry);
        this.updatePanel();
    }

    addWarning(type, data) {
        const entry = {
            timestamp: new Date().toISOString(),
            type: 'WARNING',
            severity: 'WARNING',
            category: type,
            message: this.formatMessage(data),
            data: data
        };
        this.warnings.push(entry);
        this.updatePanel();
    }

    addLog(type, data) {
        const entry = {
            timestamp: new Date().toISOString(),
            type: 'INFO',
            severity: 'INFO',
            category: type,
            message: this.formatMessage(data),
            data: data
        };
        this.logs.push(entry);
        this.updatePanel();
    }

    formatMessage(data) {
        if (typeof data === 'string') return data;
        if (Array.isArray(data)) {
            return data.map(item => {
                if (typeof item === 'object') return JSON.stringify(item, null, 2);
                return String(item);
            }).join(' ');
        }
        if (typeof data === 'object') {
            return JSON.stringify(data, null, 2);
        }
        return String(data);
    }

    createPanel() {
        // Create floating panel
        this.panel = document.createElement('div');
        this.panel.id = 'error-catcher-panel';
        this.panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 400px;
            max-height: 300px;
            background: #1a1a2e;
            border: 2px solid #e94560;
            border-radius: 8px;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 10000;
            display: none;
            flex-direction: column;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        `;

        // Create header
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 10px;
            background: #16213e;
            border-bottom: 1px solid #e94560;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
        `;
        header.innerHTML = `
            <span id="error-catcher-title">🔴 ERROR CATCHER — 0 ERRORS / 0 WARNINGS / 0 LOGS</span>
            <button id="error-catcher-toggle" style="background: #e94560; border: none; color: white; padding: 2px 8px; cursor: pointer; border-radius: 4px;">−</button>
        `;

        // Create content area
        const content = document.createElement('div');
        content.id = 'error-catcher-content';
        content.style.cssText = `
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            max-height: 200px;
        `;

        // Create footer
        const footer = document.createElement('div');
        footer.style.cssText = `
            padding: 10px;
            background: #16213e;
            border-top: 1px solid #e94560;
            display: flex;
            gap: 5px;
        `;
        footer.innerHTML = `
            <button id="error-catcher-export" style="flex: 1; background: #0f3460; border: none; color: white; padding: 5px; cursor: pointer; border-radius: 4px;">📋 Export Log</button>
            <button id="error-catcher-clear" style="flex: 1; background: #0f3460; border: none; color: white; padding: 5px; cursor: pointer; border-radius: 4px;">🗑️ Clear</button>
            <button id="error-catcher-summary" style="flex: 1; background: #0f3460; border: none; color: white; padding: 5px; cursor: pointer; border-radius: 4px;">📊 Summary</button>
        `;

        this.panel.appendChild(header);
        this.panel.appendChild(content);
        this.panel.appendChild(footer);
        document.body.appendChild(this.panel);

        // Add event listeners
        document.getElementById('error-catcher-toggle').addEventListener('click', () => this.togglePanel());
        document.getElementById('error-catcher-export').addEventListener('click', () => this.exportLog());
        document.getElementById('error-catcher-clear').addEventListener('click', () => this.clear());
        document.getElementById('error-catcher-summary').addEventListener('click', () => this.showSummary());

        // Make panel draggable
        this.makeDraggable(this.panel, header);
    }

    updatePanel() {
        const title = document.getElementById('error-catcher-title');
        const content = document.getElementById('error-catcher-content');
        
        if (!title || !content) return;
        
        title.textContent = `🔴 ERROR CATCHER — ${this.errors.length} ERRORS / ${this.warnings.length} WARNINGS / ${this.logs.length} LOGS`;
        
        // Combine all entries
        const allEntries = [
            ...this.errors.map(e => ({...e, color: '#e94560'})),
            ...this.warnings.map(w => ({...w, color: '#f39c12'})),
            ...this.logs.map(l => ({...l, color: '#3498db'}))
        ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        content.innerHTML = allEntries.map(entry => `
            <div style="margin-bottom: 8px; padding: 8px; background: #16213e; border-left: 3px solid ${entry.color}; border-radius: 4px;">
                <div style="color: ${entry.color}; font-weight: bold;">${this.formatTimestamp(entry.timestamp)} ${entry.severity} ${entry.category}</div>
                <div style="color: #fff; word-break: break-all;">${entry.message.substring(0, 200)}${entry.message.length > 200 ? '...' : ''}</div>
            </div>
        `).join('');
    }

    formatTimestamp(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString('en-US', { hour12: false });
    }

    togglePanel() {
        this.isVisible = !this.isVisible;
        this.panel.style.display = this.isVisible ? 'flex' : 'none';
        document.getElementById('error-catcher-toggle').textContent = this.isVisible ? '−' : '+';
    }

    show() {
        this.isVisible = true;
        this.panel.style.display = 'flex';
        document.getElementById('error-catcher-toggle').textContent = '−';
    }

    hide() {
        this.isVisible = false;
        this.panel.style.display = 'none';
        document.getElementById('error-catcher-toggle').textContent = '+';
    }

    clear() {
        this.errors = [];
        this.warnings = [];
        this.logs = [];
        this.updatePanel();
    }

    exportLog() {
        const log = {
            errors: this.errors,
            warnings: this.warnings,
            logs: this.logs,
            summary: {
                totalErrors: this.errors.length,
                totalWarnings: this.warnings.length,
                totalLogs: this.logs.length,
                errorsByType: this.countByType(this.errors),
                warningsByType: this.countByType(this.warnings)
            }
        };
        
        const blob = new Blob([JSON.stringify(log, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `error-log-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showSummary() {
        const summary = `
ERROR CATCHER SUMMARY
=====================
Total Errors: ${this.errors.length}
Total Warnings: ${this.warnings.length}
Total Logs: ${this.logs.length}

Errors by Type:
${Object.entries(this.countByType(this.errors)).map(([type, count]) => `  ${type}: ${count}`).join('\n')}

Warnings by Type:
${Object.entries(this.countByType(this.warnings)).map(([type, count]) => `  ${type}: ${count}`).join('\n')}
        `;
        alert(summary);
    }

    countByType(entries) {
        return entries.reduce((acc, entry) => {
            acc[entry.category] = (acc[entry.category] || 0) + 1;
            return acc;
        }, {});
    }

    makeDraggable(element, handle) {
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        handle.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        function dragStart(e) {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            if (e.target === handle || handle.contains(e.target)) {
                isDragging = true;
            }
        }

        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                element.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
            }
        }

        function dragEnd() {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
        }
    }

    getStats() {
        return {
            errors: this.errors.length,
            warnings: this.warnings.length,
            logs: this.logs.length
        };
    }
}

// Initialize error catcher when DOM is ready
if (typeof window !== 'undefined') {
    window.errorCatcher = new ErrorCatcher();
    
    // Show panel by default for validation
    window.errorCatcher.show();
}
