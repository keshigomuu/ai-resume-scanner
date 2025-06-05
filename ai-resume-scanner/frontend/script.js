// frontend/script.js

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const resumeInput = document.getElementById("resume");
    const jdTextarea = document.getElementById("jdtext");
<<<<<<< Updated upstream
  
=======
    const resultDiv = document.getElementById("results");
  
    // Validate inputs
>>>>>>> Stashed changes
    if (resumeInput.files.length === 0) {
      alert("Please select your resume PDF.");
      return;
    }
    if (!jdTextarea.value.trim()) {
      alert("Please paste the job description text.");
      return;
    }
  
<<<<<<< Updated upstream
=======
    // Build FormData for API call
>>>>>>> Stashed changes
    const formData = new FormData();
    formData.append("resume_file", resumeInput.files[0]);
    formData.append("jd_text", jdTextarea.value);
  
    try {
<<<<<<< Updated upstream
=======
      // Call FastAPI endpoint
>>>>>>> Stashed changes
      const response = await fetch("http://localhost:8000/match/", {
        method: "POST",
        body: formData,
      });
  
<<<<<<< Updated upstream
      const resultDiv = document.getElementById("results");
      if (!response.ok) {
=======
      if (!response.ok) {
        // Display error payload if status is not OK
>>>>>>> Stashed changes
        const errorPayload = await response.json();
        resultDiv.innerHTML = `<pre style="color:red">${JSON.stringify(errorPayload, null, 2)}</pre>`;
        return;
      }
  
      const data = await response.json();
<<<<<<< Updated upstream
=======
  
      // Build HTML for results
>>>>>>> Stashed changes
      let html = `
        <h2>Results</h2>
        <p><strong>Match %:</strong> ${data.match_percentage}%</p>
        <p><strong>Matched Skills:</strong> ${data.matched_skills.join(", ") || "None"}</p>
        <p><strong>Missing Skills:</strong> ${data.missing_skills.join(", ") || "None"}</p>
<<<<<<< Updated upstream
        <h3>Suggestions:</h3>
        <ul>`;
      for (const s of data.suggestions) {
        html += `<li>${s}</li>`;
      }
      html += "</ul>";
=======
        <h3>Missing Context (from JD):</h3>
        <ul>
      `;
  
      // For each missing skill, show the sentences from the JD where it appeared
      data.missing_skills.forEach((skill) => {
        const contexts = data.missing_context[skill] || [];
        html += `<li><strong>${skill}:</strong><ul>`;
        contexts.forEach((sentence) => {
          html += `<li>${sentence}</li>`;
        });
        html += `</ul></li>`;
      });
  
      html += `</ul><h3>Suggestions:</h3><ul>`;
      data.suggestions.forEach((s) => {
        html += `<li>${s}</li>`;
      });
      html += `</ul>`;
  
>>>>>>> Stashed changes
      resultDiv.innerHTML = html;
  
    } catch (err) {
      console.error(err);
<<<<<<< Updated upstream
      document.getElementById("results").innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
=======
      resultDiv.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
>>>>>>> Stashed changes
    }
  });
  