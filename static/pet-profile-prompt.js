// Function to scroll chat history to the bottom
function scrollToBottom() {
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.scrollTop = chatHistory.scrollHeight; // Always scroll to the latest content
  }

  // Function for typing effect (letter by letter, super fast)
  function typeText(element, text, speed) {
    let index = 0;
    element.innerHTML = ''; // Clear existing content if any
    const chatHistory = document.getElementById('chatHistory'); // Reference to chat history
    const interval = setInterval(() => {
      if (index < text.length) {
        if (text.charAt(index) === '\n') {
          element.innerHTML += '<br>'; // Insert a <br> for line breaks
        } else {
          element.innerHTML += text.charAt(index); // Add each character
        }
        index++;
        scrollToBottom(); // Scroll to the bottom with each new character
      } else {
        clearInterval(interval); // Stop interval after typing completes
      }
    }, speed); // Speed set for typing delay per character
  }

  document.getElementById('promptForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const userPrompt = document.getElementById('userPrompt').value.trim();
    const chatHistory = document.getElementById('chatHistory');
    const urlParts = window.location.pathname.split('/');
    const controlNumber = urlParts[urlParts.length - 2];

    if (!userPrompt) {
      console.warn('The user prompt is empty');
      return;
    }

    // User message (appears instantly)
    const userMessage = document.createElement('div');
    userMessage.className = 'chat-message user';
    userMessage.textContent = userPrompt;
    chatHistory.appendChild(userMessage);
    scrollToBottom();

    try {
      const response = await fetch(`/pet/${controlNumber}/prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userPrompt })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const result = await response.json();
      if (result && result.response) {
        const aiMessage = document.createElement('div');
        aiMessage.className = 'chat-message';

        let responseText = result.response.trim();
        responseText = responseText.replace(/\*\*/g, ''); // Remove '**' symbols

        if (responseText.includes('*')) {
          const lines = responseText.split('\n');
          let formattedResponse = '';

          lines.forEach(line => {
            if (line.startsWith('*')) {
              formattedResponse += `• ${line.replace('*', '').trim()}\n`; // Using bullet points as plain text
            } else {
              formattedResponse += `${line.trim()}\n`; // Regular text
            }
          });

          aiMessage.textContent = formattedResponse.trim();
        } else {
          aiMessage.textContent = responseText.replace(/\n/g, '\n'); // Maintain line breaks
        }

        chatHistory.appendChild(aiMessage);
        typeText(aiMessage, aiMessage.textContent, 3); // Typing speed set to 3ms per character
      } else {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'chat-message error';
        errorMessage.textContent = 'Error: Unexpected response from server.';
        chatHistory.appendChild(errorMessage);
      }

      document.getElementById('userPrompt').value = '';
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = document.createElement('div');
      errorMessage.className = 'chat-message';
      errorMessage.textContent = 'An error occurred. Please try again.';
      chatHistory.appendChild(errorMessage);
    } finally {
      scrollToBottom(); // Ensure scrolling happens regardless of success or error
    }
  });