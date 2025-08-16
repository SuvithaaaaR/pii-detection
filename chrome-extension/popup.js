document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("uploadForm");
  if (!form) return;
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const fileInput = document.getElementById("file");
    if (!fileInput.files || fileInput.files.length === 0) {
      document.getElementById("result").innerHTML =
        '<div class="error">Please select a file to analyze.</div>';
      return;
    }
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append(
      "service_type",
      document.getElementById("service_type").value
    );
    document.getElementById("result").innerHTML =
      '<div class="loader"></div><div class="loading-text">Analyzing document for PII...</div>';
    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Server error: " + res.status);
      const data = await res.json();
      let html = "<h2>Detected PII</h2><ul>";
      if (data.pii && data.pii.length > 0) {
        data.pii.forEach((p) => {
          html += `<li>\n                <div class=\"pii-type\">${p.type}</div>\n                <div class=\"pii-value\">${p.masked ? p.masked : p.value}</div>\n                ${
            p.confidence
              ? `<div class=\"confidence\">Confidence: ${p.confidence}</div>`
              : ""
          }\n              </li>`;
        });
      } else {
        html +=
          '<li><div class="pii-value">No PII detected in this document.</div></li>';
      }
      html += "</ul><h2>Data Necessity</h2><ul>";
      if (data.necessity && data.necessity.length > 0) {
        data.necessity.forEach((n) => {
          html += `<li>\n                <div class=\"pii-type\">${
            n.type
          }</div>\n                <div class=\"pii-value\">${
            n.value
          }</div>\n                <div class=\"${
            n.needed ? "needed" : "not-needed"
          }\">${
            n.needed ? "✓ Required" : "✗ Not Required"
          }</div>\n              </li>`;
        });
      } else {
        html +=
          '<li><div class="pii-value">No necessity information available.</div></li>';
      }
      html += "</ul>";
      document.getElementById("result").innerHTML = html;
      document.getElementById("downloadMaskedBtn").style.display = "block";
    } catch (err) {
      document.getElementById("result").innerHTML =
        '<div class="error">❌ Error: ' + err.message + "</div>";
    }
  });

  // Download masked file logic
  document.getElementById("downloadMaskedBtn").onclick = async function () {
    const fileInput = document.getElementById("file");
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    const res = await fetch("http://127.0.0.1:5000/download-masked", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      alert("Failed to download masked file.");
      return;
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "masked.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };
});
