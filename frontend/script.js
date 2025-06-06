// frontend/script.js

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const resumeInput = document.getElementById("resume");
    const jdTextarea = document.getElementById("jdtext");
    const resultDiv = document.getElementById("results");
    const spinner = document.getElementById("spinner");
  
    // Clear previous results and hide any errors
    resultDiv.innerHTML = "";
  
    // Validate inputs
    if (resumeInput.files.length === 0) {
      alert("Please select your resume PDF.");
      return;
    }
    if (!jdTextarea.value.trim()) {
      alert("Please paste the job description text.");
      return;
    }
  
    // Build FormData for API call
    const formData = new FormData();
    formData.append("resume_file", resumeInput.files[0]);
    formData.append("jd_text", jdTextarea.value);
  
    try {
      // Show spinner
      spinner.style.display = "block";
  
      // Call FastAPI endpoint
      const response = await fetch("https://ai-resume-scanner-backend.onrender.com/match/", {
        method: "POST",
        body: formData,
      });
  
      // Hide spinner once response returns (success or error)
      spinner.style.display = "none";
  
      if (!response.ok) {
        // Display error payload if status is not OK
        const errorPayload = await response.json();
        resultDiv.innerHTML = `<div class="error"><pre>${JSON.stringify(
          errorPayload,
          null,
          2
        )}</pre></div>`;
        return;
      }
  
      const data = await response.json();
  
      // Build HTML for results
      let html = `
        <h2>Results</h2>
        <p><strong>Match %:</strong> ${data.match_percentage}%</p>
        <p><strong>Matched Skills:</strong> ${
          data.matched_skills.join(", ") || "None"
        }</p>
        <p><strong>Missing Skills:</strong> ${
          data.missing_skills.join(", ") || "None"
        }</p>
        <h3>Rewritten Bullets:</h3>
        <ul>
      `;
  
      // Display rewritten bullets
      data.rewritten_bullets.forEach((b) => {
        html += `<li>${b}</li>`;
      });
      html += `</ul><h3>Suggestions:</h3><ul>`;
  
      // Display suggestions
      data.suggestions.forEach((s) => {
        html += `<li>${s}</li>`;
      });
      html += `</ul>`;
  
      resultDiv.innerHTML = html;
    } catch (err) {
      // Hide spinner
      spinner.style.display = "none";
  
      console.error(err);
      resultDiv.innerHTML = `<div class="error"><p>Error: ${
        err.message
      }</p></div>`;
    }
  });
  