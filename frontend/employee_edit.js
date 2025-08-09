// employee_edit.js

// Upewnij się, że DOM jest załadowany
document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const originalId = urlParams.get('id');
  
  if (!originalId) {
    alert('Brak ID pracownika w URL');
    window.location.href = 'employees.html';
    return;
  }

  // Minimalistyczne i bezpieczne budowanie URL API: zawsze względne do bieżącego origin,
  // aby przeglądarka wysyłała ciasteczka sesji i nie traciła autoryzacji.
  function getApiUrl(endpoint) {
    if (!endpoint.startsWith('/api/')) {
      return '/api' + endpoint;
    }
    return endpoint;
  }

  const apiUrl = getApiUrl(`/worker/${originalId}`);
  console.log('API GET URL:', apiUrl);

  fetch(apiUrl, { credentials: 'include' })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    document.getElementById('firstName').value = data.first_name;
    document.getElementById('lastName').value = data.last_name;
    document.getElementById('workerId').value = data.id;
    document.getElementById('pin').value = data.pin || '';
    document.getElementById('hourlyRate').value = data.hourly_rate;
    document.getElementById('rate_saturday').value = data.rate_saturday || 0;
    document.getElementById('rate_sunday').value = data.rate_sunday || 0;
    document.getElementById('rate_night').value = data.rate_night || 0;
    document.getElementById('rate_overtime').value = data.rate_overtime || 0;
  })
  .catch(error => {
    console.error('Błąd pobierania danych pracownika:', error);
    alert('Błąd pobierania danych pracownika');
  });

  // Event listener dla formularza edycji
  const editForm = document.getElementById("editForm");
  if (!editForm) {
    console.error('Formularz editForm nie został znaleziony!');
    return;
  }

  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const newId = document.getElementById("workerId").value;
    const updatedWorker = {
      first_name: document.getElementById("firstName").value,
      last_name: document.getElementById("lastName").value,
      pin: document.getElementById("pin").value,
      hourly_rate: parseFloat(document.getElementById("hourlyRate").value),
      new_id: newId,
      rate_saturday: parseFloat(document.getElementById('rate_saturday').value),
      rate_sunday: parseFloat(document.getElementById('rate_sunday').value),
      rate_night: parseFloat(document.getElementById('rate_night').value),
      rate_overtime: parseFloat(document.getElementById('rate_overtime').value)
    };

    // Dynamiczna konfiguracja URL API dla PUT (również względna)
    const updateApiUrl = getApiUrl(`/worker/${originalId}`);
    console.log('API PUT URL:', updateApiUrl);

    try {
      const response = await fetch(updateApiUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: 'include',
        body: JSON.stringify(updatedWorker),
      });

      if (response.ok) {
        alert("Zapisano zmiany!");
        window.location.href = "employees.html";
      } else {
        const errorData = await response.text();
        console.error('Błąd zapisu:', errorData);
        alert("Błąd zapisu: " + response.status);
      }
    } catch (error) {
      console.error('Błąd zapisu:', error);
      alert("Błąd zapisu - sprawdź połączenie z serwerem");
    }
  });
});

function goBack() {
  window.location.href = "employees.html";
}
