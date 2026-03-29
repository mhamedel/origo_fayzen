odoo.define('odoo_custom_login_inf.hide_help_links', [], function(require) {
    "use strict";
    document.addEventListener('DOMContentLoaded', function() {
        // Ensure body exists
        var targetNode = document.body;
        if (!targetNode) return;

        var observer = new MutationObserver(function(mutationsList) {
            mutationsList.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    // Check if the added node is the dropdown menu
                    if (node.classList && node.classList.contains('o-dropdown--menu')) {
                        // Dropdown created, hide help links
                        var docElements = node.querySelectorAll('.dropdown-item');
                        docElements.forEach(function(el) {
                            var menuName = el.getAttribute('data-menu');
                            if (menuName === 'documentation' || menuName === 'support' || menuName === 'shortcuts' || menuName === 'account') {
                                el.style.display = 'none';
                            }
                        });
                    }
                    // Also hide the mail systray dropdown if it appears
                   if (node.classList && node.classList.contains('o-mail-DiscussSystray-class')) {
                        node.style.display = 'none'; // hide the mail systray dropdown
                    }
                });
            });
        });

        // Observe the whole body for new nodes
        observer.observe(targetNode, { childList: true, subtree: true });
    });
});