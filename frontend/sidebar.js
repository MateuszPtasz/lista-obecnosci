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
      if (configSubmenuPanel) {
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
      if (submenuPanel) {
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
      if (submenuPanel) {
        submenuPanel.classList.remove('active');
        const arrow = showSubmenu?.querySelector('.fa-chevron-right');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
      if (configSubmenuPanel) {
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
  
  // Zamknij submenu przy kliknięciu poza nim
  document.addEventListener('click', function(e) {
    // Zamknij submenu obecności
    if (submenuPanel && !submenuPanel.contains(e.target) && !showSubmenu?.contains(e.target)) {
      submenuPanel.classList.remove('active');
      const arrow = showSubmenu?.querySelector('.fa-chevron-right');
      if (arrow) {
        arrow.style.transform = 'rotate(0deg)';
      }
    }
    
    // Zamknij submenu konfiguracji
    if (configSubmenuPanel && !configSubmenuPanel.contains(e.target) && !showConfigSubmenu?.contains(e.target)) {
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
});
