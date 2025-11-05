document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ SymptoCare Loaded");

  // -------------------------------
  // 🎙 Voice + Prediction Section
  // -------------------------------
  function speakText(text) {
    if (!("speechSynthesis" in window)) return;
    const msg = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(msg);
  }

  async function predictDisease(symptomText) {
    const arr = symptomText.split(",").map(s => s.trim()).filter(Boolean);
    const resultDiv = document.getElementById("predictionResult");
    resultDiv.innerText = "Predicting...";
    try {
      const res = await axios.post('/predict-disease', { symptoms: arr });
      const disease = res.data.disease || JSON.stringify(res.data);
      resultDiv.innerText = "Predicted Disease: " + disease;
    } catch (err) {
      resultDiv.innerText = "Error: " + (err.response?.data?.error || err.message);
    }
  }

  const predictBtn = document.getElementById("predictBtn");
  if (predictBtn) {
    predictBtn.addEventListener("click", async () => {
      const raw = document.getElementById("symptoms").value.trim();
      if (!raw) return alert("Please enter symptoms.");
      predictDisease(raw);
    });
  }

  const voiceInput = document.getElementById("voiceInput");
  if (voiceInput) {
    voiceInput.addEventListener("click", () => {
      if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        alert("Voice recognition not supported.");
        return;
      }

      const Recog = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new Recog();
      rec.lang = 'en-IN';
      rec.continuous = false;
      rec.interimResults = false;

      voiceInput.innerText = "🎙 Listening...";
      voiceInput.disabled = true;

      rec.start();

      rec.onresult = (e) => {
        const spoken = e.results[0][0].transcript.trim();
        document.getElementById("symptoms").value = spoken;
        predictDisease(spoken);
      };

      rec.onerror = () => alert("Could not recognize voice, please try again.");
      rec.onend = () => {
        voiceInput.innerText = "🎤 Speak";
        voiceInput.disabled = false;
      };
    });
  }

  // -------------------------------
  // 🏥 Hospital Finder Section
  // -------------------------------
  const hospBtn = document.getElementById("hospBtn");
  if (hospBtn) {
    hospBtn.addEventListener("click", async () => {
      const cityInput = document.getElementById("cityHosp");
      const listEl = document.getElementById("hospList");
      const city = cityInput.value.trim();

      if (!city) return alert("Please enter a city name.");
      listEl.innerHTML = "🔎 Searching for hospitals near " + city + "...";

      try {
        const res = await axios.get(`/find-hospitals?city=${encodeURIComponent(city)}`);
        console.log("Hospitals API response:", res.data);
        const results = res.data.results || [];
        listEl.innerHTML = "";

        if (results.length === 0) {
          listEl.innerHTML = "<li>No hospitals found nearby.</li>";
          return;
        }

        results.forEach(h => {
          const li = document.createElement("li");
          li.classList.add("bg-green-100", "p-2", "m-1", "rounded");
          li.textContent = `🏥 ${h.name} (${parseFloat(h.lat).toFixed(3)}, ${parseFloat(h.lon).toFixed(3)})`;
          listEl.appendChild(li);
        });
      } catch (err) {
        console.error("Hospitals error:", err);
        listEl.innerHTML = "<li>❌ Error fetching hospital data.</li>";
      }
    });
  }

  // -------------------------------
  // 💊 Medical Shop Finder Section
  // -------------------------------
  const shopBtn = document.getElementById("shopBtn");
  if (shopBtn) {
    shopBtn.addEventListener("click", async () => {
      const cityInput = document.getElementById("cityShop");
      const listEl = document.getElementById("shopList");
      const city = cityInput.value.trim();

      if (!city) return alert("Please enter a city name.");
      listEl.innerHTML = "🔎 Searching for medical shops near " + city + "...";

      try {
        const res = await axios.get(`/find-medicalshops?city=${encodeURIComponent(city)}`);
        console.log("Shops API response:", res.data);
        const results = res.data.results || [];
        listEl.innerHTML = "";

        if (results.length === 0) {
          listEl.innerHTML = "<li>No medical shops found nearby.</li>";
          return;
        }

        results.forEach(s => {
          const li = document.createElement("li");
          li.classList.add("bg-blue-100", "p-2", "m-1", "rounded");
          li.textContent = `💊 ${s.name} (${parseFloat(s.lat).toFixed(3)}, ${parseFloat(s.lon).toFixed(3)})`;
          listEl.appendChild(li);
        });
      } catch (err) {
        console.error("Shops error:", err);
        listEl.innerHTML = "<li>❌ Error fetching medical shop data.</li>";
      }
    });
  }

  // -------------------------------
  // 🧠 Precautions Section
  // -------------------------------
  const precBtn = document.getElementById("precBtn");
  if (precBtn) {
    precBtn.addEventListener("click", async () => {
      const disease = document.getElementById("diseaseInput").value.trim();
      const resultDiv = document.getElementById("precResult");

      if (!disease) return alert("Enter a disease name.");
      resultDiv.innerHTML = "⏳ Getting precautions for " + disease + "...";

      try {
        const res = await axios.post("/precautions", { disease });
        console.log("Precautions API response:", res.data);
        resultDiv.innerText = res.data.precautions || "No precautions found.";
      } catch (err) {
        console.error("Precautions error:", err);
        resultDiv.innerText = "❌ Error fetching precautions.";
      }
    });
  }

  const speakOut = document.getElementById("speakOut");
  if (speakOut) {
    speakOut.addEventListener("click", () => {
      const txt = document.getElementById("precResult").innerText.trim();
      if (!txt) return alert("No precautions to read");
      speakText(txt);
    });
  }
});
