document.getElementById("addForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const newWorker = {
    id: document.getElementById("workerId").value,
    first_name: document.getElementById("firstName").value,
    last_name: document.getElementById("lastName").value,
    hourly_rate: parseFloat(document.getElementById("hourlyRate").value),
    rate_saturday: parseFloat(document.getElementById("rate_saturday").value) || 0,
    rate_sunday: parseFloat(document.getElementById("rate_sunday").value) || 0,
    rate_night: parseFloat(document.getElementById("rate_night").value) || 0,
    rate_overtime: parseFloat(document.getElementById("rate_overtime").value) || 0
  };

  const response = await fetch("http://127.0.0.1:8002/workers", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(newWorker),
  });

  if (response.ok) {
    alert("Pracownik dodany!");
    window.location.href = "index.html#team";
  } else {
    alert("Błąd dodawania pracownika");
  }
});

function goBack() {
  window.history.back();
}
