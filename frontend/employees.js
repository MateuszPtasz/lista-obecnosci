// employees.js

document.addEventListener('DOMContentLoaded', () => {
  renderEmployeeTable();
});

function renderEmployeeTable() {
  const container = document.querySelector('.main-content');
  container.innerHTML = `
    <h1>Mój zespół</h1>
    <button onclick="window.location.href='employee_add.html'" style="margin-bottom: 10px;">+ Dodaj pracownika</button>
    <table class="employee-table">
      <thead>
        <tr>
          <th>Imię i nazwisko</th>
          <th>ID</th>
          <th>Stawka</th>
          <th>Akcje</th>
        </tr>
      </thead>
      <tbody id="employeeList"></tbody>
    </table>
  `;
  loadEmployeesTable();
}

async function loadEmployeesTable() {
  try {
    const response = await fetch('http://127.0.0.1:8002/workers');
    const tbody = document.getElementById('employeeList');
    tbody.innerHTML = '';
    if (response.ok) {
      const employees = await response.json();
      for (const employee of employees) {
        let firstName = employee.first_name;
        let lastName = employee.last_name;
        if (typeof firstName === 'undefined' && typeof lastName === 'undefined' && employee.name) {
          const parts = employee.name.split(' ');
          firstName = parts[0] || '';
          lastName = parts.slice(1).join(' ') || '';
        }
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${firstName} ${lastName}</td>
          <td>${employee.id}</td>
          <td>${employee.hourly_rate} zł</td>
          <td>
            <a href="employee_edit.html?id=${employee.id}">Edytuj</a>
            &nbsp;|&nbsp;
            <a href="#" onclick="deleteEmployee('${employee.id}')">Usuń</a>
            &nbsp;|&nbsp;
            <a href="work_log.html?id=${employee.id}">Szczegóły</a>
          </td>
        `;
        tbody.appendChild(row);
      }
    } else {
      tbody.innerHTML = '<tr><td colspan="4">Błąd pobierania danych - status: ' + response.status + '</td></tr>';
    }
  } catch (error) {
    const tbody = document.getElementById('employeeList');
    tbody.innerHTML = '<tr><td colspan="4">Błąd podczas pobierania danych: ' + error.message + '</td></tr>';
    console.error("Błąd w loadEmployeesTable:", error);
  }
}

async function deleteEmployee(id) {
  if (!confirm("Na pewno chcesz usunąć tego pracownika?")) return;

  const response = await fetch(`http://127.0.0.1:8002/workers/${id}`, {
    method: "DELETE"
  });

  if (response.ok) {
    alert("Usunięto pracownika.");
    location.reload();
  } else {
    alert("Błąd podczas usuwania.");
  }
}
