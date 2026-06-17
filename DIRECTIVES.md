
## Technical Requirements

### 1. Move Customization & Typing Strategy
The current combat system relies on hardcoded moves and lacks tactical depth. Implement the following two sub-systems using real matching pokemon moves:

*   **Move Learning System (Level-Up Modal):**
    *   Track the number of moves a character knows (maximum of 4).
    *   Upon leveling up, if a new move is available and the character already knows 4 moves, trigger a modal interface.
    *   **Modal Text/Flow:** Display: *" [Character Name] wants to learn [New Move], but already knows 4 moves!"*
    *   Allow the user to select an existing move to replace, or choose to forget the new move.
*   **Type Effectiveness System:**
    *   Implement a type chart/matrix (e.g., Fire, Water, Grass, Normal).
    *   Apply damage multipliers during combat calculations based on typing (e.g., Fire deals 2x damage to Grass).
