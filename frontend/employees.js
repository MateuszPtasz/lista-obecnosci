// employees.js - Nowoczesny interfejs zarządzania pracownikami

// Funkcja do tworzenia API URL z fallback'ami dla Firefox
function getApiUrl(endpoint) {
  // Dodaj prefiks /api/ jeśli nie ma go w endpoint
  if (!endpoint.startsWith('/api/')) {
    endpoint = '/api' + endpoint;
  }
  
  const currentUrl = window.location;
  
  // Debug dla Firefox
  console.log('Firefox Debug - window.location:', {
    hostname: currentUrl.hostname,
    port: currentUrl.port,
    protocol: currentUrl.protocol,
    href: currentUrl.href,
    origin: currentUrl.origin
  });
  
  // Zawsze używamy względnych URL dla API
  return endpoint;
}

document.addEventListener('DOMContentLoaded', () => {
  loadEmployeesTable();
  // Obsługa importu CSV
  const importBtn = document.getElementById('importCsvBtn');
  const csvInput = document.getElementById('csvInput');
  if(importBtn && csvInput) {
    importBtn.addEventListener('click', () => csvInput.click());
    csvInput.addEventListener('change', handleCsvImport);
  }
// Funkcja obsługi importu CSV
async function handleCsvImport(e) {
  const file = e.target.files[0];
  if (!file) return;
  const importMessage = document.getElementById('importMessage');
  importMessage.innerHTML = '<span class="text-info"><i class="fas fa-spinner fa-spin"></i> Przetwarzanie pliku CSV...</span>';
  try {
    const text = await file.text();
    // Parsowanie CSV: zakładamy format: imie,nazwisko,pin,stawka
    const lines = text.split(/\r?\n/).filter(l => l.trim());
    const employees = [];
    let lineNumber = 0;
    const errors = [];
    
    for(const line of lines) {
      lineNumber++;
      if(lineNumber === 1 && line.toLowerCase().includes('imie') || line.toLowerCase().includes('nazwisko')) {
        continue; // Pomijamy nagłówek
      }
      
      const values = line.split(',').map(v => v.trim());
      if(values.length !== 4) {
        errors.push(`Wiersz ${lineNumber}: Nieprawidłowa liczba kolumn (oczekiwano: 4, otrzymano: ${values.length})`);
        continue;
      }
      
      const [first_name, last_name, pin, hourly_rate] = values;
      
      if(!first_name || !last_name) {
        errors.push(`Wiersz ${lineNumber}: Brak imienia lub nazwiska`);
        continue;
      }
      
      if(!/^\d+$/.test(pin)) {
        errors.push(`Wiersz ${lineNumber}: PIN musi być liczbą`);
        continue;
      }
      
      const rate = parseFloat(hourly_rate);
      if(isNaN(rate) || rate <= 0) {
        errors.push(`Wiersz ${lineNumber}: Nieprawidłowa stawka godzinowa`);
        continue;
      }
      
      employees.push({
        first_name, 
        last_name, 
        pin,
        hourly_rate: rate
      });
    }
    
    if(errors.length > 0) {
      importMessage.innerHTML = `<div class="alert alert-warning">
        <strong>Znaleziono błędy w pliku:</strong><br>
        ${errors.join('<br>')}
      </div>`;
      return;
    }
    
    if(employees.length === 0) throw new Error('Brak poprawnych danych w pliku CSV.');
    // Wyślij do backendu
    const apiUrl = getApiUrl('/import_employees_csv');
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({employees})
    });
    
    const result = await response.json();
    
    if(!response.ok) {
      throw new Error(result.detail || 'Wystąpił błąd podczas importu');
    }
    
    let message = `<div class="alert alert-success">
      Pomyślnie zaimportowano ${result.imported} pracowników.
    </div>`;
    
    if(result.errors && result.errors.length > 0) {
      message += `<div class="alert alert-warning">
        <strong>Wystąpiły problemy przy imporcie niektórych rekordów:</strong><br>
        ${result.errors.map(err => `Wiersz ${err.row}: ${err.error}`).join('<br>')}
      </div>`;
    }
    
    importMessage.innerHTML = message;
    if(response.ok) {
      importMessage.innerHTML = '<span class="text-success"><i class="fas fa-check"></i> Import zakończony sukcesem!</span>';
      loadEmployeesTable();
    } else {
      const err = await response.text();
      importMessage.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-triangle"></i> Błąd importu: ${err}</span>`;
    }
  } catch(error) {
    importMessage.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-triangle"></i> Błąd: ${error.message}</span>`;
  }
  e.target.value = '';
}
});

// Funkcja odświeżania listy pracowników
function loadEmployees() {
  loadEmployeesTable();
}

async function loadEmployeesTable() {
  try {
    const tbody = document.getElementById('employeeList');
    
    if (!tbody) {
      console.error('Element employeeList nie został znaleziony');
      return;
    }
    
    // Pokaż loading
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; padding: 2rem;">
          <i class="fas fa-spinner fa-spin text-primary" style="font-size: 2rem;"></i>
          <p class="mt-2 text-muted">Ładowanie pracowników...</p>
        </td>
      </tr>
    `;
    
    console.log('Ładowanie pracowników...');
    const apiUrl = getApiUrl('/workers');
    console.log('Fetch URL:', apiUrl);
    
    const response = await fetch(apiUrl);
    console.log('Response status:', response.status);
    
    if (response.ok) {
      const employees = await response.json();
      tbody.innerHTML = '';
      
      if (employees.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; padding: 2rem;">
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
          <td><input type="checkbox" class="employee-checkbox" value="${employee.id}"></td>
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
            <span class="text-info" style="font-weight: 600; font-family: monospace;">
              <i class="fas fa-key"></i> ${employee.pin || '----'}
            </span>
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
        tbody.appendChild(row);
      }
    } else {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            Błąd podczas ładowania pracowników: ${response.status}
          </td>
        </tr>
      `;
    }
  } catch (error) {
    const tbody = document.getElementById('employeeList');
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="error-message">
          <i class="fas fa-exclamation-triangle"></i>
          Błąd połączenia: ${error.message}
        </td>
      </tr>
    `;
    console.error('Error loading employees:', error);
  }
}

async function deleteEmployee(id) {
  if (!confirm('Czy na pewno chcesz usunąć tego pracownika?')) {
    return;
  }
  
  try {
    const apiUrl = getApiUrl(`/workers/${id}`);
    console.log('Delete URL:', apiUrl);
    
    const response = await fetch(apiUrl, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      // Pokaż komunikat sukcesu
      const tbody = document.getElementById('employeeList');
      const successRow = document.createElement('tr');
      successRow.innerHTML = `
        <td colspan="5" class="success-message">
          <i class="fas fa-check-circle"></i>
          Pracownik został usunięty pomyślnie!
        </td>
      `;
      tbody.insertBefore(successRow, tbody.firstChild);
      
      // Usuń komunikat po 3 sekundach i odśwież listę
      setTimeout(() => {
        loadEmployeesTable();
      }, 3000);
    } else {
      alert(`Błąd podczas usuwania pracownika: ${response.status}`);
    }
  } catch (error) {
    alert(`Błąd połączenia: ${error.message}`);
    console.error('Error deleting employee:', error);
  }
}

// Dodaj obsługę checkboxów i grupowego usuwania pracowników
function renderEmployeeRow(employee) {
  return `
    <tr>
      <td><input type="checkbox" class="employee-checkbox" value="${employee.id}"></td>
      <td>${employee.name}</td>
      <td>${employee.id}</td>
      <td>${employee.pin || ''}</td>
      <td>${employee.hourly_rate} zł/h</td>
      <td>
        <a href="employee_edit.html?id=${employee.id}" class="btn btn-sm btn-secondary">Edytuj</a>
        <button onclick="deleteEmployee('${employee.id}')" class="btn btn-sm btn-danger">Usuń</button>
      </td>
    </tr>
  `;
}

function renderEmployeeTable(employees) {
  const tbody = document.getElementById('employeeList');
  tbody.innerHTML = employees.map(renderEmployeeRow).join('');
  // Obsługa checkboxa "Zaznacz wszystko"
  const selectAll = document.getElementById('selectAllEmployees');
  if (selectAll) {
    selectAll.onclick = function() {
      const checkboxes = document.querySelectorAll('.employee-checkbox');
      checkboxes.forEach(cb => { cb.checked = selectAll.checked; });
    };
  }
}

function getSelectedEmployeeIds() {
  return Array.from(document.querySelectorAll('.employee-checkbox:checked')).map(cb => cb.value);
}

async function deleteSelectedEmployees() {
  const ids = getSelectedEmployeeIds();
  if (ids.length === 0) {
    alert('Zaznacz co najmniej jednego pracownika do usunięcia!');
    return;
  }
  if (!confirm(`Czy na pewno chcesz usunąć ${ids.length} pracowników?`)) return;
  const apiUrl = getApiUrl('/workers/batch');
  try {
    const response = await fetch(apiUrl, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ids)
    });
    const data = await response.json();
    if (data.count_deleted > 0) {
      alert(`Usunięto ${data.count_deleted} pracowników.`);
      loadEmployeesTable();
    } else {
      alert('Nie udało się usunąć żadnego pracownika.');
    }
  } catch (err) {
    alert('Błąd podczas usuwania pracowników.');
  }
}

// Dodaj przycisk nad tabelą
window.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('employeeListContainer');
  if (container) {
    const btn = document.createElement('button');
    btn.className = 'btn btn-danger';
    btn.textContent = 'Usuń zaznaczonych';
    btn.style.marginBottom = '1rem';
    btn.onclick = deleteSelectedEmployees;
    container.insertAdjacentElement('afterbegin', btn);
  }
});
