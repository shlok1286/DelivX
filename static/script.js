/* ══════════════════════════════════════════
   DeliverIQ – Frontend Logic
   ══════════════════════════════════════════ */

/* ── DOM refs ────────────────────────────────────────────────── */
const form         = document.getElementById("predict-form");
const predictBtn   = document.getElementById("predict-btn");
const btnText      = document.getElementById("btn-text");
const btnSpinner   = document.getElementById("btn-spinner");
const btnArrow     = document.getElementById("btn-arrow");

const resultEmpty  = document.getElementById("result-empty");
const resultFilled = document.getElementById("result-filled");
const resultError  = document.getElementById("result-error");
const resultNumber = document.getElementById("result-number");
const resultStatus = document.getElementById("result-status");
const resultStatusText = document.getElementById("result-status-text");
const summaryDesc  = document.getElementById("summary-desc");
const errorMsg     = document.getElementById("error-msg");

const impDistance  = document.getElementById("impact-distance");
const impTraffic   = document.getElementById("impact-traffic");
const impWeather   = document.getElementById("impact-weather");
const impOverall   = document.getElementById("impact-overall");

/* ── Helpers ─────────────────────────────────────────────────── */
function setLoading(on) {
  predictBtn.disabled = on;
  btnText.hidden      = on;
  btnSpinner.hidden   = !on;
  if (btnArrow) btnArrow.hidden = on;
}

function setImpact(el, level, label) {
  el.textContent = label;
  el.className   = "impact-badge " + level;
}

function getDistanceImpact(km) {
  if (km < 5)  return ["low",    "Low"];
  if (km < 14) return ["medium", "Medium"];
  return              ["high",   "High"];
}

function getWeatherImpact(w) {
  if (w === "Clear")           return ["low",    "Low"];
  if (w === "Windy" || w === "Foggy") return ["medium", "Medium"];
  if (w === "Rainy")           return ["medium", "Medium"];
  return                              ["high",   "High"]; // Snowy
}

function getTrafficImpact(t) {
  if (t === "Low")    return ["low",  "Low"];
  if (t === "Medium") return ["medium","Medium"];
  return                     ["high", "High"];
}

function getOverall(dLvl, tLvl, wLvl) {
  const score = { low: 1, medium: 2, high: 3 };
  const avg = (score[dLvl] + score[tLvl] + score[wLvl]) / 3;
  if (avg <= 1.5)  return ["low",      "Low"];
  if (avg <= 2.2)  return ["moderate", "Moderate"];
  return                  ["high",     "High"];
}

function getSummaryText(mins, traffic, weather) {
  const parts = [];
  if (traffic === "High") parts.push("high traffic conditions");
  if (traffic === "Medium") parts.push("moderate traffic");
  if (weather === "Rainy" || weather === "Snowy") parts.push(`${weather.toLowerCase()} weather`);
  if (weather === "Foggy") parts.push("foggy conditions");

  if (mins <= 30)  return "Fast delivery expected. Conditions are favourable.";
  if (parts.length === 0)
    return mins <= 50
      ? "Standard delivery window. Conditions are average."
      : "Longer delivery expected based on distance and preparation time.";
  return `Moderate delivery time due to ${parts.join(" and ")}.`;
}

function getStatusInfo(mins) {
  if (mins <= 40) return { label: "On Time",  cls: "" };
  if (mins <= 65) return { label: "Moderate", cls: "moderate" };
  return               { label: "Delayed",   cls: "delayed" };
}

/* ── Count-up ────────────────────────────────────────────────── */
function animateCount(target, duration = 600) {
  const start = performance.now();
  const from  = parseInt(resultNumber.textContent) || 0;
  function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 2);
    resultNumber.textContent = Math.round(from + (target - from) * ease);
    if (t < 1) requestAnimationFrame(tick);
    else resultNumber.textContent = target;
  }
  requestAnimationFrame(tick);
}

/* ── Form submit ─────────────────────────────────────────────── */
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Reset UI
  resultFilled.hidden = true;
  resultError.hidden  = true;
  setLoading(true);

  const distance   = parseFloat(document.getElementById("distance").value);
  const weather    = document.getElementById("weather").value;
  const traffic    = document.getElementById("traffic").value;
  const time_of_day = document.getElementById("time_of_day").value;
  const vehicle    = document.getElementById("vehicle").value;
  const prep_time  = parseFloat(document.getElementById("prep_time").value);
  const experience = parseFloat(document.getElementById("experience").value);

  const payload = { distance, weather, traffic, time_of_day, vehicle, prep_time, experience };

  try {
    const res  = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.success) {
      const mins = Math.round(data.prediction);

      // Show filled result panel
      resultEmpty.hidden  = true;
      resultFilled.hidden = false;
      resultError.hidden  = true;

      // Status chip
      const { label, cls } = getStatusInfo(mins);
      resultStatus.className = "result-status" + (cls ? " " + cls : "");
      resultStatusText.textContent = label;

      // Summary text
      summaryDesc.textContent = getSummaryText(mins, traffic, weather);

      // Impact badges
      const [dLvl, dLabel] = getDistanceImpact(distance);
      const [tLvl, tLabel] = getTrafficImpact(traffic);
      const [wLvl, wLabel] = getWeatherImpact(weather);
      const [oLvl, oLabel] = getOverall(dLvl, tLvl, wLvl);

      setImpact(impDistance, dLvl,    dLabel);
      setImpact(impTraffic,  tLvl,    tLabel);
      setImpact(impWeather,  wLvl,    wLabel);
      setImpact(impOverall,  oLvl,    oLabel);

      // Number animation
      animateCount(mins);

    } else {
      resultEmpty.hidden  = true;
      resultFilled.hidden = true;
      resultError.hidden  = false;
      errorMsg.textContent = data.error || "Prediction failed.";
    }

  } catch {
    resultEmpty.hidden  = true;
    resultFilled.hidden = true;
    resultError.hidden  = false;
    errorMsg.textContent = "Network error — is the server running?";
  } finally {
    setLoading(false);
  }
});
