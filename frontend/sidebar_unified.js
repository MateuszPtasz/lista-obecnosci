// Ulepszony skrypt obsługi sidebar - kompatybilny z ujednoliconym designem

document.addEventListener('DOMContentLoaded', function() {
  // Obsługa submenu obecności
  const showSubmenu = document.getElementById('showSubmenu');
  const submenuPanel = document.getElementById('submenuPanel');
  
  if (showSubmenu && submenuPanel) {
    showSubmenu.onclick = function(e) {
      e.preventDefault();
      submenuPanel.classList.toggle('active');
      
      // Zamknij inne submenu
      const configSubmenuPanel = document.getElementById('configSubmenuPanel');
      const securitySubmenuPanel = document.getElementById('securitySubmenuPanel');
      if (configSubmenuPanel && !configSubmenuPanel.classList.contains('keep-open')) {
        configSubmenuPanel.classList.remove('active');
        const configArrow = document.getElementById('showConfigSubmenu')?.querySelector('.fa-chevron-right');
        if (configArrow) configArrow.style.transform = 'rotate(0deg)';
      }
      if (securitySubmenuPanel) {
        securitySubmenuPanel.classList.remove('active');
        const securityArrow = document.getElementById('showSecuritySubmenu')?.querySelector('.fa-chevron-right');
        if (securityArrow) securityArrow.style.transform = 'rotate(0deg)';
      }
      
      // Obróć strzałkę
      const arrow = showSubmenu.querySelector('.fa-chevron-right');
      if (arrow) {
        arrow.style.transform = submenuPanel.classList.contains('active') ? 'rotate(90deg)' : 'rotate(0deg)';
      }
    };
  }

  // Obsługa submenu konfiguracji
  const showConfigSubmenu = document.getElementById('showConfigSubmenu');
  const configSubmenuPanel = document.getElementById('configSubmenuPanel');
  
  if (showConfigSubmenu && configSubmenuPanel) {
    showConfigSubmenu.onclick = function(e) {
      e.preventDefault();
      configSubmenuPanel.classList.toggle('active');
      
      // Zamknij inne submenu
      if (submenuPanel && !submenuPanel.classList.contains('keep-open')) {
        submenuPanel.classList.remove('active');
        const arrow = showSubmenu?.querySelector('.fa-chevron-right');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
      const securitySubmenuPanel = document.getElementById('securitySubmenuPanel');
      if (securitySubmenuPanel) {
        securitySubmenuPanel.classList.remove('active');
        const securityArrow = document.getElementById('showSecuritySubmenu')?.querySelector('.fa-chevron-right');
        if (securityArrow) securityArrow.style.transform = 'rotate(0deg)';
      }
      
      // Obróć strzałkę
      const configArrow = showConfigSubmenu.querySelector('.fa-chevron-right');
      if (configArrow) {
        configArrow.style.transform = configSubmenuPanel.classList.contains('active') ? 'rotate(90deg)' : 'rotate(0deg)';
      }
    };
  }

  // Obsługa submenu bezpieczeństwa
  const showSecuritySubmenu = document.getElementById('showSecuritySubmenu');
  const securitySubmenuPanel = document.getElementById('securitySubmenuPanel');
  
  if (showSecuritySubmenu && securitySubmenuPanel) {
    showSecuritySubmenu.onclick = function(e) {
      e.preventDefault();
      securitySubmenuPanel.classList.toggle('active');
      
      // Zamknij inne submenu
      if (submenuPanel && !submenuPanel.classList.contains('keep-open')) {
        submenuPanel.classList.remove('active');
        const arrow = showSubmenu?.querySelector('.fa-chevron-right');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
      if (configSubmenuPanel && !configSubmenuPanel.classList.contains('keep-open')) {
        configSubmenuPanel.classList.remove('active');
        const configArrow = document.getElementById('showConfigSubmenu')?.querySelector('.fa-chevron-right');
        if (configArrow) configArrow.style.transform = 'rotate(0deg)';
      }
      
      // Obróć strzałkę
      const securityArrow = showSecuritySubmenu.querySelector('.fa-chevron-right');
      if (securityArrow) {
        securityArrow.style.transform = securitySubmenuPanel.classList.contains('active') ? 'rotate(90deg)' : 'rotate(0deg)';
      }
    };
  }
  
  // Obsługa przycisku mobilnej nawigacji
  const mobileToggle = document.querySelector('.mobile-toggle');
  const sidebar = document.querySelector('.sidebar');
  
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', function() {
      sidebar.classList.toggle('active');
      this.classList.toggle('active');
    });
  }
  
  // Zamknij sidebar na mobilce po kliknięciu w treść
  const content = document.querySelector('.content');
  if (content && sidebar) {
    content.addEventListener('click', function() {
      if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        if (mobileToggle) mobileToggle.classList.remove('active');
      }
    });
  }
  
  // Dodaj przycisk hamburger menu dla widoku mobilnego jeśli go nie ma
  if (!mobileToggle) {
    const toggle = document.createElement('button');
    toggle.className = 'mobile-toggle';
    toggle.innerHTML = '<i class="fas fa-bars"></i>';
    document.body.appendChild(toggle);
    
    toggle.addEventListener('click', function() {
      if (sidebar) {
        sidebar.classList.toggle('active');
        this.classList.toggle('active');
      }
    });
  }
  
  // Zamknij submenu przy kliknięciu poza nim
  document.addEventListener('click', function(e) {
    // Zamknij submenu obecności
    if (submenuPanel && !submenuPanel.contains(e.target) && !showSubmenu?.contains(e.target) && !submenuPanel.classList.contains('keep-open')) {
      submenuPanel.classList.remove('active');
      const arrow = showSubmenu?.querySelector('.fa-chevron-right');
      if (arrow) {
        arrow.style.transform = 'rotate(0deg)';
      }
    }
    
    // Zamknij submenu konfiguracji
    if (configSubmenuPanel && !configSubmenuPanel.contains(e.target) && !showConfigSubmenu?.contains(e.target) && !configSubmenuPanel.classList.contains('keep-open')) {
      configSubmenuPanel.classList.remove('active');
      const configArrow = showConfigSubmenu?.querySelector('.fa-chevron-right');
      if (configArrow) {
        configArrow.style.transform = 'rotate(0deg)';
      }
    }

    // Zamknij submenu bezpieczeństwa
    if (securitySubmenuPanel && !securitySubmenuPanel.contains(e.target) && !showSecuritySubmenu?.contains(e.target)) {
      securitySubmenuPanel.classList.remove('active');
      const securityArrow = showSecuritySubmenu?.querySelector('.fa-chevron-right');
      if (securityArrow) {
        securityArrow.style.transform = 'rotate(0deg)';
      }
    }
  });
  
  // Podświetlenie aktywnej strony w menu na podstawie URL
  function highlightActiveMenu() {
    const currentPath = window.location.pathname;
    const fileName = currentPath.split('/').pop();
    
    // Wyczyść wszystkie aktywne klasy
    document.querySelectorAll('.sidebar a').forEach(link => {
      link.classList.remove('active');
    });
    
    // Znajdź i oznacz aktywny link
    document.querySelectorAll('.sidebar a').forEach(link => {
      const linkHref = link.getAttribute('href');
      if (linkHref && (linkHref === fileName || currentPath.includes(linkHref))) {
        link.classList.add('active');
        
        // Jeśli to link w submenu, otwórz submenu
        const parentPanel = link.closest('#submenuPanel, #configSubmenuPanel, #securitySubmenuPanel');
        if (parentPanel) {
          parentPanel.classList.add('active');
          parentPanel.classList.add('keep-open');
          
          // Obróć strzałkę dla odpowiedniego menu
          let menuButton;
          let arrowIcon;
          
          if (parentPanel.id === 'submenuPanel') {
            menuButton = document.getElementById('showSubmenu');
          } else if (parentPanel.id === 'configSubmenuPanel') {
            menuButton = document.getElementById('showConfigSubmenu');
          } else if (parentPanel.id === 'securitySubmenuPanel') {
            menuButton = document.getElementById('showSecuritySubmenu');
          }
          
          if (menuButton) {
            arrowIcon = menuButton.querySelector('.fa-chevron-right');
            if (arrowIcon) {
              arrowIcon.style.transform = 'rotate(90deg)';
            }
          }
        }
      }
    });
  }
  
  // Aktywuj podświetlanie menu
  highlightActiveMenu();
});
