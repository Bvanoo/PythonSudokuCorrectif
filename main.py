import curses   # bibliothèque standard pour piloter le terminal (clavier + écran)
import random   # pour mélanger les chiffres et varier les grilles


"""
SUDOKU EN TERMINAL - Correction guidée pas à pas

On sépare la LOGIQUE du jeu (étapes 1 à 3) de l'AFFICHAGE
et des ENTRÉES CLAVIER (étapes 4 et 5).

Pourquoi ? Parce qu'on peut tester la logique sans écran, et changer
l'interface (web, graphique...) sans toucher aux règles.

Représentation choisie : une grille = liste de 9 lignes de 9 entiers.
    board[ligne][colonne], et 0 signifie "case vide".
"""


# ==============================================================================
# ÉTAPE 1 : LA GRILLE ET LES RÈGLES
# ==============================================================================


def create_empty_board():
    """Crée une grille 9x9 remplie de 0."""
    # Compréhension de liste imbriquée : on crée 9 listes DISTINCTES.
    return [[0 for _ in range(9)] for _ in range(9)]


def is_valid(board, row, col, num):
    """Check 'num' en (row, col) valide (règles sudoku) ?"""
    # Règle 1 : pas deux fois le même chiffre sur la ligne.
    for x in range(9):
        if board[row][x] == num:
            return False

    # Règle 2 : pas deux fois le même chiffre sur la colonne.
    for x in range(9):
        if board[x][col] == num:
            return False

    # Règle 3 : pas deux fois le même chiffre dans le bloc 3x3.
    # La division entière (//) donne le numéro du bloc (0, 1 ou 2),
    # multiplié par 3 on retrouve la ligne/colonne du coin haut-gauche.
    # Ex : row = 7 -> 7 // 3 = 2 -> start_row = 6
    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


# ==============================================================================
# ÉTAPE 2 : GÉNÉRER UN PUZZLE
# Fabrication d'une grille complète ensuite suppresion de certaines cases ( pas de grille impossible verification simplifiée)
# ==============================================================================


def fill_grid_backtracking(board):
    """Remplit la grille par backtracking (essai / erreur / retour en arrière)."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # on cherche la première case vide

                # On mélange 1..9 pour que chaque partie soit différente.
                # Sans shuffle, on obtiendrait toujours la même grille.
                numbers = list(range(1, 10))
                random.shuffle(numbers)

                for num in numbers:
                    if is_valid(board, row, col, num):
                        board[row][col] = num              # 1. on essaie
                        if fill_grid_backtracking(board):  # 2. on continue (récursion)
                            return True
                        board[row][col] = 0                # 3. impasse : on annule (backtrack)

                # Aucun chiffre ne convient : on remonte d'un cran pour que
                # l'appel précédent essaie un autre chiffre.
                return False

    # Aucune case vide trouvée : la grille est complète.
    return True


def generate_puzzle(empty_cells=40):
    """Génère une grille complète, puis vide 'empty_cells' cases au hasard.
       Retourne : (puzzle à jouer, solution, masque des cases d'origine)."""

    full_board = create_empty_board()
    fill_grid_backtracking(full_board)

    # IMPORTANT : [row[:] for row in ...] fait une COPIE de chaque ligne.
    # Écrire puzzle = full_board ne copierait rien : effacer des cases du
    # puzzle effacerait aussi la solution.
    puzzle = [row[:] for row in full_board]

    removed = 0
    while removed < empty_cells:
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        if puzzle[r][c] != 0:  # on ne compte que les cases réellement vidées
            puzzle[r][c] = 0
            removed += 1

    # Masque : True = case donnée au départ, que le joueur ne doit pas modifier.
    # On le calcule APRÈS le retrait : une case non vide à ce stade est d'origine.
    original_mask = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]

    return puzzle, full_board, original_mask

    # Cette méthode ne garantit pas que le puzzle n'a qu'UNE seule solution (les vrais générateurs le vérifient).


# ==============================================================================
# ÉTAPE 3 : DÉTECTER LA VICTOIRE
# ==============================================================================


def check_victory(current_board, solution):
    """True si la grille du joueur est identique à la solution."""
    # On compare à la solution stockée plutôt que de revalider les règles :
    # c'est plus simple. Contrepartie : si le puzzle avait plusieurs
    # solutions, une réponse valide mais différente serait refusée.
    for r in range(9):
        for c in range(9):
            if current_board[r][c] != solution[r][c]:
                return False
    return True


# ==============================================================================
# ÉTAPE 4 : L'AFFICHAGE
# Cette fonction ne fait que DESSINER. Elle ne modifie jamais
# l'état du jeu, ce qui évite des bugs difficiles à retrouver.
# ==============================================================================


def draw_grid(stdscr, board, cursor_r, cursor_c, original_mask, message=""):
    """Dessine toute la grille, le curseur et le message de statut."""
    # curses ne redessine pas tout seul : on efface puis on réécrit à chaque tour.
    stdscr.clear()

    max_y, max_x = stdscr.getmaxyx()  # taille actuelle du terminal

    # Écrire hors de l'écran fait planter curses : on vérifie la taille d'abord.
    if max_y < 22 or max_x < 65:
        try:
            stdscr.addstr(0, 0, "Veuillez agrandir la fenêtre du terminal !")
        except curses.error:
            pass
        stdscr.refresh()
        return

    def safe_addstr(y, x, string, attr=curses.A_NORMAL):
        """addstr protégé : ignore silencieusement ce qui sortirait de l'écran."""
        if y < max_y and x + len(string) < max_x:
            try:
                stdscr.addstr(y, x, string, attr)
            except curses.error:
                pass

    # --- En-tête : rappel des commandes ---
    safe_addstr(0, 0, "=== SUDOKU ===", curses.A_BOLD)
    safe_addstr(1, 0, "Flèches: Se déplacer | 1-9: Insérer | Suppr/Backspace: Effacer")
    safe_addstr(2, 0, "Touches 'v': Vérifier la case | 'c': Correction complète | 'q': Quitter")

    # --- Plateau ---
    for r in range(9):
        # Position écran de la ligne r : on part de la ligne 4 et on ajoute
        # (r // 3) pour décaler d'une ligne à chaque bloc : c'est la place
        # de la ligne séparatrice "+-------+".
        row_y = 4 + r + (r // 3)

        if r % 3 == 0:  # avant chaque bloc de 3 lignes : séparateur horizontal
            safe_addstr(row_y - 1, 0, "+-------+-------+-------+")

        safe_addstr(row_y, 0, "| ")

        col_x = 2  # position écran de la colonne courante
        for c in range(9):
            # "." plutôt que "0" : une case vide est plus lisible à l'écran.
            val_str = str(board[r][c]) if board[r][c] != 0 else "."

            # Style : le curseur prime sur le gras des cases d'origine.
            attr = curses.A_NORMAL
            if r == cursor_r and c == cursor_c:
                attr = curses.A_REVERSE  # inversion des couleurs = surlignage
            elif original_mask[r][c]:
                attr = curses.A_BOLD     # cases d'origine en gras

            safe_addstr(row_y, col_x, val_str, attr)
            col_x += 2  # un chiffre + un espace

            if (c + 1) % 3 == 0:  # fin d'un bloc : séparateur vertical
                safe_addstr(row_y, col_x, "| ")
                col_x += 2

    # Dernière ligne du cadre (4 + 9 lignes + 2 séparateurs intermédiaires + 1).
    safe_addstr(16, 0, "+-------+-------+-------+")

    # --- Message de statut (retour d'information au joueur) ---
    if message:
        safe_addstr(18, 0, f"Info : {message}", curses.A_BOLD)

    stdscr.refresh()  # c'est ici que tout s'affiche réellement


# ==============================================================================
# ÉTAPE 5 : LA BOUCLE DE JEU
# Principe de tout programme interactif :
# afficher -> attendre une touche -> modifier l'état -> recommencer
# ==============================================================================


def main(stdscr):
    curses.curs_set(0)  # on masque le curseur système : on dessine le nôtre

    puzzle, solution, original_mask = generate_puzzle(empty_cells=40)

    # Le joueur travaille sur une COPIE, pour ne jamais abîmer le puzzle initial.
    current_board = [row[:] for row in puzzle]

    cursor_r, cursor_c = 0, 0  # position du curseur dans la grille (pas à l'écran)
    message = "Prêt à jouer ! Placez-vous sur une case et entrez un chiffre."

    while True:
        draw_grid(stdscr, current_board, cursor_r, cursor_c, original_mask, message)

        key = stdscr.getch()  # bloque jusqu'à ce que le joueur appuie sur une touche

        # --- Quitter ---
        if key in (ord("q"), ord("Q")):
            break

        # --- Déplacements ---
        # max/min "bloquent" le curseur dans la grille (indices 0 à 8)
        # au lieu de le laisser sortir.
        elif key == curses.KEY_UP:
            cursor_r = max(0, cursor_r - 1)
        elif key == curses.KEY_DOWN:
            cursor_r = min(8, cursor_r + 1)
        elif key == curses.KEY_LEFT:
            cursor_c = max(0, cursor_c - 1)
        elif key == curses.KEY_RIGHT:
            cursor_c = min(8, cursor_c + 1)

        # --- Saisie d'un chiffre ---
        # getch() renvoie le code ASCII de la touche : on compare donc
        # à ord("1") et ord("9"), puis on reconvertit en entier.
        elif ord("1") <= key <= ord("9"):
            num = int(chr(key))
            if original_mask[cursor_r][cursor_c]:
                message = "Impossible de modifier une case d'origine !"
            else:
                current_board[cursor_r][cursor_c] = num
                message = f"Chiffre {num} placé en ({cursor_r+1}, {cursor_c+1})"

                # +1 car le joueur compte à partir de 1, alors que
                # Python compte à partir de 0.

                # On teste la victoire après chaque saisie : le joueur est
                # prévenu dès qu'il place le dernier bon chiffre.
                if check_victory(current_board, solution):
                    message = "BRAVO ! Vous avez résolu le Sudoku !"

        # --- Effacement ---
        # Plusieurs codes pour la même action : selon le terminal, la touche
        # Retour arrière n'envoie pas le même code (KEY_BACKSPACE, 127 ou \b).
        elif key in (curses.KEY_BACKSPACE, curses.KEY_DC, 127, ord("\b"), ord("0")):
            if original_mask[cursor_r][cursor_c]:
                message = "Impossible d'effacer une case d'origine !"
            else:
                current_board[cursor_r][cursor_c] = 0
                message = "Case effacée."

        # --- 'v' : vérifier la case sous le curseur (aide au joueur) ---
        elif key in (ord("v"), ord("V")):
            val = current_board[cursor_r][cursor_c]
            if val == 0:
                message = "Cette case est vide !"
            elif original_mask[cursor_r][cursor_c]:
                message = "C'est une case d'origine (elle est correcte)."
            elif val == solution[cursor_r][cursor_c]:
                message = f"CORRECT ! Le {val} en ({cursor_r+1}, {cursor_c+1}) est bien placé."
            else:
                message = f"INCORRECT ! Le {val} en ({cursor_r+1}, {cursor_c+1}) est faux."

        # --- 'c' : afficher la solution complète ---
        elif key in (ord("c"), ord("C")):
            current_board = [row[:] for row in solution]  # copie, pas de partage
            message = "Correction affichée ! Grille complètement résolue."


# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================

if __name__ == "__main__":
    curses.wrapper(main)