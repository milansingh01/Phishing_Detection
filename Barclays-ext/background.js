// Service Worker for Universal Site Blocking
let cache = {};

chrome.webNavigation.onCommitted.addListener(async (details) => {
    // Only check main frame navigation (not iframes)
    if (details.frameId !== 0) return;
    
    const url = details.url;
    
    // Skip internal chrome/extension pages
    if (url.startsWith('chrome://') || url.startsWith('chrome-extension://')) return;
    
    // Check local cache first to avoid repeating API calls for the same tab/domain rapidly
    if (cache[url] && cache[url].isDangerous) {
         injectBlocker(details.tabId, cache[url].reason);
         return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8001/api/check_site', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.is_dangerous) {
                cache[url] = { isDangerous: true, reason: result.reason };
                injectBlocker(details.tabId, result.reason);
            } else {
                cache[url] = { isDangerous: false };
            }
        }
    } catch (e) {
        console.error("Barclays Extension: Backend URL check failed.", e);
    }
});

function injectBlocker(tabId, reason) {
    chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: (blockedReason) => {
            // Un-bypassable blocker screen creation
            if (document.getElementById("barclays-hard-blocker")) return;
            
            const blocker = document.createElement("div");
            blocker.id = "barclays-hard-blocker";
            blocker.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background-color: #0f172a; color: white;
                z-index: 2147483647; display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                backdrop-filter: blur(10px); text-align: center; padding: 20px;
            `;
            
            // Try resolving the logo URL within the extension context
            const logoUrl = chrome.runtime.getURL("barclays.png");
            
            blocker.innerHTML = `
                <div style="background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 12px; padding: 40px; max-width: 600px; box-shadow: 0 25px 50px -12px rgba(220, 38, 38, 0.25);">
                    <img src="${logoUrl}" alt="Barclays Logo" style="height: 50px; margin-bottom: 20px; filter: brightness(0) invert(1);">
                    <h1 style="color: #ef4444; font-size: 28px; margin: 0 0 15px 0;">ACCESS BLOCKED</h1>
                    <h3 style="color: #f87171; margin: 0 0 20px 0;">Security Violation Detected</h3>
                    <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                        ${blockedReason}
                    </p>
                    <div style="background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; margin-bottom: 30px; font-family: monospace; font-size: 12px; color: #94a3b8; word-break: break-all;">
                        Restricted URL: ${window.location.href}
                    </div>
                    
                    <button id="barclays-back-btn" style="background: #0ea5e9; color: white; border: none; padding: 12px 24px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                        Go Back To Safety
                    </button>
                    
                    <div style="margin-top: 20px;">
                        <a href="#" id="barclays-bypass-btn" style="color: #475569; font-size: 12px; text-decoration: underline; cursor: pointer;">
                            Continue anyway (Not Recommended - Activity will be logged)
                        </a>
                    </div>
                </div>
            `;
            
            document.body.appendChild(blocker);
            document.body.style.overflow = "hidden"; // Prevent scrolling
            
            document.getElementById("barclays-back-btn").addEventListener("click", () => {
                window.history.back();
                // If history is empty, close tab
                setTimeout(() => { if(window.history.length <= 1) window.close(); }, 100);
            });
            
            document.getElementById("barclays-bypass-btn").addEventListener("click", (e) => {
                e.preventDefault();
                blocker.remove();
                document.body.style.overflow = "auto";
            });
        },
        args: [reason]
    });
}
