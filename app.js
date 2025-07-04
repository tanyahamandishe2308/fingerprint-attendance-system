document.addEventListener('DOMContentLoaded', () => {
    const enrollForm = document.querySelector('#enroll-form');
    const verifyForm = document.querySelector('#verify-form');

    if (enrollForm) {
        enrollForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const name = document.querySelector('#name').value;
            const surname = document.querySelector('#surname').value;

            const response = await fetch('/enroll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, surname })
            });

            const data = await response.json();
            alert(data.message);

            if (data.status === 'success') {
                enrollForm.reset(); // Clear the form after successful enrollment
            }
        });
    }

    if (verifyForm) {
        verifyForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const response = await fetch('/verify', { method: 'POST' });
            const data = await response.json();

            alert(data.message);
        });
    }
});
