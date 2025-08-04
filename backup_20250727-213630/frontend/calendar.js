// Kalendarz w sidebarze
let calendarMonth = (new Date()).getMonth();
let calendarYear = (new Date()).getFullYear();
let isCalendarExpanded = false;

function renderCalendar() {
  const calendarElement = document.getElementById('calendar');
  if (!calendarElement) return;

  const now = new Date();
  const currentMonth = new Date(calendarYear, calendarMonth, 1);
  
  // Nagłówek z nawigacją
  let calHtml = `
    <div class="calendar-nav">
      <button id="calPrev" title="Poprzedni miesiąc">
        <i class="fas fa-chevron-left"></i>
      </button>
      <span class="calendar-month-year">
        ${currentMonth.toLocaleString('pl-PL', { month: 'long', year: 'numeric' })}
      </span>
      <button id="calNext" title="Następny miesiąc">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  `;

  // Tabela kalendarza
  calHtml += `<table>`;
  
  // Nagłówki dni tygodnia (skrócone)
  calHtml += `<tr>`;
  ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd'].forEach(day => {
    calHtml += `<th>${day}</th>`;
  });
  calHtml += `</tr>`;

  // Oblicz pierwszy dzień miesiąca (poniedziałek = 1)
  let firstDay = currentMonth.getDay();
  if (firstDay === 0) firstDay = 7; // Niedziela jako 7

  // Liczba dni w miesiącu
  const daysInMonth = new Date(calendarYear, calendarMonth + 1, 0).getDate();
  
  // Liczba dni w poprzednim miesiącu  
  const daysInPrevMonth = new Date(calendarYear, calendarMonth, 0).getDate();

  let currentDate = 1;
  let nextMonthDate = 1;

  // Generuj wiersze kalendarza (6 wierszy)
  for (let week = 0; week < 6; week++) {
    calHtml += `<tr>`;
    
    for (let day = 1; day <= 7; day++) {
      const cellNumber = week * 7 + day;
      
      if (cellNumber < firstDay) {
        // Dni z poprzedniego miesiąca
        const prevDate = daysInPrevMonth - (firstDay - cellNumber) + 1;
        calHtml += `<td class="other-month">${prevDate}</td>`;
      } else if (currentDate <= daysInMonth) {
        // Dni bieżącego miesiąca
        const isToday = (currentDate === now.getDate() && 
                        calendarMonth === now.getMonth() && 
                        calendarYear === now.getFullYear());
        
        let classes = [];
        if (isToday) classes.push('today');
        if (currentDate === 1) classes.push('month-start');
        if (currentDate === daysInMonth) classes.push('month-end');
        
        const classString = classes.length > 0 ? `class="${classes.join(' ')}"` : '';
        const dateString = `${calendarYear}-${String(calendarMonth + 1).padStart(2, '0')}-${String(currentDate).padStart(2, '0')}`;
        
        let cellContent = currentDate;
        if (currentDate === 1) {
          cellContent += '<br><small style="font-size:0.6em;color:#059669;">POCZĄTEK</small>';
        } else if (currentDate === daysInMonth) {
          cellContent += '<br><small style="font-size:0.6em;color:#dc2626;">KONIEC</small>';
        }
        
        calHtml += `<td ${classString} data-date="${dateString}">${cellContent}</td>`;
        currentDate++;
      } else {
        // Dni z następnego miesiąca
        calHtml += `<td class="other-month">${nextMonthDate}</td>`;
        nextMonthDate++;
      }
    }
    
    calHtml += `</tr>`;
  }

  calHtml += `</table>`;
  
  calendarElement.innerHTML = calHtml;

  // Dodaj obsługę nawigacji
  const prevBtn = document.getElementById('calPrev');
  const nextBtn = document.getElementById('calNext');
  
  if (prevBtn) {
    prevBtn.onclick = function() {
      calendarMonth--;
      if (calendarMonth < 0) {
        calendarMonth = 11;
        calendarYear--;
      }
      renderCalendar();
    };
  }

  if (nextBtn) {
    nextBtn.onclick = function() {
      calendarMonth++;
      if (calendarMonth > 11) {
        calendarMonth = 0;
        calendarYear++;
      }
      renderCalendar();
    };
  }

  // Dodaj obsługę kliknięcia na dzień
  const dayElements = calendarElement.querySelectorAll('td[data-date]');
  dayElements.forEach(dayElement => {
    dayElement.onclick = function() {
      const selectedDate = this.getAttribute('data-date');
      onDateClick(selectedDate);
    };
  });
}

// Funkcja wywoływana przy kliknięciu na dzień
function onDateClick(dateString) {
  // Domyślnie przekieruj do widoku dnia obecności
  const currentPage = window.location.pathname.split('/').pop();
  
  // Jeśli nie jesteśmy już na stronie obecności, przekieruj
  if (currentPage !== 'attendance_day.html') {
    window.location.href = `attendance_day.html?date=${dateString}`;
  } else {
    // Jeśli już jesteśmy na stronie obecności, zaktualizuj datę
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
      dateInput.value = dateString;
      // Wywołaj funkcję ładowania danych jeśli istnieje
      if (typeof loadDayAttendance === 'function') {
        loadDayAttendance();
      }
    }
  }
}

// Automatyczne renderowanie kalendarza po załadowaniu DOM
document.addEventListener('DOMContentLoaded', function() {
  // Delay żeby upewnić się że sidebar jest załadowany
  setTimeout(() => {
    renderCalendar();
    setupCalendarExpansion();
  }, 100);
});

// Funkcja do obsługi rozwijania kalendarza
function setupCalendarExpansion() {
  const calendarTitle = document.getElementById('calendarTitle');
  const calendarWidget = document.getElementById('calendarWidget');
  const calendarOverlay = document.getElementById('calendarOverlay');
  
  if (!calendarTitle || !calendarWidget || !calendarOverlay) return;
  
  // Obsługa kliknięcia na tytuł kalendarza
  calendarTitle.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleCalendarExpansion();
  });
  
  // Obsługa kliknięcia na overlay
  calendarOverlay.addEventListener('click', function() {
    collapseCalendar();
  });
  
  // Obsługa klawisza ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isCalendarExpanded) {
      collapseCalendar();
    }
  });
}

function toggleCalendarExpansion() {
  if (isCalendarExpanded) {
    collapseCalendar();
  } else {
    expandCalendar();
  }
}

function expandCalendar() {
  const calendarWidget = document.getElementById('calendarWidget');
  const calendarOverlay = document.getElementById('calendarOverlay');
  
  if (!calendarWidget || !calendarOverlay) return;
  
  isCalendarExpanded = true;
  calendarWidget.classList.add('expanded');
  calendarOverlay.classList.add('active');
  
  // Dodaj informację o tym jak zamknąć
  const existingInfo = document.querySelector('.calendar-close-info');
  if (!existingInfo) {
    const closeInfo = document.createElement('div');
    closeInfo.className = 'calendar-close-info';
    closeInfo.style.cssText = `
      text-align: center;
      margin-top: 1rem;
      font-size: 0.8rem;
      color: #666;
    `;
    closeInfo.innerHTML = '<i class="fas fa-info-circle"></i> Kliknij poza kalendarzem lub naciśnij ESC aby zamknąć';
    calendarWidget.appendChild(closeInfo);
  }
  
  // Zablokuj przewijanie strony
  document.body.style.overflow = 'hidden';
}

function collapseCalendar() {
  const calendarWidget = document.getElementById('calendarWidget');
  const calendarOverlay = document.getElementById('calendarOverlay');
  
  if (!calendarWidget || !calendarOverlay) return;
  
  isCalendarExpanded = false;
  calendarWidget.classList.remove('expanded');
  calendarOverlay.classList.remove('active');
  
  // Usuń informację o zamykaniu
  const closeInfo = document.querySelector('.calendar-close-info');
  if (closeInfo) {
    closeInfo.remove();
  }
  
  // Przywróć przewijanie strony
  document.body.style.overflow = '';
}
