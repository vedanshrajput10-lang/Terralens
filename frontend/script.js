const API_URL = "https://terralens-vvqc.onrender.com";

async function checkBackend() {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    console.log("TerraLens backend:", data);
  } catch (error) {
    console.log("Backend is not running yet.");
  }
}

document.querySelectorAll("#scanBtn, #navScanBtn").forEach((button) => {
  button.addEventListener("click", () => {
    alert("Crop Scan module will be connected to the AI next.");
  });
});

document.getElementById("voiceBtn").addEventListener("click", () => {
  alert("Voice module will be connected next.");
});

checkBackend();
