document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('emailForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const themeToggle = document.getElementById('theme-toggle');
    const fileInput = document.getElementById('file');
    const filePreview = document.getElementById('filePreview');

    let currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            currentTheme = (currentTheme === 'dark') ? 'light' : 'dark';
            setTheme(currentTheme);
            localStorage.setItem('theme', currentTheme);
        });
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        if(themeToggle) themeToggle.textContent = theme === 'dark' ? "☀️" : "🌙";
    }

    if (form) {
        form.addEventListener('submit', handleSubmit);
    }

    if (fileInput && filePreview) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                filePreview.textContent = `Arquivo: ${file.name} (${formatFileSize(file.size)})`;
                filePreview.style.display = 'inline-block';
            } else {
                filePreview.style.display = 'none';
            }
        });
    }

    async function handleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    if (fileInput.files[0]) {
        formData.set('file', fileInput.files[0]);
    }

    if (loadingDiv) {
        loadingDiv.style.display = 'block';
    }
    if (resultDiv) {
        resultDiv.style.display = 'none';
        resultDiv.innerHTML = '';
    }

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            throw new Error('Servidor retornou resposta inválida: ' + text);
        }
        if (!data || typeof data !== "object") {
            throw new Error("Resposta inesperada do servidor.");
        }
        if (data.error) {
            throw new Error(data.error);
        }
        if (!('categoria' in data) || !('resposta' in data)) {
            throw new Error("Resposta do servidor incompleta.");
        }
        displayResult(data);

    } catch (error) {
        displayError(error.message);
    } finally {
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
}

function displayResult(data) {
    if (!resultDiv) return;
    const categoriaClass = data.categoria === 'produtivo' ? 'success' : 'warning';
    const catIcon = data.categoria === 'produtivo'
        ? '<span class="cat-icon" aria-hidden="true">✅</span>'
        : '<span class="cat-icon" aria-hidden="true">💡</span>';
    resultDiv.innerHTML = `
        <div class="result-container">
            <div class="result-section">
                <h3>Classificação</h3>
                <span class="badge ${categoriaClass}">
                    ${catIcon}
                    ${data.categoria.charAt(0).toUpperCase() + data.categoria.slice(1)}
                </span>
            </div>
            <div class="result-section">
                <h3>Resposta Gerada</h3>
                <div class="response-text">
                    ${data.resposta}
                </div>
            </div>
            ${data.texto_processado ? `
                <div class="result-section">
                    <h3>Texto Processado (prévia)</h3>
                    <div class="processed-text">
                        ${data.texto_processado}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    resultDiv.style.display = 'block';
}

    function displayError(errorMessage) {
        if (!resultDiv) return;
        resultDiv.innerHTML = `
            <div class="error-container">
                <h3>Erro</h3>
                <p class="error-message">${errorMessage}</p>
                <p class="error-help">
                    Verifique se:
                    <ul>
                        <li>O arquivo está no formato correto (PDF ou TXT)</li>
                        <li>O texto não está vazio</li>
                        <li>O servidor está funcionando corretamente</li>
                    </ul>
                </p>
            </div>
        `;
        resultDiv.style.display = 'block';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});