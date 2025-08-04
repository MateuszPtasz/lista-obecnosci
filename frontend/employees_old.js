// employees.js - Nowoczesny interfejs zarządzania pracownikami

document.addEventListener('DOMContentLoaded', () => {
  loadEmployeesTable();
});

// Nie potrzebujemy już renderEmployeeTable, bo HTML jest już w pliku
function loadEmployees() {
  loadEmployeesTable();
}

async function loadEmployeesTable() {
  try {
    const tbody = document.getElementById('employeeList');
    
    // Pokaż loading
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align: center; padding: 2rem;">
          <i class="fas fa-spinner fa-spin text-primary" style="font-size: 2rem;"></i>
          <p class="mt-2 text-muted">Ładowanie pracowników...</p>
        </td>
      </tr>
    `;
    
    const response = await fetch('http://localhost:8000/workers');
    
    if (response.ok) {
      const employees = await response.json();
      tbody.innerHTML = '';
      
      if (employees.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" style="text-align: center; padding: 2rem;">
              <i class="fas fa-user-slash text-muted" style="font-size: 3rem;"></i>
              <h3 class="mt-2 text-muted">Brak pracowników</h3>
              <p class="text-muted">Dodaj pierwszego pracownika do systemu.</p>
            </td>
          </tr>
        `;
        return;
      }
      
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
          <td>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <i class="fas fa-user-circle text-primary" style="font-size: 1.5rem;"></i>
              <strong>${firstName} ${lastName}</strong>
            </div>
          </td>
          <td>
            <span class="status status-unknown">#${employee.id}</span>
          </td>
          <td>
            <span class="text-success" style="font-weight: 600;">
              <i class="fas fa-coins"></i> ${employee.hourly_rate} zł/h
            </span>
          </td>
          <td>
            <div style="display: flex; gap: 0.5rem;">
              <a href="employee_edit.html?id=${employee.id}" class="btn btn-sm btn-secondary">
                <i class="fas fa-edit"></i> Edytuj
              </a>
              <button onclick="deleteEmployee('${employee.id}')" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Usuń
              </button>
            </div>
          </td>
        `;
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

  const response = await fetch(`http://localhost:8000/workers/${id}`, {
    method: "DELETE"
  });

  if (response.ok) {
    alert("Usunięto pracownika.");
    location.reload();
  } else {
    alert("Błąd podczas usuwania.");
  }
}
