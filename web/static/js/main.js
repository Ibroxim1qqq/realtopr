document.getElementById('requestForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = "Yuborilmoqda...";
    submitBtn.disabled = true;

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('successModal').style.display = 'flex';
            this.reset();
        } else {
            alert('Xatolik yuz berdi: ' + (result.detail || 'Noma\'lum xatolik'));
        }
    } catch (error) {
        alert('Internet bilan aloqa yo\'q yoki server ishlamayapti.');
        console.error(error);
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});

function closeModal() {
    document.getElementById('successModal').style.display = 'none';
}
