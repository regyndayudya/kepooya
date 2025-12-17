// 1. Fungsi Utama Salin Teks
function copyText(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Ambil link dari href atau teks yang terlihat
    const textToCopy = element.href || element.innerText;

    // Metode cadangan menggunakan textarea (paling stabil untuk diklik berkali-kali)
    const tempInput = document.createElement('textarea');
    tempInput.value = textToCopy;
    document.body.appendChild(tempInput);
    tempInput.select();
    tempInput.setSelectionRange(0, 99999);

    try {
        document.execCommand('copy');
        alert("Link berhasil disalin! 📋");
    } catch (err) {
        console.error("Gagal menyalin", err);
    }
    document.body.removeChild(tempInput);
}

// 2. Event Listener Global untuk Suara & Navigasi
document.addEventListener('click', function (e) {
    const btn = e.target.closest('button');
    if (!btn) return;

    // Putar suara klik
    const sound = new Audio("/static/click.wav");
    sound.play().catch(err => console.log("Audio error"));

    // Logika Tombol Copy (ID harus copyBtn)
    if (btn.id === 'copyBtn') {
        e.preventDefault();
        setTimeout(() => { copyText('linkJawab'); }, 100);
    }

    // Logika Navigasi (Lihat Jawaban & Home)
    const targetUrl = btn.getAttribute('data-url');
    if (targetUrl) {
        e.preventDefault();
        setTimeout(() => { window.location.assign(targetUrl); }, 400);
    }
});

// 3. Logika Menangani Tombol Enter di Textarea
document.addEventListener('DOMContentLoaded', function() {
    const buatForm = document.getElementById('buatForm');
    const buatTextarea = document.querySelector('#buatForm textarea'); 

    if (buatTextarea && buatForm) {
        buatTextarea.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') { 
                event.preventDefault(); 
                buatForm.submit(); 
            }
        });
    }
});