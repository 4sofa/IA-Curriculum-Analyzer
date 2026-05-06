const form = document.querySelector("#analysisForm");
const resumeInput = document.querySelector("#resumeInput");
const dropZone = document.querySelector("#dropZone");
const fileName = document.querySelector("#fileName");
const fileError = document.querySelector("#fileError");
const formError = document.querySelector("#formError");
const jobDescription = document.querySelector("#jobDescription");
const charCount = document.querySelector("#charCount");
const submitButton = document.querySelector("#submitButton");
const buttonSpinner = document.querySelector("#buttonSpinner");
const buttonText = document.querySelector("#buttonText");
const result = document.querySelector("#result");
const resultMeta = document.querySelector("#resultMeta");
const emptyState = document.querySelector("#emptyState");
const clearButton = document.querySelector("#clearButton");
const apiStatus = document.querySelector("#apiStatus");

const allowedExtensions = [".pdf", ".docx"];
const maxFileBytes = 8 * 1024 * 1024;

marked.setOptions({
  breaks: true,
  gfm: true,
});

checkApiStatus();

dropZone.addEventListener("click", () => resumeInput.click());

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("is-dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("is-dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("is-dragover");

  const file = event.dataTransfer.files?.[0];
  if (!file) return;

  const transfer = new DataTransfer();
  transfer.items.add(file);
  resumeInput.files = transfer.files;
  updateSelectedFile();
});

resumeInput.addEventListener("change", updateSelectedFile);

jobDescription.addEventListener("input", () => {
  charCount.textContent = `${jobDescription.value.length} caracteres`;
});

clearButton.addEventListener("click", () => {
  result.innerHTML = "";
  result.classList.add("hidden");
  emptyState.classList.remove("hidden");
  resultMeta.textContent = "A analise aparecera aqui apos o envio.";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();

  const file = resumeInput.files?.[0];
  const validationError = validateFile(file);
  if (validationError) {
    showFileError(validationError);
    return;
  }

  if (jobDescription.value.trim().length < 20) {
    showFormError("Cole uma descricao da vaga com detalhes suficientes para analise.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_description", jobDescription.value.trim());

  setLoading(true);

  try {
    const response = await fetch("/api/analyses", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error?.message || "Nao foi possivel concluir a analise.");
    }

    renderMarkdown(payload.data.analysis);
    resultMeta.textContent = `Modelo: ${payload.data.model} | Arquivo: ${payload.data.filename}`;
  } catch (error) {
    showFormError(error.message);
  } finally {
    setLoading(false);
  }
});

function updateSelectedFile() {
  clearError();
  const file = resumeInput.files?.[0];
  const validationError = validateFile(file);

  if (validationError) {
    fileName.textContent = "";
    showFileError(validationError);
    return;
  }

  fileName.textContent = file ? file.name : "";
}

function validateFile(file) {
  if (!file) return "Selecione um arquivo PDF ou DOCX.";

  const lowerName = file.name.toLowerCase();
  const isAllowed = allowedExtensions.some((extension) => lowerName.endsWith(extension));
  if (!isAllowed) return "Formato invalido. Envie apenas .pdf ou .docx.";

  if (file.size > maxFileBytes) return "Arquivo muito grande. O limite e 8 MB.";

  return "";
}

function renderMarkdown(markdown) {
  const unsafeHtml = marked.parse(markdown);
  result.innerHTML = DOMPurify.sanitize(unsafeHtml);
  emptyState.classList.add("hidden");
  result.classList.remove("hidden");
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  buttonSpinner.classList.toggle("hidden", !isLoading);
  buttonText.textContent = isLoading ? "Analisando..." : "Analisar Curriculo";
}

function showFileError(message) {
  fileError.textContent = message;
  fileError.classList.remove("hidden");
}

function showFormError(message) {
  formError.textContent = message;
  formError.classList.remove("hidden");
}

function clearError() {
  fileError.textContent = "";
  fileError.classList.add("hidden");
  formError.textContent = "";
  formError.classList.add("hidden");
}

async function checkApiStatus() {
  try {
    const response = await fetch("/api/ready");
    const payload = await response.json();
    const ready = payload.data?.has_openrouter_api_key;
    apiStatus.textContent = ready ? "API pronta" : "API sem chave OpenRouter";
  } catch {
    apiStatus.textContent = "API indisponivel";
  }
}
