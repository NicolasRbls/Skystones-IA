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

# Tour actuel (AI ou PLAYER) - l'IA commence
current_turn = "AI"

game_over = False  # Indique si la partie est terminée

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
        pygame.draw.line(
            screen, BLACK,
            (0, 150 + x * CELL_SIZE),
            (GRID_SIZE * CELL_SIZE, 150 + x * CELL_SIZE),
            LINE_WIDTH
        )

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

# ===================== Dessin des lames =====================
def draw_card_lames(card, x, y):
    """Dessine les lames d'une carte (triangles successifs)."""
    blade_color = BLACK

    for i in range(card["top"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE // 2 - 10 + i * 10, y),
            (x + CARD_SIZE // 2 - 15 + i * 10, y + 15),
            (x + CARD_SIZE // 2 - 5 + i * 10, y + 15)
        ])
    for i in range(card["right"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE, y + CARD_SIZE // 2 - 10 + i * 10),
            (x + CARD_SIZE - 15, y + CARD_SIZE // 2 - 15 + i * 10),
            (x + CARD_SIZE - 15, y + CARD_SIZE // 2 - 5 + i * 10)
        ])
    for i in range(card["bottom"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE // 2 - 10 + i * 10, y + CARD_SIZE),
            (x + CARD_SIZE // 2 - 15 + i * 10, y + CARD_SIZE - 15),
            (x + CARD_SIZE // 2 - 5 + i * 10, y + CARD_SIZE - 15)
        ])
    for i in range(card["left"]):
        pygame.draw.polygon(screen, blade_color, [
            (x, y + CARD_SIZE // 2 - 10 + i * 10),
            (x + 15, y + CARD_SIZE // 2 - 15 + i * 10),
            (x + 15, y + CARD_SIZE // 2 - 5 + i * 10)
        ])

# ===================== Dessin des decks =====================
def draw_deck(deck, y, owner):
    """Dessine les cartes du deck (joueur ou IA), centrées horizontalement."""
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
    """Effet visuel lorsqu'une carte change de propriétaire."""
    x = col * CELL_SIZE + 25
    y = 150 + row * CELL_SIZE + 25

    for _ in range(3):
        pygame.draw.rect(screen, WHITE, (x, y, CARD_SIZE, CARD_SIZE))
        pygame.display.flip()
        pygame.time.delay(80)
        draw_board()
        pygame.display.flip()
        pygame.time.delay(80)

# ===================== Vérification bidirectionnelle =====================
def check_and_capture(row, col, nr, nc, placed_side, neighbor_side):
    """
    Vérifie et applique la capture dans les deux sens :
    - La carte (row,col) capture (nr,nc) si owners différents et placed_side > neighbor_side
    - La carte (nr,nc) capture (row,col) si owners différents et neighbor_side > placed_side
    """
    if board[row][col] is None or board[nr][nc] is None:
        return

    c1 = board[row][col]
    c2 = board[nr][nc]

    # Pas de capture si c'est le même propriétaire
    if c1["owner"] == c2["owner"]:
        return

    # c1 vs c2
    if c1[placed_side] > c2[neighbor_side]:
        c2["owner"] = c1["owner"]
        animate_capture(nr, nc)
    elif c2[neighbor_side] > c1[placed_side]:
        c1["owner"] = c2["owner"]
        animate_capture(row, col)

def capture_adjacent(row, col):
    """Compare la carte (row,col) avec ses voisines dans les deux sens."""
    neighbors = [
        (row - 1, col,    "bottom", "top"),    # Haut
        (row, col + 1,    "left",   "right"),  # Droite
        (row + 1, col,    "top",    "bottom"), # Bas
        (row, col - 1,    "right",  "left")    # Gauche
    ]
    for (nr, nc, side1, side2) in neighbors:
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            check_and_capture(row, col, nr, nc, side1, side2)

# ===================== Placement de carte =====================
def place_card(row, col, card, owner):
    """Place la carte (row,col) et déclenche la capture bidirectionnelle."""
    if board[row][col] is not None:
        return

    new_card = copy.deepcopy(card)
    new_card["owner"] = owner
    board[row][col] = new_card

    # Capture autour de la carte posée
    capture_adjacent(row, col)

# ===================== État du plateau =====================
def is_board_full():
    """Retourne True si le plateau est plein."""
    return all(cell is not None for row in board for cell in row)

# ===================== IA (Placement simple) =====================
def ai_play():
    """
    IA : pose la première carte du deck IA sur la première case vide.
    """
    global current_turn
    if ai_deck:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] is None:
                    card = ai_deck.pop(0)
                    place_card(r, c, card, "O")
                    current_turn = "PLAYER"
                    return

# ===================== Annonce du gagnant =====================
def announce_winner():
    """Affiche qui gagne ou égalité, puis attend 3s."""
    player_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "X")
    ai_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "O")

    if player_score > ai_score:
        winner_text = "Le Joueur (X) Gagne !"
    elif ai_score > player_score:
        winner_text = "L'IA (O) Gagne !"
    else:
        winner_text = "Match Nul !"

    text_surface = font.render(winner_text, True, BLACK)
    x_center = (WINDOW_WIDTH - text_surface.get_width()) // 2
    y_center = (WINDOW_HEIGHT - text_surface.get_height()) // 2
    screen.blit(text_surface, (x_center, y_center))
    pygame.display.flip()
    pygame.time.delay(3000)

# ===================== Boucle principale =====================
def main():
    global selected_card, current_turn, game_over

    running = True

    # Position des decks (évite chevauchement)
    ai_deck_y = 20
    player_deck_y = 650

    while running:
        screen.fill(WHITE)

        # Dessin de la grille et du plateau
        draw_grid()
        draw_board()

        # Dessin des decks
        draw_deck(ai_deck, ai_deck_y, "O")
        draw_deck(player_deck, player_deck_y, "X")

        # Tour de l'IA
        if current_turn == "AI" and not game_over:
            ai_play()
            if is_board_full():
                game_over = True
                announce_winner()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and current_turn == "PLAYER" and not game_over:
                mx, my = event.pos

                # Clique sur le deck joueur ?
                if player_deck_y <= my <= player_deck_y + CARD_SIZE:
                    deck_width = len(player_deck) * (CARD_SIZE + 10)
                    start_x = (WINDOW_WIDTH - deck_width) // 2
                    index = (mx - start_x) // (CARD_SIZE + 10)
                    if 0 <= index < len(player_deck):
                        selected_card = player_deck[index]

                # Clique sur le plateau ?
                elif 150 <= my <= 150 + GRID_SIZE * CELL_SIZE:
                    row = (my - 150) // CELL_SIZE
                    col = mx // CELL_SIZE
                    if selected_card and 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if board[row][col] is None:
                            player_deck.remove(selected_card)
                            place_card(row, col, selected_card, "X")
                            selected_card = None

                            if is_board_full():
                                game_over = True
                                announce_winner()
                            else:
                                current_turn = "AI"

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
