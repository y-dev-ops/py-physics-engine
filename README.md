🚀 My 2D Physics Engine (Python + Tkinter)
A lightweight, custom-built 2D physics engine developed in Python. This project features a Rigidbody system and a flexible scripting architecture inspired by modern game engines like Unity.

🛠 Features
Physics Core: Real-time gravity and collision detection.

Collision Forces: Realistic physics response (impulse resolution) when objects hit.

Rigidbody System: Each object has a customizable Rigidbody script to control mass, drag, and velocity.

Custom Scripting: Support for external scripts located in the /scripts folder, allowing for unique object behaviors.

Tkinter Rendering: Uses Python's native GUI for high-compatibility 2D drawing.

📂 Project Structure
app.py: The main entry point. This is where you initialize the engine and "attach" scripts to objects.

/scripts: Add your custom .py logic here.

kinematics.py: Handles the math for gravity and collisions.

🎮 How to Use
Define an Object: Create a shape and assign it a Rigidbody.

Attach a Script:

Create a new file in the /scripts folder (e.g., player_movement.py).

Import and define the script in app.py.

Run: Execute python app.py to start the simulation.

🏗 Future Roadmap (To-Do)
[ ] Fix overlapping/sinking during collisions.

[ ] Add Rotation and Torque physics.

[ ] Implement a visual UI for the Inspector (instead of coding it in app.py).
