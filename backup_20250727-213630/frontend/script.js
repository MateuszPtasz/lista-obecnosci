// Tutaj będzie logika JS do obsługi aplikacji
console.log('Aplikacja frontendowa działa!');

function showTab(tabId) {
  document.querySelectorAll('.tab').forEach(tab => tab.classList.add('hidden'));
  document.getElementById(tabId).classList.remove('hidden');
}

// Tymczasowo – testowa liczba pracowników w pracy
document.getElementById('inWorkCount').innerText = '5';

// Funkcja do pobierania i wyświetlania wszystkich pracowników w zakładce "Zespół"
async function loadAllEmployees() {
  const response = await fetch("http://localhost:8000/employees");
  const teamList = document.getElementById("teamList");
  teamList.innerHTML = "";

  if (response.ok) {
    const employees = await response.json();
    const table = document.createElement("table");
    table.className = "employee-table";
    table.innerHTML = `<tr><th>Imię i nazwisko</th><th>ID</th><th>Stawka</th><th>Akcje <button id='addWorkerBtn' style='margin-left:8px'>+ Dodaj pracownika</button></th></tr>`;
    for (const e of employees) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${e.name || (e.first_name + ' ' + e.last_name)}</td>
        <td>${e.id || e.employee_id}</td>
        <td>${e.hourly_rate || e.rate || ''} zł</td>
        <td>
          <a href='/frontend/employee_edit.html?id=${e.id}'>Edytuj</a>
          &nbsp;|&nbsp;
          <a href='#' onclick='deleteEmployee("${e.id}")'>Usuń</a>
        </td>
      `;
      table.appendChild(row);
    }
    teamList.appendChild(table);
    // Dodaj obsługę przycisku
    document.getElementById('addWorkerBtn').onclick = () => {
      window.location.href = 'employee_add.html';
    };
  } else {
    teamList.innerHTML = "<p>Błąd pobierania danych pracowników</p>";
  }
}

async function deleteEmployee(id) {
  if (!confirm("Na pewno chcesz usunąć tego pracownika?")) return;
  const response = await fetch(`http://localhost:8000/workers/${id}`, {
    method: "DELETE"
  });
  if (response.ok) {
    alert("Usunięto pracownika.");
    loadAllEmployees();
  } else {
    alert("Błąd podczas usuwania.");
  }
}

// Funkcja do pobierania i wyświetlania logów obecności z dzisiaj
async function loadTodayLogs() {
  const response = await fetch("http://localhost:8000/logs");
  const teamList = document.getElementById("teamList");
  teamList.innerHTML = "";

  if (response.ok) {
    const logs = await response.json();
    const today = new Date().toISOString().slice(0, 10); // 'YYYY-MM-DD'
    // Grupowanie logów po pracowniku (worker_id)
    const logsByWorker = {};
    for (const log of logs) {
      const startDate = log.start_time.slice(0, 10);
      if (startDate === today) {
        if (!logsByWorker[log.worker_id]) logsByWorker[log.worker_id] = [];
        logsByWorker[log.worker_id].push(log);
      }
    }
    for (const workerId in logsByWorker) {
      // Bierzemy najnowszy log dla pracownika
      const log = logsByWorker[workerId].sort((a, b) => new Date(b.start_time) - new Date(a.start_time))[0];
      let html = `<strong>${workerId}</strong> – `;
      const start = new Date(log.start_time);
      let duration = '';
      if (log.stop_time) {
        const stop = new Date(log.stop_time);
        const diffMs = stop - start;
        const h = Math.floor(diffMs / 3600000);
        const m = Math.floor((diffMs % 3600000) / 60000);
        duration = `${h}h ${m}min`;
        const stopHour = stop.getHours().toString().padStart(2, '0');
        const stopMin = stop.getMinutes().toString().padStart(2, '0');
        html += `${duration} – koniec pracy: ${stopHour}:${stopMin}`;
      } else {
        const now = new Date();
        const diffMs = now - start;
        const h = Math.floor(diffMs / 3600000);
        const m = Math.floor((diffMs % 3600000) / 60000);
        duration = `${h}h ${m}min`;
        const startHour = start.getHours().toString().padStart(2, '0');
        const startMin = start.getMinutes().toString().padStart(2, '0');
        html += `<span style='color:green;font-weight:bold' title='W pracy'>&#9679;</span> W PRACY – od ${startHour}:${startMin} (${duration})`;
      }
      const div = document.createElement("div");
      div.className = "employee-log";
      div.innerHTML = html;
      teamList.appendChild(div);
    }
  } else {
    teamList.innerHTML = "<p>Błąd pobierania logów obecności</p>";
  }
}

// Funkcja do pobierania i wyświetlania tylko pracowników online w zakładce "Pulpit"
async function loadOnlineEmployees() {
  const responseLogs = await fetch("http://localhost:8000/logs");
  const responseEmployees = await fetch("http://localhost:8000/employees");
  const inWorkCount = document.getElementById("inWorkCount");
  const onlineList = document.getElementById("onlineList");
  let online = 0;
  let onlineRows = [];
  if (responseLogs.ok && responseEmployees.ok) {
    const logs = await responseLogs.json();
    const employees = await responseEmployees.json();
    const today = new Date().toISOString().slice(0, 10);
    // Mapowanie ID -> {name, id}
    const empMap = {};
    for (const emp of employees) {
      let firstName = emp.first_name;
      let lastName = emp.last_name;
      if (typeof firstName === 'undefined' && typeof lastName === 'undefined' && emp.name) {
        const parts = emp.name.split(' ');
        firstName = parts[0] || '';
        lastName = parts.slice(1).join(' ') || '';
      }
      empMap[emp.id] = { firstName, lastName };
    }
    // Szukamy logów online (brak stop_time)
    const onlineLogs = logs.filter(log => {
      const startDate = log.start_time.slice(0, 10);
      return startDate === today && !log.stop_time;
    });
    online = onlineLogs.length;
    onlineRows = onlineLogs.map(log => {
      const emp = empMap[log.worker_id] || { firstName: log.worker_id, lastName: '' };
      const start = new Date(log.start_time);
      const now = new Date();
      const diffMs = now - start;
      const h = Math.floor(diffMs / 3600000);
      const m = Math.floor((diffMs % 3600000) / 60000);
      const startHour = start.getHours().toString().padStart(2, '0');
      const startMin = start.getMinutes().toString().padStart(2, '0');
      return `<li><strong>${emp.firstName} ${emp.lastName}</strong> – start: ${startHour}:${startMin} (${h}h ${m}min temu)</li>`;
    });
  }
  inWorkCount.innerText = online;
  onlineList.innerHTML = onlineRows.length > 0 ? onlineRows.join('') : '<li>Brak pracowników online</li>';
}

// Automatycznie ładuj zespół po przełączeniu zakładki
window.showTab = function(tabId) {
  document.querySelectorAll('.tab').forEach(tab => tab.classList.add('hidden'));
  document.getElementById(tabId).classList.remove('hidden');
  if(tabId === 'team') loadAllEmployees();
  if(tabId === 'dashboard') loadOnlineEmployees();
}
