document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('repoForm');
    const loadingContainer = document.getElementById('loadingContainer');
    const stepsList = document.getElementById('steps');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading container
        loadingContainer.style.display = 'block';
        
        // Clear previous steps
        stepsList.innerHTML = '';
        
        const steps = [
            'Fetching repository structure...',
            'Reading Java files...',
            'Analyzing code with GPT...',
            'Generating feedback...'
        ];
        
        let stepIndex = 0;
        const stepInterval = setInterval(function() {
            if (stepIndex < steps.length) {
                const li = document.createElement('li');
                li.textContent = steps[stepIndex];
                stepsList.appendChild(li);
                stepIndex++;
            } else {
                clearInterval(stepInterval);
                submitForm();
            }
        }, 1500);
    });

    function submitForm() {
        const formData = new FormData(form);
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingContainer.style.display = 'none';
            if (data.success) {
                // Display the feedback
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'feedback';
                feedbackDiv.innerHTML = data.feedback;
                document.body.appendChild(feedbackDiv);
            } else {
                // Display the error
                const errorP = document.createElement('p');
                errorP.className = 'error';
                errorP.textContent = data.error;
                document.body.appendChild(errorP);
            }
        })
        .catch(error => {
            loadingContainer.style.display = 'none';
            console.error('Error:', error);
            const errorP = document.createElement('p');
            errorP.className = 'error';
            errorP.textContent = 'An error occurred while processing your request.';
            document.body.appendChild(errorP);
        });
    }
});