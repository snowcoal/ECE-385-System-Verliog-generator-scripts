### System-Verliog-ROM-generator-scripts
Some scripts I wrote that generate System Verliog ROMs, module instantiations, and C code fo my final project,
which was an FPGA pacman game.

NOTE: Due to people potentially copying my entire project, this is NOT the full program
with all required assets!!! This is simply an example showing what I did to generate these ROMs. DO NOT copy exactly
what I did here (you wont be able to generate anything without the correct input images), and instead use this as 
an example to help you write your own scripts specific to YOUR project!!

Features:

generateGhostROM() generates ROMS for ghost sprites

generateBoardROM() generates a large ROM for the game board

generateDotStuff() generates a some module instantiations and an "OR" gate for wiring everything together

generateCStuff() generates some C arrays with specific values of dot locations

generateScaredGhostROM() generates the ROM for the ghosts in the scared state

