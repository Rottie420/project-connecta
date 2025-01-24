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
      const response = await fetch('https://connecta.store/pet/' + controlNumber + '/prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userPrompt }),
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
      errorMessage.className = 'chat-message error';
    
      if (error instanceof TypeError) {
        // Handle TypeError (e.g., network issues, fetch call errors)
        errorMessage.textContent = 'Network error occurred. Please check your connection.';
      } else if (error.message.includes('HTTP error')) {
        // Handle HTTP errors explicitly
        const statusMatch = error.message.match(/Status: (\d+)/);
        const statusCode = statusMatch ? statusMatch[1] : 'unknown';
        errorMessage.textContent = `Server error (Status: ${statusCode}). Please try again later.`;
      } else if (error instanceof SyntaxError) {
        // Handle JSON parsing issues or unexpected responses
        errorMessage.textContent = 'Unexpected response from the server. Please contact support.';
      } else {
        // Generic fallback for any other errors
        errorMessage.textContent = 'An unknown error occurred. Please try again.';
      }
    
      // Append error message to chat history
      chatHistory.appendChild(errorMessage);
    
      // Optionally, alert the user for critical errors
      // alert('A critical error occurred. Please refresh the page.');
    }
     finally {
      scrollToBottom(); // Ensure scrolling happens regardless of success or error
    }
  });