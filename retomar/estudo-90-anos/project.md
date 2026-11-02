# Diário — "estudo dos idosos de 90 anos" (videos/estudo-90-anos)

**Pedido:** link do Drive + print do estudo ("High-intensity strength training in nonagenarians", Fiatarone et al., JAMA 1990): "Eu falo do estudo dos idosos de 90 anos, aí você coloca essa foto, que é o estudo."
**Plano aprovado** ("Ok"). Pergunta sobre o @ (no vídeo anterior ele pediu sem) ficou sem resposta: usei o padrão, com @.
**Sessão:** o PR #12 (vídeo 5) ainda não estava no `main`; trabalhei a partir da branch dele, que tem as peças novas.
**Cortes:** fala limpa numa tomada; 22 pausas de 0,12–0,5 s saíram. O `ajustar_cortes.py` empurrou o início do 2º trecho para antes do fim do 1º (sobreposição em "60, 70"); juntei trechos que se sobrepõem ou ficam a < 0,1 s. "com as próprias as pernas" era erro do Whisper: transcrevendo o trecho sozinho, ele ouve "com as próprias pernas". Transcrição do cortado: 161 palavras, nenhuma comida.
**Cor:** o `grade` do vídeo 5 (teto e janela do carro menos estourados, pele quente) com `brightness` 0.
**Clipes:** Mixkit bloqueou a busca (Cloudflare), mas o download por número funciona. Reaproveitei aprovados (229071 gancho, 12866 levantar, 365401 casal, 302441 esqueleto, coxa em corte). O agachamento com barra 148204 virou um close das costas de uma moça jovem em tela cheia: troquei pelo esqueleto (tela cheia) e pus o agachamento com elástico (Mixkit 21273) no "fabricando o próprio remédio". O recorte das cápsulas foi corrigido para mostrá-las (trecho do começo, à esquerda).
**Estudo:** o resultado do artigo é +174% de força em 8 semanas; o título diz "quase 3× mais força" (o que ele fala) e "+174% em 8 semanas".
**Entrega:** `estudo_90_anos.mp4`, 52,7 s, -14,0 LUFS, pico -1,4 dBTP, 26,9 MB. Quadro 0 com o gancho inteiro.
**Pedido 2:** "Troque essa imagem que mostra o esqueleto fazendo exercício. Tô achando muito ruim… coloca uma pessoa fazendo exercício." Pixabay e Mixkit só têm gente jovem treinando força; escolhi o Mixkit 4506 (homem adulto comum com kettlebell, não fisiculturista), trecho 6,9 s para o peso subir no "força". Ficou em cartão (720p esticado para tela cheia ficaria borrado), `tv --brilho 1.45` (academia escura). Entrega `estudo_90_anos_v2.mp4`: -14,0 LUFS, pico -1,4 dBTP, 26,9 MB.
**Pendente:** retorno do usuário sobre o vídeo e sobre o @ daqui pra frente.
