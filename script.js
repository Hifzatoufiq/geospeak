async function generateText() {
    const prompt = document.getElementById('prompt').value;
    const resultDiv = document.getElementById('result');
    
    if (!prompt) {
        resultDiv.textContent = 'Please enter a prompt.';
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        resultDiv.textContent = data.text;
    } catch (error) {
        resultDiv.textContent = 'Error generating text: ' + error.message;
    }
}

async function fetchHistory() {
    const historyDiv = document.getElementById('history');
    
    try {
        const response = await fetch('http://localhost:5000/history');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        historyDiv.innerHTML = '<h2>History</h2>';
        data.history.forEach(entry => {
            historyDiv.innerHTML += `<p><strong>Prompt:</strong> ${entry[1]}<br><strong>Response:</strong> ${entry[2]}</p>`;
        });
    } catch (error) {
        historyDiv.textContent = 'Error fetching history: ' + error.message;
    }
}
