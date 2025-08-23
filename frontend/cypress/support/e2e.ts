// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "./commands";

// Disable animations and transitions to prevent flakiness with Radix/shadcn components
beforeEach(() => {
  cy.window().then((win) => {
    const s = win.document.createElement("style");
    s.innerHTML = `
      *, *:before, *:after { 
        transition: none !important; 
        animation: none !important; 
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
      
      /* Super aggressive targeting of Radix elements */
      [data-state="open"], [data-state="closed"],
      [data-state="open"] *, [data-state="closed"] *,
      [data-radix-select-content], [data-radix-select-item],
      [role="listbox"], [role="option"],
      [id^="radix-"], [class*="radix-"] { 
        animation: none !important;
        transition: none !important;
        opacity: 1 !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
        pointer-events: auto !important;
      }
      
      /* Target all possible animation classes with wildcard matching */
      [class*="animate"], [class*="fade"], [class*="zoom"], [class*="slide"] {
        animation: none !important;
        transition: none !important;
        opacity: 1 !important;
        transform: none !important;
        visibility: visible !important;
      }
      
      /* Extremely specific targeting for the problematic element */
      div[id^="radix-"][class*="data-[state=open]:animate-in"] {
        opacity: 1 !important;
        visibility: visible !important;
        transform: none !important;
        animation: none !important;
        transition: none !important;
        display: block !important;
        pointer-events: auto !important;
      }
      
      /* Override any CSS custom properties that might affect animations */
      :root {
        --radix-select-content-transform-origin: center !important;
        --radix-select-content-available-height: auto !important;
      }
    `;
    win.document.head.appendChild(s);

    // Also add a mutation observer to force styles on dynamically created elements
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof Element) {
            // Force styles on any new Radix elements
            if (
              node.id?.startsWith("radix-") ||
              node.getAttribute("role") === "listbox" ||
              node.getAttribute("data-state")
            ) {
              (node as HTMLElement).style.setProperty(
                "opacity",
                "1",
                "important"
              );
              (node as HTMLElement).style.setProperty(
                "visibility",
                "visible",
                "important"
              );
              (node as HTMLElement).style.setProperty(
                "animation",
                "none",
                "important"
              );
              (node as HTMLElement).style.setProperty(
                "transition",
                "none",
                "important"
              );
            }
          }
        });
      });
    });

    observer.observe(win.document.body, {
      childList: true,
      subtree: true,
    });
  });
});
