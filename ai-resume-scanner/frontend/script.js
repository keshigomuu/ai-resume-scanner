document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const resumeInput = document.getElementById("resume");
  const jdTextarea = document.getElementById("jdtext");

  if (resumeInput.files.length === 0) {
    alert("Please select your resume PDF.");
    return;
  }
  if (!jdTextarea.value.trim()) {
    alert("Please paste the job description text.");
    return;
  }

  const formData = new FormData();
  formData.append("resume_file", resumeInput.files[0]);
  formData.append("jd_text", jdTextarea.value);

  try {
    const response = await fetch("http://localhost:8000/match/", {
      method: "POST",
      body: formData,
    });

    const resultDiv = document.getElementById("results");
    if (!response.ok) {
      const errorPayload = await response.json();
      resultDiv.innerHTML = `<pre style="color:red">${JSON.stringify(errorPayload, null, 2)}</pre>`;
      return;
    }

    const data = await response.json();
    let html = `
      <h2>Results</h2>
      <p><strong>Match %:</strong> ${data.match_percentage}%</p>
      <p><strong>Matched Skills:</strong> ${data.matched_skills.join(", ") || "None"}</p>
      <p><strong>Missing Skills:</strong> ${data.missing_skills.join(", ") || "None"}</p>
      <h3>Suggestions:</h3>
      <ul>`;
    for (const s of data.suggestions) {
      html += `<li>${s}</li>`;
    }
    html += "</ul>";
    resultDiv.innerHTML = html;

  } catch (err) {
    console.error(err);
    document.getElementById("results").innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
  }
});
