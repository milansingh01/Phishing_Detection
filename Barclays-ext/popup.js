document.addEventListener('DOMContentLoaded', () => {
    const statusText = document.getElementById('statusText');
    const resultSection = document.getElementById('resultSection');
    const resultTitle = document.getElementById('resultTitle');
    const resultDesc = document.getElementById('resultDesc');
    const safeIcon = document.getElementById('safeIcon');
    const spamIcon = document.getElementById('spamIcon');
    const emailPreview = document.getElementById('emailPreview');
    const securityInsights = document.getElementById('securityInsights');
    const attachmentTypes = document.getElementById('attachmentTypes');
    const languageDetected = document.getElementById('languageDetected');
    const reasoningText = document.getElementById('reasoningText');
    const credentialStatus = document.getElementById('credentialStatus');
    const historyList = document.getElementById('historyList');

    // Load initial history
    chrome.storage.local.get({ scanHistory: [] }, (res) => {
        renderHistory(res.scanHistory);
    });

    // 1. Pull data directly from the active Gmail tab
    async function pullEmailData() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab || !tab.url.includes('mail.google.com')) {
            statusText.textContent = "Please use Gmail";
            return;
        }

        // Execute a script on the fly to get Gmail data (more reliable than waiting for messages)
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const subject = document.querySelector('h2.hP')?.innerText || document.title.split(' - ')[0] || '';
                const body = document.querySelector('.ii.gt, .a3s')?.innerText || '';
                const attachmentContainers = document.querySelectorAll('.aYw, .hq, .a8X, .a78, .Xv, [role="listitem"]');
                
                let attachments = [];
                attachmentContainers.forEach(el => {
                   const txt = el.innerText.trim();
                   if (txt && txt.length > 3 && !attachments.includes(txt) && txt.includes('.')) attachments.push(txt);
                });

                let lang = "English";
                if (body.match(/[अ-ह]/)) lang = "Hindi";
                else if (body.match(/[\u3040-\u309f\u30a0-\u30ff]/)) lang = "Japanese";

                const senderNode = document.querySelector('.gD');
                const sender = senderNode ? (senderNode.getAttribute('email') || senderNode.innerText) : "Unknown Extracted";

                return { subject, body: body.substring(0, 500), attachments: attachments.join(", "), lang, sender };
            }
        }, async (results) => {
            if (results && results[0] && results[0].result) {
                const data = results[0].result;
                
                // Set loading state
                statusText.textContent = "Analyzing email content...";
                reasoningText.textContent = "Computing AI inference...";
                
                try {
                    const response = await fetch('http://localhost:8000/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        const analysisData = await response.json();
                        updateUI(data, analysisData);
                    } else {
                        statusText.textContent = "Backend analysis failed.";
                        updateUI(data, null);
                    }
                } catch (e) {
                    console.error("Backend connection failed", e);
                    statusText.textContent = "Backend disconnected.";
                    updateUI(data, null);
                }
            }
        });
    }

    function updateUI(data, analysis) {
        if (!data.subject || data.subject.includes('Gmail')) {
            statusText.textContent = "Select an email to start";
            return;
        }

        // Fill Preview
        emailPreview.innerHTML = `
            <div style="text-align: left; width: 100%;">
                <strong style="color: #64748b; font-size: 10px; text-transform: uppercase;">Current Email</strong> 
                <p style="margin: 4px 0 0 0; font-size: 11px; font-weight: 700; color: #001e3c;">${data.subject}</p>
            </div>
        `;

        // Fill Insights
        securityInsights.classList.remove('hidden');
        attachmentTypes.textContent = data.attachments || "None Found";
        languageDetected.textContent = data.lang || "English";
        
        // Final UI Updates
        resultSection.classList.remove('hidden');
        resultTitle.textContent = "Security Metadata";
        resultDesc.textContent = "Gmail parameters extracted successfully.";

        if (analysis) {
            statusText.textContent = `Analysis Complete - ${analysis.predicted_label}`;
            reasoningText.textContent = analysis.explanation;
            
            if (analysis.flags && analysis.flags.credential_leaks) {
                credentialStatus.textContent = `Leaked: ${analysis.flags.credential_leaks.join(', ')}`;
                credentialStatus.style.color = "red";
            } else {
                credentialStatus.textContent = "No credentials exposed.";
            }

            if (analysis.predicted_label === "Phishing") {
                resultSection.className = "result-card spam";
                safeIcon.classList.add('hidden');
                spamIcon.classList.remove('hidden');
                resultTitle.textContent = "Critical Risk Detected";
                resultDesc.textContent = `Confidence: ${analysis.confidence_score}%`;
            } else {
                resultSection.className = "result-card safe";
                safeIcon.classList.remove('hidden');
                spamIcon.classList.add('hidden');
                resultTitle.textContent = "Email appears Legitimate";
                resultDesc.textContent = `Confidence: ${analysis.confidence_score}%`;
            }

        } else {
            reasoningText.textContent = "Backend model analysis failed or disconnected.";
            credentialStatus.textContent = "Unknown";
            resultSection.className = "result-card warning";
        }

        // Save to History List if valid analysis
        if (analysis && data.subject) {
            chrome.storage.local.get({ scanHistory: [] }, (res) => {
                let historyArray = res.scanHistory;
                const timeString = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                const newItem = {
                    time: "Today, " + timeString,
                    subject: data.subject.substring(0, 20),
                    isFraud: analysis.predicted_label === "Phishing"
                };
                
                // Avoid logging duplicates sequentially
                if (historyArray.length === 0 || historyArray[0].subject !== newItem.subject) {
                    historyArray.unshift(newItem);
                    if (historyArray.length > 3) historyArray.pop(); // keep last 3
                    chrome.storage.local.set({ scanHistory: historyArray });
                    renderHistory(historyArray);
                }
            });
        }
    }

    function renderHistory(historyArray) {
        if (!historyList) return;
        historyList.innerHTML = '';
        if (!historyArray || historyArray.length === 0) {
            historyList.innerHTML = '<span style="font-size:11px; color:#94a3b8; padding-left:5px;">No recent scans yet.</span>';
            return;
        }
        
        historyArray.forEach(item => {
            const statusClass = item.isFraud ? 'spam' : 'safe';
            const statusText = item.isFraud ? 'Phishing' : 'Legitimate';
            historyList.innerHTML += `
                <div class="history-item">
                    <span class="history-date">${item.time} - ${item.subject}</span>
                    <span class="history-status ${statusClass}">${statusText}</span>
                </div>
            `;
        });
    }

    // Auto-pull on open
    pullEmailData();
});
