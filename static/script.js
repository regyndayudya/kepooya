
function copyText(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    
    const textToCopy = element.href || element.innerText;

   
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

document.addEventListener('click', function (e) {
    const btn = e.target.closest('button');
    if (!btn) return;

 
    const sound = new Audio("/static/click.wav");
    sound.play().catch(err => console.log("Audio error"));

    
    if (btn.id === 'copyBtn') {
        e.preventDefault();
        setTimeout(() => { copyText('linkJawab'); }, 100);
    }

    
    const targetUrl = btn.getAttribute('data-url');
    if (targetUrl) {
        e.preventDefault();
        setTimeout(() => { window.location.assign(targetUrl); }, 400);
    }
});


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