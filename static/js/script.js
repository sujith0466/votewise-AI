document.addEventListener('DOMContentLoaded', () => {
    // 1. Voting Eligibility Checker
    const eligibilityForm = document.getElementById('eligibility-form');
    const eligibilityResult = document.getElementById('eligibility-result');

    if (eligibilityForm) {
        eligibilityForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const age = parseInt(document.getElementById('age').value, 10);
            const state = document.getElementById('state').value;
            
            eligibilityResult.classList.remove('hidden', 'bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800', 'border-green-200', 'border-red-200');
            eligibilityResult.classList.add('border');

            if (age >= 18) {
                eligibilityResult.classList.add('bg-green-100', 'text-green-800', 'border-green-200');
                eligibilityResult.innerHTML = `Great news! You are eligible to vote in ${state ? state : 'your state'}.<br>Next step: <a href="#process" class="underline font-semibold">Follow the registration process</a>.`;
            } else {
                eligibilityResult.classList.add('bg-red-100', 'text-red-800', 'border-red-200');
                eligibilityResult.textContent = `Sorry, you are not currently eligible to vote. You must be at least 18 years old.`;
            }
        });
    }

    // 2. Chatbot Logic
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const chatSubmitBtn = document.getElementById('chat-submit');

    // Disable send button if input is empty
    if (chatInput && chatSubmitBtn) {
        chatInput.addEventListener('input', () => {
            chatSubmitBtn.disabled = chatInput.value.trim() === '';
        });
        // Initial state
        chatSubmitBtn.disabled = chatInput.value.trim() === '';
    }

    function formatTime(date) {
        let hours = date.getHours();
        let minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return hours + ':' + minutes + ' ' + ampm;
    }

    function addMessage(message, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex items-start gap-3 fade-in ${isUser ? 'flex-row-reverse' : ''}`;
        
        const avatar = document.createElement('div');
        avatar.className = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs ${isUser ? 'bg-blue-600' : 'bg-gray-800'}`;
        avatar.textContent = isUser ? 'You' : 'AI';

        const bubbleContainer = document.createElement('div');
        bubbleContainer.className = `flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[85%]`;

        const bubble = document.createElement('div');
        bubble.className = `px-4 py-3 shadow-sm text-gray-800 whitespace-pre-wrap ${
            isUser 
            ? 'bg-blue-100 border border-blue-200 rounded-2xl rounded-tr-none text-right' 
            : 'bg-white border border-gray-200 rounded-2xl rounded-tl-none text-left'
        }`;
        bubble.textContent = message;

        const timestamp = document.createElement('span');
        timestamp.className = 'text-xs text-gray-400 mt-1';
        timestamp.textContent = formatTime(new Date());

        bubbleContainer.appendChild(bubble);
        bubbleContainer.appendChild(timestamp);

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubbleContainer);
        chatBox.appendChild(msgDiv);
        
        // Auto-scroll to latest message
        chatBox.scrollTop = chatBox.scrollHeight;
        return msgDiv;
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex items-start gap-3 fade-in typing-indicator-container`;
        msgDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs bg-gray-800`;
        avatar.textContent = 'AI';

        const bubble = document.createElement('div');
        bubble.className = `px-4 py-3 shadow-sm text-gray-500 italic bg-white border border-gray-200 rounded-2xl rounded-tl-none`;
        bubble.textContent = 'Typing...';

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        chatBox.appendChild(msgDiv);
        
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) return;

            // Disable input while processing
            chatInput.disabled = true;
            chatSubmitBtn.disabled = true;
            
            // Add user message to UI
            addMessage(message, true);
            chatInput.value = '';

            // Show typing indicator
            addTypingIndicator();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                
                // Remove typing indicator before adding actual message
                removeTypingIndicator();
                addMessage(data.response);
            } catch (error) {
                console.error('Chat error:', error);
                removeTypingIndicator();
                addMessage("I'm sorry, I'm having trouble connecting to my servers right now. Please try again later.");
            } finally {
                // Re-enable input
                chatInput.disabled = false;
                // Chat input is now empty, so keep submit disabled
                chatSubmitBtn.disabled = true; 
                chatInput.focus();
            }
        });
    }

    // Quick Reply Buttons Logic
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('quick-reply-btn')) {
            const text = e.target.textContent;
            if (chatInput) {
                chatInput.value = text;
                chatSubmitBtn.disabled = false;
                // Auto-submit the form
                chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            }
        }
    });

    // 3. Highlight active navbar section on scroll
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('nav a');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= (sectionTop - sectionHeight / 3)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('text-primary', 'font-bold');
            link.classList.add('text-gray-700');
            if (link.getAttribute('href').includes(current) && current !== '') {
                link.classList.remove('text-gray-700');
                link.classList.add('text-primary', 'font-bold');
            }
        });
    });

    // FORCE HARD FIX (GUARANTEED) to overcome aggressive browser HTML caching
    const dropdown = document.getElementById("state");
    if (dropdown) {
        dropdown.innerHTML = `
            <option value="" disabled selected>Select your state</option>
            <option value="Andhra Pradesh">Andhra Pradesh</option>
            <option value="Telangana">Telangana</option>
            <option value="Tamil Nadu">Tamil Nadu</option>
            <option value="Karnataka">Karnataka</option>
            <option value="Maharashtra">Maharashtra</option>
            <option value="Delhi</option>
            <option value="Odisha">Odisha</option>
            <option value="West Bengal">West Bengal</option>
        `;
    }
});
