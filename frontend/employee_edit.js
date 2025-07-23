// employee_edit.js
const urlParams = new URLSearchParams(window.location.search);
const originalId = urlParams.get('id');

fetch(`http://127.0.0.1:8002/worker/${originalId}`)
  .then(response => response.json())
  .then(data => {
    document.getElementById('firstName').value = data.first_name;
    document.getElementById('lastName').value = data.last_name;
    document.getElementById('workerId').value = data.id;
    document.getElementById('hourlyRate').value = data.hourly_rate;
    document.getElementById('rate_saturday').value = data.rate_saturday || 0;
    document.getElementById('rate_sunday').value = data.rate_sunday || 0;
    document.getElementById('rate_night').value = data.rate_night || 0;
    document.getElementById('rate_overtime').value = data.rate_overtime || 0;
  });

document.getElementById("editForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const newId = document.getElementById("workerId").value;
  const updatedWorker = {
    first_name: document.getElementById("firstName").value,
    last_name: document.getElementById("lastName").value,
    rate: parseFloat(document.getElementById("hourlyRate").value),
    new_id: newId,
    rate_saturday: parseFloat(document.getElementById('rate_saturday').value),
    rate_sunday: parseFloat(document.getElementById('rate_sunday').value),
    rate_night: parseFloat(document.getElementById('rate_night').value),
    rate_overtime: parseFloat(document.getElementById('rate_overtime').value)
  };

  const response = await fetch(`http://127.0.0.1:8002/worker/${originalId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updatedWorker),
  });

  if (response.ok) {
    alert("Zapisano zmiany!");
    window.location.href = "index.html#team";
  } else {
    alert("Błąd zapisu");
  }
});

function goBack() {
  window.history.back();
}
