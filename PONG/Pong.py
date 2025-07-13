import pygame
import sys
import random
import os

pygame.init()

# Caminhos
BASE_DIR = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

# Tela
largura, altura = 1366, 640
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pong")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# Fonte
fonte = pygame.font.Font(None, 60)
fonte_menor = pygame.font.Font(None, 40)

# Sons
pong_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "pong_hit.wav"))
score_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "score.wav"))

# Estados
MENU = "menu"
JOGO = "jogo"
VITORIA = "vitoria"
estado = MENU

# Placar
pontos1, pontos2 = 0, 0
limite_pontos = 5

# Velocidade da IA
velocidade_ia = 5  # Quanto menor, mais suave (mas mais lenta)

# Inicializar variáveis do jogo
def inicializar_jogo():
    global raquete1_y, raquete2_y, bola_x, bola_y
    global bola_vel_x, bola_vel_y, pontos1, pontos2
    raquete1_y = altura // 2 - 50
    raquete2_y = altura // 2 - 50
    bola_x = largura // 2
    bola_y = altura // 2
    bola_vel_x = random.choice([-15, 15])
    bola_vel_y = random.choice([-15, 15])
    pontos1, pontos2 = 0, 0

# Botões do menu
def desenhar_botao(texto, x, y, largura_b, altura_b, mouse_pos):
    cor = (100, 100, 100) if pygame.Rect(x, y, largura_b, altura_b).collidepoint(mouse_pos) else (60, 60, 60)
    pygame.draw.rect(tela, cor, (x, y, largura_b, altura_b))
    texto_render = fonte_menor.render(texto, True, BRANCO)
    tela.blit(texto_render, (x + (largura_b - texto_render.get_width()) // 2, y + 10))
    return pygame.Rect(x, y, largura_b, altura_b)

# Tela de vitória
def mostrar_vitoria(vencedor):
    tela.fill(PRETO)
    msg = fonte.render(f"{vencedor} venceu!", True, BRANCO)
    restart = fonte_menor.render("Pressione ENTER para jogar novamente", True, BRANCO)
    tela.blit(msg, (largura // 2 - msg.get_width() // 2, 200))
    tela.blit(restart, (largura // 2 - restart.get_width() // 2, 300))
    pygame.display.flip()

# Inicializar
clock = pygame.time.Clock()
inicializar_jogo()

# Loop principal
while True:
    if estado == MENU:
        mouse = pygame.mouse.get_pos()
        tela.fill(PRETO)
        titulo = fonte.render("PONG", True, BRANCO)
        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, 150))

        botao_jogar = desenhar_botao("Jogar", largura//2 - 150, 280, 300, 50, mouse)
        botao_sair = desenhar_botao("Sair", largura//2 - 150, 350, 300, 50, mouse)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(event.pos):
                    estado = JOGO
                    inicializar_jogo()
                elif botao_sair.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    elif estado == JOGO:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Entrada
        mouse_y = pygame.mouse.get_pos()[1]
        raquete1_y = mouse_y - 50
        raquete1_y = max(0, min(altura - 100, raquete1_y))

        # IA com previsão + erro mínimo + movimento suave
        if bola_vel_x > 0 and bola_x > largura // 2:
            tempo_colisao = (largura - 2 - bola_x) / bola_vel_x
            posicao_futura = bola_y + bola_vel_y * tempo_colisao

            # Reflete em caso de quique
            while posicao_futura < 0 or posicao_futura > altura:
                if posicao_futura < 0:
                    posicao_futura = -posicao_futura
                elif posicao_futura > altura:
                    posicao_futura = 2 * altura - posicao_futura

            erro = random.randint(-2, 2)  # Remova o erro aleatório para evitar tremor
            alvo = int(posicao_futura - 50 + erro)
            alvo = max(0, min(altura - 100, alvo))

            # Movimento suave: só move se estiver fora da tolerância
            tolerancia = 2
            if abs(raquete2_y - alvo) > tolerancia:
                if raquete2_y < alvo:
                    raquete2_y += min(velocidade_ia, alvo - raquete2_y)
                elif raquete2_y > alvo:
                    raquete2_y -= min(velocidade_ia, raquete2_y - alvo)

        # Movimento da bola
        bola_x += bola_vel_x
        bola_y += bola_vel_y

        # Colisão com topo/baixo
        if bola_y <= 0 or bola_y >= altura - 20:
            bola_vel_y *= -1

        # Colisão com raquetes
        if bola_x <= 20 and raquete1_y < bola_y < raquete1_y + 100:
            bola_x = 21  # Move a bola para fora da raquete
            bola_vel_x *= -1
            pong_sound.play()
        elif bola_x >= largura - 30 and raquete2_y < bola_y < raquete2_y + 100:
            bola_x = largura - 31  # Move a bola para fora da raquete
            bola_vel_x *= -1
            pong_sound.play()

        # Pontuação
        if bola_x < 0:
            pontos2 += 1
            score_sound.play()
            bola_x, bola_y = largura // 2, altura // 2
            bola_vel_x = -15
            bola_vel_y = random.choice([-15, 15])

        if bola_x > largura:
            pontos1 += 1
            score_sound.play()
            bola_x, bola_y = largura // 2, altura // 2
            bola_vel_x = 15
            bola_vel_y = random.choice([-15, 15])

        # Vitória
        if pontos1 >= limite_pontos:
            estado = VITORIA
            vencedor = "Você"
        elif pontos2 >= limite_pontos:
            estado = VITORIA
            vencedor = "IA"

        # Desenho
        tela.fill(PRETO)
        pygame.draw.rect(tela, BRANCO, (10, raquete1_y, 10, 100))
        pygame.draw.rect(tela, BRANCO, (largura - 20, raquete2_y, 10, 100))
        pygame.draw.ellipse(tela, BRANCO, (bola_x, bola_y, 20, 20))
        pygame.draw.aaline(tela, BRANCO, (largura // 2, 0), (largura // 2, altura))
        placar = fonte.render(f"{pontos1}  {pontos2}", True, BRANCO)
        tela.blit(placar, (largura // 2 - placar.get_width() // 2, 20))
        pygame.display.flip()
        clock.tick(60)

    elif estado == VITORIA:
        mostrar_vitoria(vencedor)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_RETURN]:
            estado = MENU
