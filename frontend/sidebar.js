const showSubmenu = document.getElementById('showSubmenu');
const submenuPanel = document.getElementById('submenuPanel');
if (showSubmenu && submenuPanel) {
  showSubmenu.onclick = function() {
    submenuPanel.classList.toggle('active');
    document.body.classList.toggle('submenu-open', submenuPanel.classList.contains('active'));
  };
  document.addEventListener('click', function(e) {
    if (!submenuPanel.contains(e.target) && e.target !== showSubmenu) {
      submenuPanel.classList.remove('active');
      document.body.classList.remove('submenu-open');
    }
  });
}
