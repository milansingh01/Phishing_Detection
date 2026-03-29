// Aggressive detection for Gmail
let lastEmailId = '';

function detectEmail() {
    // Check if we are in an email view by looking for the subject line
    const subjectEl = document.querySelector('h2.hP');
    if (!subjectEl || !subjectEl.textContent) return;

    const subjectText = subjectEl.textContent.trim();
    if (subjectText === lastEmailId) return; // Already analyzed this email
    
    lastEmailId = subjectText;
    console.log('Barclays Detector: Analysis Triggered for Subject:', subjectText);

    // Extraction
    const bodyText = document.querySelector('.ii.gt, .a3s')?.innerText || '';
    
    // Advanced Attachment & Image Detection
    let attachmentsArr = [];
    
    // 1. Search for actual Downloadable attachments
    const downloadLinks = document.querySelectorAll('a[download], [aria-label*="Attachment"], .vI, .aYw, .hq, .a8X, .a78, .Xv, [role="listitem"]');
    downloadLinks.forEach(el => {
        let name = el.getAttribute('download') || el.innerText.trim();
        // Fallback for aria-label "Attachment: filename.pdf"
        if (!name && el.getAttribute('aria-label')) {
            const aria = el.getAttribute('aria-label');
            if (aria.includes("Attachment")) name = aria.replace("Attachment:", "").trim();
        }
        if (name && name.length > 3 && name.includes('.') && !attachmentsArr.includes(name)) {
            attachmentsArr.push(name);
        }
    });

    // 2. Explicitly search for inline Images 
    const images = document.querySelectorAll('img[src*="googleusercontent"], img[alt*="image"]');
    images.forEach((img, idx) => {
        let currentExt = "image_file.png";
        if (img.src.includes(".jpg")) currentExt = `inline_image_${idx}.jpg`;
        else if (img.src.includes(".gif")) currentExt = `inline_image_${idx}.gif`;
        if (!attachmentsArr.includes(currentExt)) {
            attachmentsArr.push(currentExt);
        }
    });

    // Language
    let lang = "English";
    if (bodyText.match(/[अ-ह]/)) lang = "Hindi";
    else if (bodyText.match(/[\u3040-\u309f\u30a0-\u30ff]/)) lang = "Japanese";

    // Sender
    const senderNode = document.querySelector('.gD');
    const sender = senderNode ? (senderNode.getAttribute('email') || senderNode.innerText) : "Unknown Extracted";

    const result = {
        subject: subjectText,
        body: bodyText.substring(0, 300),
        attachments: attachmentsArr.length > 0 ? attachmentsArr.join(", ") : "None",
        lang: lang,
        sender: sender
    };

    // Save to local storage for Popup
    try {
        if (!chrome.runtime?.id) throw new Error("Extension context invalidated");
        
        chrome.storage.local.set({ lastEmail: result }, () => {
            console.log('Barclays Detector: Data Stored Successfully');
        });
    } catch (e) {
        if (e.message.includes("context invalidated") || e.message.includes("Extension context invalidated")) {
            console.warn("Barclays Detector: Extension was updated. Stopping old orphaned script.");
            if (window.pollInterval) clearInterval(window.pollInterval);
            return; // stop execution
        }
    }

    // Automatically send to Backend for Fraud Team Dashboard independently of Popup state
    fetch('http://127.0.0.1:8001/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
    }).then(async res => {
          if (!res.ok) {
              const errText = await res.text();
              throw new Error(`HTTP error! status: ${res.status}, response: ${errText}`);
          }
          return res.json();
    }).then(data => {
          window.lastAnalyzedStatus = data.predicted_label;
          window.lastAnalyzedFlags = data.flags || {};
          console.log("Barclays Detector: Backend Analysis Complete:", data.predicted_label);
          showBanner(data);
    }).catch(err => {
          console.error("Barclays Detector: Backend connection failed", err);
    });

    // Also send message to update popup UI if it happens to be open
    try {
        const messagePromise = chrome.runtime.sendMessage({ type: 'EMAIL_DETECTED', data: result, analysis: null });
        if (messagePromise && typeof messagePromise.catch === 'function') {
            messagePromise.catch(() => {});
        }
    } catch (err) {}
}

function showBanner(analysis) {
    let oldBanner = document.getElementById("barclays-security-banner");
    if (oldBanner) oldBanner.remove();

    const banner = document.createElement("div");
    banner.id = "barclays-security-banner";
    
    // Style depending on fraud or safe
    const isFraud = analysis.predicted_label === "Phishing";
    const bgColor = isFraud ? "#f8d7da" : "#d1e7dd";
    const textColor = isFraud ? "#842029" : "#0f5132";
    const borderColor = isFraud ? "#f5c2c7" : "#badbcc";
    const icon = isFraud ? "⚠️ CRITICAL PHISHING RISK" : "✅ VERIFIED LEGITIMATE";

    banner.style.cssText = `
        background-color: ${bgColor};
        color: ${textColor};
        border: 1px solid ${borderColor};
        padding: 12px 20px;
        margin: 10px 20px;
        border-radius: 8px;
        font-family: 'Google Sans', Roboto, sans-serif;
        font-size: 14px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 9999;
    `;

    banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
           <img src="${chrome.runtime.getURL("barclays.png")}" style="height: 24px; object-fit: contain;">
           <span>${icon}: ${analysis.explanation || 'Analyzed by Barclays Fraud Team'}</span>
        </div>
        ${isFraud && analysis.flags.credential_leaks ? `<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">CREDENTIALS LEAKED</span>` : ''}
    `;

    // Try finding the subject header container in Gmail
    const headerEl = document.querySelector('.ha'); 
    if (headerEl) {
        headerEl.parentElement.insertBefore(banner, headerEl);
    } else {
        // Fallback to top of screen if specific Gmail class isn't found
        banner.style.position = "fixed";
        banner.style.top = "10px";
        banner.style.left = "50%";
        banner.style.transform = "translateX(-50%)";
        document.body.appendChild(banner);
    }
}

// Poll for changes (more reliable than MutationObserver on some versions)
window.pollInterval = setInterval(detectEmail, 1500);

// Run on page interaction
document.addEventListener('click', () => setTimeout(detectEmail, 500));

// --- NEW FEATURE: INTERCEPT DANGEROUS ATTACHMENT CLICKS IN GMAIL ---
document.body.addEventListener('click', (e) => {
    // If the click is on an attachment icon, a download button, or an inline image
    const isAttachmentClick = e.target.closest('a[download], [aria-label*="Attachment"], .vI, .aYw, .hq, .a8X, .a78, .Xv, img[src*="googleusercontent"], img[alt*="image"]');
    
    if (isAttachmentClick && window.lastAnalyzedStatus === "Phishing") {
        if (window.lastAnalyzedFlags && window.lastAnalyzedFlags.malicious_executable) {
            e.preventDefault();
            e.stopPropagation();
            alert("🛑 BARCLAYS SECURITY BLOCK: This attachment was positively identified as a malicious executable capable of installing hidden malware. Download explicitly blocked.");
        } else {
            // General phishing attachment warning
            const proceed = confirm("⚠️ BARCLAYS SECURITY WARNING: The AI has flagged this entire email as Phishing. Opening this attachment or image may expose you to credential smuggling or spyware.\n\nAre you absolutely sure you want to open it?");
            if (!proceed) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    }
}, true); // Use capture phase to ensure we intercept it BEFORE Gmail's custom handlers trigger

