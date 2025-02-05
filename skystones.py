import pygame
import sys
import random
import copy
import time

# ===================== Initialisation de Pygame =====================
pygame.init()

# ===================== Paramètres d'affichage =====================
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
GRID_SIZE = 3
CELL_SIZE = 150
CARD_SIZE = 100
LINE_WIDTH = 5

# ===================== Couleurs =====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)    # Couleur des cartes du joueur
RED = (255, 0, 0)     # Couleur des cartes de l'IA
GREEN = (0, 255, 0)   # Pour encadrer la sélection

# ===================== Création de la fenêtre =====================
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Skystones - IA et Joueur")

# ===================== Polices =====================
font = pygame.font.Font(None, 36)

# ===================== Plateau et decks =====================
board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def generate_card():
    """Génère une carte avec des lames aléatoires (1 à 5)."""
    return {
        "top": random.randint(1, 5),
        "right": random.randint(1, 5),
        "bottom": random.randint(1, 5),
        "left": random.randint(1, 5),
        "owner": None
    }

# Le joueur dispose de 4 cartes, l'IA de 5 cartes
player_deck = [generate_card() for _ in range(4)]
ai_deck = [generate_card() for _ in range(5)]

# Carte sélectionnée par le joueur
selected_card = None

# Tour actuel (IA ou PLAYER) - l'IA commence
current_turn = "AI"

game_over = False  # Indique si la partie est terminée
winner_text = ""   # Texte affiché à la fin de la partie

# ===================== Dessin de la grille =====================
def draw_grid():
    """Dessine la grille 3x3 au milieu de la fenêtre, de y=150 à y=600."""
    for x in range(1, GRID_SIZE):
        pygame.draw.line(
            screen, BLACK,
            (x * CELL_SIZE, 150),
            (x * CELL_SIZE, 150 + GRID_SIZE * CELL_SIZE),
            LINE_WIDTH
        )
    for y in range(1, GRID_SIZE):
        pygame.draw.line(
            screen, BLACK,
            (0, 150 + y * CELL_SIZE),
            (GRID_SIZE * CELL_SIZE, 150 + y * CELL_SIZE),
            LINE_WIDTH
        )

# ===================== Dessin des lames =====================
def draw_card_lames(card, x, y):
    """Dessine les lames d'une carte (représentées par des petits triangles)."""
    blade_color = BLACK

    # Lames du haut
    for i in range(card["top"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE // 2 - 10 + i * 10, y),
            (x + CARD_SIZE // 2 - 15 + i * 10, y + 15),
            (x + CARD_SIZE // 2 - 5 + i * 10, y + 15)
        ])
    # Lames de droite
    for i in range(card["right"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE, y + CARD_SIZE // 2 - 10 + i * 10),
            (x + CARD_SIZE - 15, y + CARD_SIZE // 2 - 15 + i * 10),
            (x + CARD_SIZE - 15, y + CARD_SIZE // 2 - 5 + i * 10)
        ])
    # Lames du bas
    for i in range(card["bottom"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE // 2 - 10 + i * 10, y + CARD_SIZE),
            (x + CARD_SIZE // 2 - 15 + i * 10, y + CARD_SIZE - 15),
            (x + CARD_SIZE // 2 - 5 + i * 10, y + CARD_SIZE - 15)
        ])
    # Lames de gauche
    for i in range(card["left"]):
        pygame.draw.polygon(screen, blade_color, [
            (x, y + CARD_SIZE // 2 - 10 + i * 10),
            (x + 15, y + CARD_SIZE // 2 - 15 + i * 10),
            (x + 15, y + CARD_SIZE // 2 - 5 + i * 10)
        ])

# ===================== Dessin du plateau =====================
def draw_board():
    """Dessine les cartes placées sur le plateau."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            card = board[row][col]
            x = col * CELL_SIZE
            y = 150 + row * CELL_SIZE
            if card:
                color = BLUE if card["owner"] == "X" else RED
                pygame.draw.rect(screen, color, (x + 25, y + 25, CARD_SIZE, CARD_SIZE))
                draw_card_lames(card, x + 25, y + 25)

# ===================== Dessin des decks =====================
def draw_deck(deck, y, owner):
    """
    Dessine les cartes du deck (joueur ou IA), centrées horizontalement.
    La couleur est définie par le paramètre 'owner'.
    """
    start_x = (WINDOW_WIDTH - (len(deck) * (CARD_SIZE + 10))) // 2
    deck_color = BLUE if owner == "X" else RED

    for i, card in enumerate(deck):
        card_x = start_x + i * (CARD_SIZE + 10)
        pygame.draw.rect(screen, deck_color, (card_x, y, CARD_SIZE, CARD_SIZE))
        draw_card_lames(card, card_x, y)
        # Encadrement vert si la carte est sélectionnée
        if card == selected_card:
            pygame.draw.rect(screen, GREEN, (card_x, y, CARD_SIZE, CARD_SIZE), 3)

# ===================== Animation de capture =====================
def animate_capture(row, col):
    """Animation simple lors du changement de propriétaire d'une carte."""
    x = col * CELL_SIZE + 25
    y = 150 + row * CELL_SIZE + 25

    for _ in range(3):
        pygame.draw.rect(screen, WHITE, (x, y, CARD_SIZE, CARD_SIZE))
        pygame.display.flip()
        pygame.time.delay(80)
        draw_board()
        pygame.display.flip()
        pygame.time.delay(80)

# ===================== Vérification et capture bidirectionnelle =====================
def check_and_capture(row, col, nr, nc, placed_side, neighbor_side):
    """
    Vérifie et applique la capture dans les deux sens :
      - La carte (row,col) capture (nr,nc) si son côté 'placed_side'
        est supérieur au côté 'neighbor_side' du voisin.
      - Sinon, si le voisin a une valeur supérieure, la carte (row,col) est capturée.
    """
    if board[row][col] is None or board[nr][nc] is None:
        return

    c1 = board[row][col]
    c2 = board[nr][nc]

    # Pas de capture si même propriétaire
    if c1["owner"] == c2["owner"]:
        return

    if c1[placed_side] > c2[neighbor_side]:
        c2["owner"] = c1["owner"]
        animate_capture(nr, nc)
    elif c2[neighbor_side] > c1[placed_side]:
        c1["owner"] = c2["owner"]
        animate_capture(row, col)

# ===================== Capture des cartes adjacentes =====================
def capture_adjacent(row, col):
    """
    Compare la carte (row,col) avec ses voisins adjacents.
    Les côtés comparés sont :
      - Haut : compare 'top' de la carte et 'bottom' du voisin.
      - Droite : compare 'right' et 'left'.
      - Bas : compare 'bottom' et 'top'.
      - Gauche : compare 'left' et 'right'.
    """
    neighbors = [
        (row - 1, col, "top", "bottom"),    # Haut
        (row, col + 1, "right", "left"),      # Droite
        (row + 1, col, "bottom", "top"),      # Bas
        (row, col - 1, "left", "right")       # Gauche
    ]
    for (nr, nc, placed_side, neighbor_side) in neighbors:
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            check_and_capture(row, col, nr, nc, placed_side, neighbor_side)

# ===================== Placement de carte =====================
def place_card(row, col, card, owner):
    """Place la carte sur le plateau et déclenche la vérification de capture."""
    if board[row][col] is not None:
        return

    new_card = copy.deepcopy(card)  # On copie pour ne pas modifier le deck
    new_card["owner"] = owner
    board[row][col] = new_card

    capture_adjacent(row, col)

# ===================== État du plateau =====================
def is_board_full():
    """Retourne True si toutes les cases du plateau sont occupées."""
    return all(cell is not None for row in board for cell in row)

# ===================== Annonce du gagnant =====================
def announce_winner():
    """Définit le vainqueur et passe en mode game_over."""
    global winner_text, game_over

    player_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "X")
    ai_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "O")

    if player_score > ai_score:
        winner_text = "Le Joueur (X) Gagne !"
    elif ai_score > player_score:
        winner_text = "L'IA (O) Gagne !"
    else:
        winner_text = "Match Nul !"

    game_over = True

# ===================== IA (Placement simple) =====================
def ai_play():
    global current_turn
    if ai_deck:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] is None:
                    card = ai_deck.pop(0)
                    place_card(r, c, card, "O")

                    pygame.display.flip()
                    pygame.time.delay(500)

                    if is_board_full():
                        announce_winner()
                        return

                    current_turn = "PLAYER"
                    return

# ===================== Réinitialisation de la partie =====================
def reset_game():
    """Réinitialise la partie pour rejouer."""
    global board, player_deck, ai_deck, selected_card, current_turn, game_over, winner_text
    board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    player_deck = [generate_card() for _ in range(4)]
    ai_deck = [generate_card() for _ in range(5)]
    selected_card = None
    current_turn = "AI"
    game_over = False
    winner_text = ""

# ===================== Bouton Rejouer =====================
def get_restart_button_rect():
    """Retourne le rectangle du bouton 'Rejouer' centré."""
    button_width = 150
    button_height = 50
    x = (WINDOW_WIDTH - button_width) // 2
    y = (WINDOW_HEIGHT // 2) + 10
    return pygame.Rect(x, y, button_width, button_height)

def draw_restart_button():
    """Dessine le bouton 'Rejouer'."""
    button_rect = get_restart_button_rect()
    pygame.draw.rect(screen, BLACK, button_rect)
    text = font.render("Rejouer", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

# ===================== Dessin du texte du gagnant =====================
def draw_winner_text():
    """Affiche le texte du vainqueur et le bouton 'Rejouer' en fin de partie."""
    if game_over:
        darken_screen()  # Assombrit l'écran avant d'afficher le texte
        text_surface = font.render(winner_text, True, GREEN)
        text_x = (WINDOW_WIDTH - text_surface.get_width()) // 2
        text_y = (WINDOW_HEIGHT // 2) - 70
        screen.blit(text_surface, (text_x, text_y))
        draw_restart_button()

# ===================== Assombrissement de l'écran =====================
def darken_screen():
    """Ajoute un voile gris semi-transparent sur l'écran pour faire ressortir le texte de fin."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Noir avec 70% d'opacité
    screen.blit(overlay, (0, 0))

# ===================== Boucle principale =====================
def main():
    global selected_card, current_turn, game_over

    running = True

    # Positions des decks (pour éviter les chevauchements)
    ai_deck_y = 20
    player_deck_y = 650

    while running:
        screen.fill(WHITE)

        # Affichage de la grille, du plateau et des decks
        draw_grid()
        draw_board()
        draw_deck(ai_deck, ai_deck_y, "O")
        draw_deck(player_deck, player_deck_y, "X")

        # Si la partie est terminée, on affiche le vainqueur et le bouton 'Rejouer'
        if game_over:
            draw_winner_text()

        # Tour de l'IA (si la partie n'est pas finie)
        if current_turn == "AI" and not game_over:
            pygame.time.delay(500)
            ai_play()
            if is_board_full():
                announce_winner()

        # Gestion des événements
        for event in pygame.event.get():
            # Si la partie est finie, vérifier le clic sur le bouton 'Rejouer'
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if get_restart_button_rect().collidepoint(event.pos):
                    reset_game()

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and current_turn == "PLAYER" and not game_over:
                mx, my = event.pos

                # Sélection dans le deck du joueur
                if player_deck_y <= my <= player_deck_y + CARD_SIZE:
                    deck_width = len(player_deck) * (CARD_SIZE + 10)
                    start_x = (WINDOW_WIDTH - deck_width) // 2
                    index = (mx - start_x) // (CARD_SIZE + 10)
                    if 0 <= index < len(player_deck):
                        selected_card = player_deck[index]

                # Placement sur le plateau
                elif 150 <= my <= 150 + GRID_SIZE * CELL_SIZE:
                    row = (my - 150) // CELL_SIZE
                    col = mx // CELL_SIZE
                    if selected_card and 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if board[row][col] is None:
                            player_deck.remove(selected_card)
                            place_card(row, col, selected_card, "X")
                            selected_card = None

                            if is_board_full():
                                announce_winner()
                            else:
                                current_turn = "AI"

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
