import pygame
import sys
import random
import copy

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 700
GRID_SIZE = 3
CELL_SIZE = 150
CARD_SIZE = 100
LINE_WIDTH = 5

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
GREEN = (0, 255, 0)

# Initialisation de la fenêtre
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Skystones")

# Police pour le texte
font = pygame.font.Font(None, 36)

# Plateau de jeu
board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def generate_card():
    """Génère une carte avec des lames aléatoires."""
    return {
        "top": random.randint(1, 5),
        "right": random.randint(1, 5),
        "bottom": random.randint(1, 5),
        "left": random.randint(1, 5),
        "owner": None
    }

player_deck = [generate_card() for _ in range(4)]
ai_deck = [generate_card() for _ in range(5)]
selected_card = None
current_turn = "AI"
game_over = False

def draw_grid():
    """Dessine la grille 3x3."""
    for x in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x * CELL_SIZE, 150), (x * CELL_SIZE, 150 + GRID_SIZE * CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, 150 + x * CELL_SIZE), (GRID_SIZE * CELL_SIZE, 150 + x * CELL_SIZE), LINE_WIDTH)

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

def draw_card_lames(card, x, y):
    """Dessine les lames d'une carte."""
    blade_color = BLACK

    # Lame du haut
    for i in range(card["top"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE//2 - 10 + i*10, y),
            (x + CARD_SIZE//2 - 15 + i*10, y + 15),
            (x + CARD_SIZE//2 - 5 + i*10, y + 15)
        ])

    # Lame de droite
    for i in range(card["right"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE, y + CARD_SIZE//2 - 10 + i*10),
            (x + CARD_SIZE - 15, y + CARD_SIZE//2 - 15 + i*10),
            (x + CARD_SIZE - 15, y + CARD_SIZE//2 - 5 + i*10)
        ])

    # Lame du bas
    for i in range(card["bottom"]):
        pygame.draw.polygon(screen, blade_color, [
            (x + CARD_SIZE//2 - 10 + i*10, y + CARD_SIZE),
            (x + CARD_SIZE//2 - 15 + i*10, y + CARD_SIZE - 15),
            (x + CARD_SIZE//2 - 5 + i*10, y + CARD_SIZE - 15)
        ])

    # Lame de gauche
    for i in range(card["left"]):
        pygame.draw.polygon(screen, blade_color, [
            (x, y + CARD_SIZE//2 - 10 + i*10),
            (x + 15, y + CARD_SIZE//2 - 15 + i*10),
            (x + 15, y + CARD_SIZE//2 - 5 + i*10)
        ])

def draw_deck(deck, y):
    """Dessine les decks des joueurs."""
    start_x = (WINDOW_WIDTH - (len(deck) * (CARD_SIZE + 10))) // 2
    for i, card in enumerate(deck):
        card_x = start_x + i * (CARD_SIZE + 10)
        pygame.draw.rect(screen, LIGHT_GRAY, (card_x, y, CARD_SIZE, CARD_SIZE))
        draw_card_lames(card, card_x, y)
        if card == selected_card:
            pygame.draw.rect(screen, GREEN, (card_x, y, CARD_SIZE, CARD_SIZE), 3)

def capture_cards(row, col, card):
    """Capture les cartes adjacentes."""
    neighbors = [
        (row-1, col, "bottom", "top"),
        (row, col+1, "left", "right"),
        (row+1, col, "top", "bottom"),
        (row, col-1, "right", "left")
    ]

    for n_row, n_col, player_side, opponent_side in neighbors:
        if 0 <= n_row < GRID_SIZE and 0 <= n_col < GRID_SIZE:
            neighbor = board[n_row][n_col]
            if neighbor and neighbor["owner"] != card["owner"]:
                if card[player_side] > neighbor[opponent_side]:
                    neighbor["owner"] = card["owner"]

def place_card(row, col, card, owner):
    """Place une carte sur le plateau."""
    if board[row][col] is None:
        board[row][col] = copy.deepcopy(card)
        board[row][col]["owner"] = owner
        capture_cards(row, col, board[row][col])

def is_board_full():
    """Vérifie si le plateau est plein."""
    return all(cell is not None for row in board for cell in row)

def evaluate_state():
    """Évalue l'état actuel du jeu."""
    ai_score = 0
    player_score = 0
    for row in board:
        for cell in row:
            if cell:
                if cell["owner"] == "O":
                    ai_score += 1
                else:
                    player_score += 1
    return ai_score - player_score

def minimax(depth, alpha, beta, maximizing_player):
    """Algorithme Minimax avec élagage alpha-beta."""
    if depth == 0 or is_board_full():
        return evaluate_state()

    if maximizing_player:
        max_eval = -float('inf')
        for card in ai_deck:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if board[row][col] is None:
                        # Simuler le coup
                        original_board = copy.deepcopy(board)
                        ai_deck.remove(card)
                        place_card(row, col, card, "O")
                        evaluation = minimax(depth-1, alpha, beta, False)
                        ai_deck.append(card)
                        board[:] = original_board
                        
                        max_eval = max(max_eval, evaluation)
                        alpha = max(alpha, evaluation)
                        if beta <= alpha:
                            break
        return max_eval
    else:
        min_eval = float('inf')
        for card in player_deck:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if board[row][col] is None:
                        # Simuler le coup
                        original_board = copy.deepcopy(board)
                        player_deck.remove(card)
                        place_card(row, col, card, "X")
                        evaluation = minimax(depth-1, alpha, beta, True)
                        player_deck.append(card)
                        board[:] = original_board
                        
                        min_eval = min(min_eval, evaluation)
                        beta = min(beta, evaluation)
                        if beta <= alpha:
                            break
        return min_eval

def ai_play():
    """Joue le meilleur coup trouvé par Minimax."""
    global current_turn
    best_score = -float('inf')
    best_move = None

    for card in ai_deck:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board[row][col] is None:
                    # Simuler le coup
                    original_board = copy.deepcopy(board)
                    ai_deck.remove(card)
                    place_card(row, col, card, "O")
                    score = minimax(2, -float('inf'), float('inf'), False)
                    ai_deck.append(card)
                    board[:] = original_board

                    if score > best_score:
                        best_score = score
                        best_move = (card, row, col)

    if best_move:
        card, row, col = best_move
        ai_deck.remove(card)
        place_card(row, col, card, "O")
        current_turn = "PLAYER"

def show_game_over():
    """Affiche l'écran de fin de partie."""
    ai_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "O")
    player_score = sum(1 for row in board for cell in row if cell and cell["owner"] == "X")
    winner = "AI" if ai_score > player_score else "Player" if player_score > ai_score else "Tie"
    
    text = font.render(f"Game Over! {winner} wins!", True, BLACK)
    screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.wait(3000)

def main():
    global selected_card, current_turn, game_over
    running = True

    while running:
        screen.fill(WHITE)

        # Dessin des éléments
        draw_grid()
        draw_board()
        draw_deck(player_deck, 550)
        draw_deck(ai_deck, 20)

        # Surbrillance des cases disponibles
        if selected_card and not game_over:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if board[row][col] is None:
                        x = col * CELL_SIZE
                        y = 150 + row * CELL_SIZE
                        pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE), 3)

        # Gestion de l'IA
        if current_turn == "AI" and ai_deck and not game_over:
            ai_play()
            if is_board_full():
                game_over = True

        # Vérification fin de partie
        if is_board_full() and not game_over:
            game_over = True
            show_game_over()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and current_turn == "PLAYER" and not game_over:
                x, y = event.pos
                
                # Sélection de carte
                if 550 <= y <= 550 + CARD_SIZE:
                    start_x = (WINDOW_WIDTH - (len(player_deck) * (CARD_SIZE + 10))) // 2
                    index = (x - start_x) // (CARD_SIZE + 10)
                    if 0 <= index < len(player_deck):
                        selected_card = player_deck[index]
                
                # Placement de carte
                elif 150 <= y <= 150 + GRID_SIZE * CELL_SIZE:
                    row = (y - 150) // CELL_SIZE
                    col = x // CELL_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and selected_card:
                        if board[row][col] is None:
                            player_deck.remove(selected_card)
                            place_card(row, col, selected_card, "X")
                            selected_card = None
                            current_turn = "AI"
                            if is_board_full():
                                game_over = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()