// work_log.js

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const workerId = urlParams.get('id');
  if (!workerId) return;
  const response = await fetch(`http://127.0.0.1:8002/logs/${workerId}`);
  const container = document.getElementById('workLogTable');
  if (!response.ok) {
    container.innerHTML = '<p>Błąd pobierania danych.</p>';
    return;
  }
  const logs = await response.json();
  if (!logs.length) {
    container.innerHTML = '<p>Brak logów dla tego pracownika.</p>';
    return;
  }
  let html = "<table class='employee-table'><thead><tr><th>Data</th><th>Wejście</th><th>Wyjście</th><th>Czas pracy</th><th>Dzień tygodnia</th><th>Akcje</th></tr></thead><tbody>";
  for (const log of logs) {
    if (!log.start_time || !log.stop_time) continue;
    const start = new Date(log.start_time);
    const stop = new Date(log.stop_time);
    const durationMin = Math.round((stop - start) / 60000);
    const hours = Math.floor(durationMin / 60);
    const minutes = durationMin % 60;
    const durationStr = `${hours}h ${minutes}min`;
    let rate = log.hourly_rate || log.rate || 0;
    if (!rate && log.worker_id) {
      const empRes = await fetch(`http://127.0.0.1:8002/worker/${log.worker_id}`);
      if (empRes.ok) {
        const emp = await empRes.json();
        rate = emp.hourly_rate || 0;
      }
    }
    const kwota = ((rate * durationMin) / 60).toFixed(2);
    const dayOfWeek = start.toLocaleDateString('pl-PL', { weekday: 'long' });
    const dateStr = start.toISOString().slice(0,10);
    html += `<tr>
      <td data-date="${dateStr}">${dateStr} <span style='color:#888;font-size:0.95em;'>(${dayOfWeek})</span></td>
      <td><input type="time" value="${start.toISOString().slice(11,16)}" id="start-${log.id}" /></td>
      <td><input type="time" value="${stop.toISOString().slice(11,16)}" id="stop-${log.id}" /></td>
      <td>${durationStr}</td>
      <td>${kwota} zł</td>
      <td>
        <button onclick="saveEdit(${log.id})">💾 Zapisz</button>
        <button onclick="deleteLog(${log.id})" style="color:red;">❌</button>
      </td>
    </tr>`;
  }
  html += "</tbody></table>";
  container.innerHTML = html;

  document.getElementById('add-log-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const date = document.getElementById('new-date').value;
    const startTime = document.getElementById('new-start').value;
    const stopTime = document.getElementById('new-stop').value;
    const workerId = new URLSearchParams(window.location.search).get('id');

    const startDateTime = `${date}T${startTime}:00`;
    const stopDateTime = `${date}T${stopTime}:00`;

    await fetch('/logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        worker_id: workerId,
        start_time: startDateTime,
        stop_time: stopDateTime,
        start_lat: 0.0,
        start_lon: 0.0,
        stop_lat: 0.0,
        stop_lon: 0.0,
      })
    });

    location.reload();
  });
});

async function saveEdit(logId) {
  const start = document.getElementById(`start-${logId}`).value;
  const stop = document.getElementById(`stop-${logId}`).value;
  const rowDate = document.querySelector(`#start-${logId}`).closest('tr').children[0].dataset.date;
  const startDateTime = `${rowDate}T${start}:00`;
  const stopDateTime = `${rowDate}T${stop}:00`;
  const res = await fetch(`/logs/${logId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start_time: startDateTime,
      stop_time: stopDateTime
    })
  });
  if (res.ok) {
    alert("Zapisano zmiany");
    location.reload();
  } else {
    alert("Błąd zapisu");
  }
}

async function deleteLog(logId) {
  if (!confirm("Na pewno chcesz usunąć ten wpis?")) return;
  const res = await fetch(`/logs/${logId}`, {
    method: 'DELETE'
  });
  if (res.ok) {
    alert("Usunięto wpis");
    location.reload();
  } else {
    alert("Błąd usuwania");
  }
}
