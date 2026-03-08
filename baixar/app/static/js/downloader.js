document.addEventListener('DOMContentLoaded', function() {
    const dlForm = document.getElementById('dlForm');
    const urlInput = document.querySelector('input[name="url"]');
    const btn = dlForm.querySelector('button');
    const loader = document.getElementById('loader');
    const status = document.getElementById('status');
    const preview = document.getElementById('preview');

    // 1. Lógica do Botão de Download
    dlForm.onsubmit = function () {
        btn.disabled = true;
        btn.innerText = "A processar...";
        loader.style.display = 'block';
        status.style.display = 'block';

        setTimeout(() => {
            btn.disabled = false;
            btn.innerText = "Iniciar Download";
        }, 30000);
    };

    // 2. Busca Prévia do Vídeo (Thumbnail)
    urlInput.addEventListener('blur', function () {
        const url = this.value;
        if (url.includes('youtube.com') || url.includes('youtu.be')) {
            fetch('/video-info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            })
            .then(res => res.json())
            .then(data => {
                if (data.title) {
                    preview.style.display = 'block';
                    document.getElementById('thumb').src = data.thumbnail;
                    document.getElementById('video-title').innerText = data.title;
                    document.getElementById('video-duration').innerText = "Duração: " + data.duration;
                }
            })
            .catch(err => console.error("Erro ao buscar info:", err));
        }
    });
});