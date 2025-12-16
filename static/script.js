let kodeGlobal = '';
let keyGlobal = '';

function buatPertanyaan() {
  let tanya = document.getElementById('tanyaInput').value.trim();
  if (!tanya) return alert('Pertanyaan tidak boleh kosong!');
  kodeGlobal = Math.random().toString(36).substring(2, 7); // ID unik untuk pertanyaan
  keyGlobal = Math.random().toString(36).substring(2, 10); // ID unik untuk key jawaban
  
  // Mengarahkan ke halaman share dengan link untuk menjawab
  let link = `${window.location.origin}/jawab/${kodeGlobal}`;
  document.getElementById('linkJawab').innerText = link;
  document.getElementById('linkJawab').href = link;
  
  // Redirect ke halaman share
  window.location.href = `${window.location.origin}share/${kodeGlobal}`;
}

function copyText(elementId) {
  const element = document.getElementById(elementId);
  
  if (!element) {
    alert ("Gagal menyalin: Elemen link tidak ditemukan.");
        return; 
  }
  
  const textToCopy = element.href;

  if (navigator.clipboard) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert("Link berhasil disalin: " + textToCopy);
            return;
        }).catch(err => {
            console.warn('Gagal menggunakan Clipboard API, mencoba metode fallback.', err);
        });
    }

    try {
        // Buat elemen teks sementara
        const tempInput = document.createElement('textarea');
        tempInput.value = textToCopy;
        document.body.appendChild(tempInput);
        
        // Pilih teks
        tempInput.select();
        tempInput.setSelectionRange(0, 99999); // Untuk mobile
        
        // Eksekusi perintah salin (Bisa diblokir di browser baru)
        document.execCommand('copy');
        
        document.body.removeChild(tempInput);
        alert("Link berhasil disalin (melalui fallback): " + textToCopy);

    } catch (err) {
        console.error('Gagal menyalin:', err);
        alert('Gagal menyalin link secara otomatis. Silakan salin URL ini secara manual: ' + textToCopy);
    }
}

function kirimJawaban() {
  const questionId = document.getElementById('questionId').value;
  let jwb = document.getElementById('jawabanInput').value.trim();

  if (!jwb) return alert('Jawaban tidak boleh kosong!');
  if (!questionId) return alert('Error: ID Pertanyaan tidak ditemukan.');

  fetch(`/jawab/${questionId}`, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'jawabanInput': jwb
        })
    }).then(response => {
        if (response.ok) {
          const card = document.querySelector('.card');
          card.innerHTML = `
                <h2>Terima Kasih!</h2>
                <p>Jawaban Anda telah tersimpan dan siap dilihat oleh pembuat pertanyaan.</p>
                
                <button class="btn-gray" onclick="location.href='/home'">Kembali ke Home</button>
                
                <button class="btn-pink" onclick="location.href='/home'">Lanjut ke Beranda</button>
            `;
            } else {
            alert('Gagal menyimpan jawaban. Silakan coba lagi.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    });
        }

document.addEventListener('DOMContentLoaded', function() {
    // Logika untuk Buat Pertanyaan (/buat)
    const buatForm = document.getElementById('buatForm');
    // Cari textarea di dalam form tersebut
    const buatTextarea = document.querySelector('#buatForm textarea'); 

    if (buatTextarea && buatForm) {
        buatTextarea.addEventListener('keydown', function(event) {
            // Cek jika tombol yang ditekan adalah Enter (keyCode 13)
            if (event.keyCode === 13) { 

                // Mencegah aksi default (membuat baris baru)
                event.preventDefault(); 

                // Mengirim form secara paksa
                buatForm.submit(); 
            }
        });
    }

    // Catatan: Untuk halaman /jawab, skrip ini biasanya TIDAK diperlukan 
    // karena formulir HTML standar seharusnya sudah otomatis bekerja.
});