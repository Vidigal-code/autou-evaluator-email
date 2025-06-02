const CONFIG = {
  ENDPOINTS: {
    PROCESS: "/process",
  },
  FILE_SIZE_UNITS: ["Bytes", "KB", "MB", "GB"],
  THEMES: {
    LIGHT: "light",
    DARK: "dark",
  },
  CATEGORIES: {
    PRODUCTIVE: "produtivo",
    WARNING: "warning",
  },
};

const Utils = {
  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${
      CONFIG.FILE_SIZE_UNITS[i]
    }`;
  },

  capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  },

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
};

class ThemeManager {
  constructor() {
    this.currentTheme = this.getInitialTheme();
    this.themeToggle = null;
  }

  getInitialTheme() {
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    return prefersDark ? CONFIG.THEMES.DARK : CONFIG.THEMES.LIGHT;
  }

  init(toggleButton) {
    this.themeToggle = toggleButton;
    this.setTheme(this.currentTheme);

    if (this.themeToggle) {
      this.themeToggle.addEventListener("click", () => this.toggle());
    }
  }

  toggle() {
    const newTheme =
      this.currentTheme === CONFIG.THEMES.DARK
        ? CONFIG.THEMES.LIGHT
        : CONFIG.THEMES.DARK;
    this.setTheme(newTheme);
  }

  setTheme(theme) {
    this.currentTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    this.updateToggleButton();
  }

  updateToggleButton() {
    if (this.themeToggle) {
      this.themeToggle.textContent =
        this.currentTheme === CONFIG.THEMES.DARK ? "☀️" : "🌙";
    }
  }
}

class FileManager {
  constructor(fileInput, previewElement, fileUploadArea) {
    this.fileInput = fileInput;
    this.previewElement = previewElement;
    this.fileUploadArea = fileUploadArea;
    this.currentFile = null;
    this.init();
  }

  init() {
    if (this.fileInput && this.previewElement && this.fileUploadArea) {
      this.fileUploadArea.addEventListener("click", (e) => {
        if (e.target !== this.fileInput) {
          this.fileInput.click();
        }
      });

      ["dragenter", "dragover"].forEach((eventName) => {
        this.fileUploadArea.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.fileUploadArea.classList.add("dragover");
        });
      });

      ["dragleave", "drop"].forEach((eventName) => {
        this.fileUploadArea.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.fileUploadArea.classList.remove("dragover");
        });
      });

      this.fileUploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
          this.fileInput.files = files;
          this.updatePreview();
        }
      });

      this.fileInput.addEventListener("change", () => this.updatePreview());
    }
  }

  updatePreview() {
    const file = this.fileInput.files[0];
    this.currentFile = file;

    if (file) {
      this.showPreview(file);
    } else {
      this.hidePreview();
    }
  }

  showPreview(file) {
    this.previewElement.textContent = `Arquivo: ${
      file.name
    } (${Utils.formatFileSize(file.size)})`;
    this.previewElement.style.display = "inline-block";
  }

  hidePreview() {
    this.previewElement.style.display = "none";
  }

  getFile() {
    return this.currentFile;
  }
}

class ApiManager {
  constructor() {
    this.controller = null;
  }

  async processForm(formData) {
    if (this.controller) {
      this.controller.abort();
    }

    this.controller = new AbortController();

    try {
      const response = await fetch(CONFIG.ENDPOINTS.PROCESS, {
        method: "POST",
        body: formData,
        signal: this.controller.signal,
      });

      await this.validateResponse(response);
      const data = await response.json();
      this.validateData(data);

      return data;
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error("Requisição cancelada");
      }
      throw error;
    } finally {
      this.controller = null;
    }
  }

  async validateResponse(response) {
    const contentType = response.headers.get("content-type");

    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      throw new Error(`Resposta inválida do servidor: ${text}`);
    }

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }
  }

  validateData(data) {
    if (!data || typeof data !== "object") {
      throw new Error("Resposta inesperada do servidor.");
    }

    if (data.error) {
      throw new Error(data.error);
    }

    if (!("categoria" in data) || !("resposta" in data)) {
      throw new Error("Dados incompletos na resposta.");
    }
  }
}

class UIManager {
  constructor(resultDiv, loadingDiv) {
    this.resultDiv = resultDiv;
    this.loadingDiv = loadingDiv;
  }

  showLoading(isVisible = true) {
    if (this.loadingDiv) {
      this.loadingDiv.style.display = isVisible ? "block" : "none";
    }
  }

  clearResult() {
    if (this.resultDiv) {
      this.resultDiv.innerHTML = "";
      this.resultDiv.style.display = "none";
    }
  }

  displayResult(data) {
    if (!this.resultDiv) return;

    const template = this.createResultTemplate(data);
    this.resultDiv.innerHTML = template;
    this.resultDiv.style.display = "block";
  }

  displayError(errorMessage) {
    if (!this.resultDiv) return;

    const template = this.createErrorTemplate(errorMessage);
    this.resultDiv.innerHTML = template;
    this.resultDiv.style.display = "block";
  }

  createResultTemplate(data) {
    const categoriaClass =
      data.categoria === CONFIG.CATEGORIES.PRODUCTIVE ? "success" : "warning";
    const icon = data.categoria === CONFIG.CATEGORIES.PRODUCTIVE ? "✅" : "💡";

    return `
            <div class="result-container">
                <div class="result-section">
                    <h3>Classificação</h3>
                    <span class="badge ${categoriaClass}">
                        <span class="cat-icon" aria-hidden="true">${icon}</span>
                        ${Utils.capitalize(data.categoria)}
                    </span>
                </div>
                <div class="result-section">
                    <h3>Resposta Gerada</h3>
                    <div class="response-text">${this.sanitizeHtml(
                      data.resposta
                    )}</div>
                </div>
                ${
                  data.texto_processado
                    ? `
                    <div class="result-section">
                        <h3>Texto Processado (prévia)</h3>
                        <div class="processed-text">${this.sanitizeHtml(
                          data.texto_processado
                        )}</div>
                    </div>
                `
                    : ""
                }
            </div>
        `;
  }

  createErrorTemplate(errorMessage) {
    return `
            <div class="error-container">
                <h3>Erro</h3>
                <p class="error-message">${this.sanitizeHtml(errorMessage)}</p>
                <div class="error-help">
                    <p>Verifique se:</p>
                    <ul>
                        <li>O arquivo está no formato correto (PDF ou TXT)</li>
                        <li>O texto não está vazio</li>
                        <li>O servidor está funcionando corretamente</li>
                    </ul>
                </div>
            </div>
        `;
  }

  sanitizeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
}

class EmailFormApp {
  constructor() {
    this.themeManager = new ThemeManager();
    this.fileManager = null;
    this.apiManager = new ApiManager();
    this.uiManager = null;
    this.form = null;
    this.isProcessing = false;
  }

  init() {
    this.bindElements();
    this.initializeComponents();
    this.attachEventListeners();
  }

  bindElements() {
    this.form = document.getElementById("emailForm");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");
    const themeToggle = document.getElementById("theme-toggle");
    const fileInput = document.getElementById("file");
    const filePreview = document.getElementById("filePreview");
    const fileUploadArea = document.getElementById("fileUploadArea");

    this.uiManager = new UIManager(resultDiv, loadingDiv);
    this.fileManager = new FileManager(fileInput, filePreview, fileUploadArea);
  }

  initializeComponents() {
    const themeToggle = document.getElementById("theme-toggle");
    this.themeManager.init(themeToggle);
  }

  attachEventListeners() {
    if (this.form) {
      this.form.addEventListener("submit", (e) => {
        e.preventDefault();
        void this.handleSubmit(e);
      });
    }

    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", (e) => {
        if (!this.themeManager.themeToggle) return;
        const newTheme = e.matches ? CONFIG.THEMES.DARK : CONFIG.THEMES.LIGHT;
        this.themeManager.setTheme(newTheme);
      });
  }

  async handleSubmit(event) {
    event.preventDefault();

    if (this.isProcessing) {
      return;
    }

    this.isProcessing = true;
    this.uiManager.showLoading(true);
    this.uiManager.clearResult();

    try {
      const formData = this.prepareFormData();
      const data = await this.apiManager.processForm(formData);
      this.uiManager.displayResult(data);
    } catch (error) {
      this.handleError(error);
    } finally {
      this.uiManager.showLoading(false);
      this.isProcessing = false;
    }
  }

  prepareFormData() {
    const formData = new FormData(this.form);
    const file = this.fileManager.getFile();

    if (file) {
      formData.set("file", file);
    }

    return formData;
  }

  handleError(error) {
    console.error("Erro no processamento:", error);

    let userMessage = error.message;

    if (error.message.includes("Failed to fetch")) {
      userMessage =
        "Erro de conexão. Verifique sua internet e tente novamente.";
    } else if (error.message.includes("Requisição cancelada")) {
      userMessage = "Requisição cancelada.";
    }

    this.uiManager.displayError(userMessage);
  }

  destroy() {
    if (this.apiManager.controller) {
      this.apiManager.controller.abort();
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new EmailFormApp();
  app.init();

  window.emailFormApp = app;
});

window.addEventListener("beforeunload", () => {
  if (window.emailFormApp) {
    window.emailFormApp.destroy();
  }
});
