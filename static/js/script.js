document.addEventListener('DOMContentLoaded', () => {
    // ---- Main Page Logic ----
    const analyzeBtn = document.querySelector('.btn-primary:not(.chat-input .btn-primary)'); // Exclude chatbot buttons if any
    const symptomInput = document.querySelector('.symptom-input-box textarea');

    if (analyzeBtn && symptomInput) {
        analyzeBtn.addEventListener('click', (e) => {
            // Check if this button is inside the contact form
            if (analyzeBtn.closest('.contact-form')) return;

            e.preventDefault();
            const symptoms = symptomInput.value.trim();
            if (!symptoms) {
                alert('Please describe your symptoms first.');
                return;
            }

            // Simulating analysis process
            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;

            // Hide previous results if any
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
                resultsContainer.style.opacity = '0';
            }

            // Real Prediction API call
            fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms: symptoms })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    if (resultsContainer) {
                        resultsContainer.style.display = 'flex';
                        // Trigger reflow
                        resultsContainer.offsetHeight;
                        resultsContainer.style.opacity = '1';

                        // Update UI with real prediction
                        const isUnknown = data.disease === "Unknown Condition";

                        document.getElementById('prediction-title').textContent = isUnknown ? "Result Uncertain" : data.disease;
                        document.getElementById('prediction-confidence').textContent = data.confidence;
                        document.getElementById('prediction-bar').style.width = data.confidence;

                        const descElement = document.getElementById('prediction-desc');
                        if (isUnknown) {
                            descElement.textContent = "Your symptoms don't clearly match any condition in our database. Please speak with a healthcare provider for an accurate diagnosis.";
                        } else {
                            descElement.textContent = `Based on your reported symptoms ("${data.original_input}"), the most likely condition is ${data.disease}.`;
                        }

                        // Update Meal Plan UI
                        const recovery = data.recovery;
                        document.querySelector('.meal-title').textContent = recovery.title;

                        // Render Tags
                        const tagsContainer = document.querySelector('.tags');
                        tagsContainer.innerHTML = recovery.tags.map(tag => `<span class="tag">${tag}</span>`).join('');

                        // Render Details List
                        const detailsList = document.querySelector('.meal-details');
                        detailsList.innerHTML = recovery.details.map(detail => `<li>${detail}</li>`).join('');


                        // Scroll to results
                        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert("Something went wrong with the prediction.");
                })
                .finally(() => {
                    analyzeBtn.textContent = 'Analyze Symptoms';
                    analyzeBtn.disabled = false;
                });
        });
    }

    // Add sticky navbar effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(8, 10, 16, 0.95)';
            navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';
        } else {
            navbar.style.background = 'transparent';
            navbar.style.boxShadow = 'none';
        }
    });

    // ---- Chatbot Logic ----
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    let userMessage = null; // Variable to store user's message
    const inputInitHeight = chatInput.scrollHeight;

    const createChatLi = (message, className) => {
        // Create a chat <li> element with passed message and className
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", `${className}`);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi; // return chat <li> element
    }

    const generateResponse = (chatElement) => {
        const messageElement = chatElement.querySelector("p");

        // Use Fetch API to call local backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage })
        }).then(response => response.json())
            .then(data => {
                messageElement.textContent = data.response;
            }).catch(() => {
                messageElement.textContent = "Oops! Something went wrong. Please try again.";
            }).finally(() => {
                chatbox.scrollTo(0, chatbox.scrollHeight);
            });
    }

    const handleChat = () => {
        userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
        if (!userMessage) return;

        // Clear the input textarea and set its height to default
        chatInput.value = "";
        chatInput.style.height = `${inputInitHeight}px`;

        // Append the user's message to the chatbox
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);

        setTimeout(() => {
            // Display "Thinking..." message while waiting for the response
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    chatInput.addEventListener("input", () => {
        // Adjust the height of the input textarea based on its content
        chatInput.style.height = `${inputInitHeight}px`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    chatInput.addEventListener("keydown", (e) => {
        // If Enter key is pressed without Shift key and the window 
        // width is greater than 800px, handle the chat
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    if (sendChatBtn) {
        sendChatBtn.addEventListener("click", handleChat);
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    }

    if (chatbotToggler) {
        chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
    }
});
