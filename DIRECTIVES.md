
## Technical Requirements

### 1. Move Customization & Typing Strategy
The current combat system relies on hardcoded moves and lacks tactical depth. Implement the following two sub-systems:

*   **Move Learning System (Level-Up Modal):**
    *   Track the number of moves a character knows (maximum of 4).
    *   Upon leveling up, if a new move is available and the character already knows 4 moves, trigger a modal interface.
    *   **Modal Text/Flow:** Display: *" [Character Name] wants to learn [New Move], but already knows 4 moves!"*
    *   Allow the user to select an existing move to replace, or choose to forget the new move.
*   **Type Effectiveness System:**
    *   Implement a type chart/matrix (e.g., Fire, Water, Grass, Normal).
    *   Apply damage multipliers during combat calculations based on typing (e.g., Fire deals 2x damage to Grass).

### 2. Battle Camera Dynamics & Hit Effects
The battle interface currently feels static. Add visual feedback during attacks to make combat feel more dynamic:

*   **Screen Shake Effect:**
    *   When an attack lands, trigger a screen shake animation.
    *   Implement this using a CSS keyframe animation or your framework's equivalent. 
    *   *Example CSS reference:*
        ```css
        @keyframes shake {
          0% { transform: translate(1px, 1px) rotate(0deg); }
          10% { transform: translate(-1px, -2px) rotate(-1deg); }
          20% { transform: translate(-3px, 0px) rotate(1deg); }
          30% { transform: translate(0px, 2px) rotate(0deg); }
          40% { transform: translate(1px, -1px) rotate(1deg); }
          50% { transform: translate(-1px, 2px) rotate(-1deg); }
          60% { transform: translate(-3px, 1px) rotate(0deg); }
          70% { transform: translate(2px, 1px) rotate(-1deg); }
          80% { transform: translate(-1px, -1px) rotate(1deg); }
          90% { transform: translate(2px, 2px) rotate(0deg); }
          100% { transform: translate(1px, -2px) rotate(-1deg); }
        }
        ```
*   **Slash Animation:**
    *   Render a temporary visual slash or impact effect over the target's sprite when they take damage.
*   **Floating Combat Text:**
    *   When damage is dealt, instantiate the damage number at the target's location.
    *   Animate the text so it floats upward and fades out over a brief duration (e.g., 1–1.5 seconds).
