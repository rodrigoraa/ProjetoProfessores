document.addEventListener('DOMContentLoaded', function() {
    const dlForm = document.getElementById('dlForm');
    const urlInput = document.querySelector('input[name="url"]');
    const btn = dlForm.querySelector('button');
    const loader = document.getElementById('loader');
    const status = document.getElementById('status');
    const preview = document.getElementById('preview');

    // 1. Lógica do Botão de Download com Progresso Real
    dlForm.onsubmit = function (e) {
        e.preventDefault(); // Impede a página de recarregar

        const url = urlInput.value;
        const format = document.querySelector('input[name="format"]:checked').value;

        btn.disabled = true;
        btn.innerText = "A preparar...";
        loader.style.display = 'block';
        status.style.display = 'block';
        status.style.color = "var(--text-muted)";
        status.innerText = "A iniciar download...";

        // Pede ao servidor para começar
        fetch('/start-download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, format: format })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                mostrarErro(data.error);
                return;
            }
            // Começa a perguntar o progresso
            acompanharProgresso(data.task_id);
        })
        .catch(err => mostrarErro("Erro de comunicação com o servidor."));
    };

    function acompanharProgresso(taskId) {
        const intervalo = setInterval(() => {
            fetch(`/progress/${taskId}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    clearInterval(intervalo);
                    mostrarErro(data.error);
                } else if (data.status === 'Concluído') {
                    clearInterval(intervalo);
                    status.innerText = "Concluído! O download vai iniciar...";
                    status.style.color = "#2e7d32"; // Cor verde
                    
                    // Força o navegador a baixar o ficheiro
                    window.location.href = `/get-file/${taskId}`;
                    
                    setTimeout(() => resetarFormulario(), 3000);
                } else {
                    // Atualiza o texto na tela (ex: "A transferir... 45%")
                    status.innerText = `${data.status} ${data.percent}`;
                }
            });
        }, 1000); // Pergunta a cada 1 segundo
    }

    function mostrarErro(mensagem) {
        status.innerText = "Erro: " + mensagem;
        status.style.color = "#c62828"; // Cor vermelha
        resetarFormulario(false);
    }

    function resetarFormulario(esconderStatus = true) {
        btn.disabled = false;
        btn.innerText = "Iniciar Download";
        loader.style.display = 'none';
        if (esconderStatus) {
            setTimeout(() => status.style.display = 'none', 5000);
        }
    }

    // 2. Busca Prévia do Vídeo (Thumbnail) - Mantido igual
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