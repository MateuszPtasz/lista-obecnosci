// Upewnij się, że DOM jest załadowany przed dodaniem event listenera
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById("addForm");
  if (!form) {
    console.error('Formularz addForm nie został znaleziony!');
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const newWorker = {
      id: document.getElementById("workerId").value,
      first_name: document.getElementById("firstName").value,
      last_name: document.getElementById("lastName").value,
      pin: document.getElementById("pin").value,
      hourly_rate: parseFloat(document.getElementById("hourlyRate").value),
      rate_saturday: parseFloat(document.getElementById("rate_saturday").value) || 0,
      rate_sunday: parseFloat(document.getElementById("rate_sunday").value) || 0,
      rate_night: parseFloat(document.getElementById("rate_night").value) || 0,
      rate_overtime: parseFloat(document.getElementById("rate_overtime").value) || 0
    };

    // Bardziej niezawodne wykrywanie URL API z fallback'ami dla Firefox
    let apiUrl;
    const currentUrl = window.location;
    
    // Debug dla Firefox - logujemy wszystkie dostępne informacje
    console.log('Firefox Debug - window.location:', {
      hostname: currentUrl.hostname,
      port: currentUrl.port,
      protocol: currentUrl.protocol,
      href: currentUrl.href,
      origin: currentUrl.origin
    });
    
    // Firefox fallback: sprawdź czy jesteśmy na localhost z portem
    if (currentUrl.hostname === 'localhost' || currentUrl.hostname === '127.0.0.1') {
      apiUrl = `http://${currentUrl.hostname}:8000/workers`;
    } else if (currentUrl.port && currentUrl.port !== '80' && currentUrl.port !== '443') {
      apiUrl = `http://${currentUrl.hostname}:${currentUrl.port}/workers`;
    } else {
      // Fallback dla względnych URL
      apiUrl = '/workers';
    }

    console.log('Trying API URL:', apiUrl); // Debug dla Firefox
    console.log('Worker data:', newWorker); // Debug danych

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newWorker),
      });

      console.log('Response status:', response.status); // Debug odpowiedzi

      if (response.ok) {
        alert("Pracownik dodany pomyślnie!");
        window.location.href = "employees.html";
      } else {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        alert(`Błąd dodawania pracownika: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      alert(`Błąd połączenia: ${error.message}`);
    }
  });
});

function goBack() {
  window.history.back();
}
