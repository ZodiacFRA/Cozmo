# Cozmo
F21-HR 2nd Coursework

Coursework 2 – Human Robot Interaction (group work 4-5 students) deadline for the all document
submissions is Week 11 on the 28.11.2019 15:30 pm and the presentation will be held on 29.11.2019
and the 6.12.2019.

Implement a human-robot-game using a Cozmo robot and run an experiment to evaluate its usability
and user experience.

## The Game
#### Components:  
• 1 Cozmo robot  
• 2 Cubes  
• (minimum) 8 Control cards  
• 1 Execution card  
• 1 Egg timer  
#### Control Cards: 
Each control card shows a different ARMarker [1]. Each of these markers is associated
with a specific action that Cozmo can execute. These actions are:  
• Detect cube (find a cube in the current camera view)  
• Approach cube (move towards the cube until Cozmo touches it)  
• Raise forklift  
• Lower forklift  
• Turn left (turn 90 deg counter clockwise)  
• Turn right (turn 90 clockwise)  
• Move forward (move 10cm forward)  
• Move backward (move 10cm backward)  

#### Execution Card: 
A single card that contains an ARMarker different to the markers on the control cards.  
This marker is used as the trigger to start executing the programme the human has given Cozmo using
the Control Cards.  
#### Set-up: 
The cubes are placed on a table together with the Cozmo. The control cards are handed to the
human playing the game. Cozmo is started and explores its environment, creating a map of where the
cubes and the player are located.  
Goal: The player has to program Cozmo to pick up one of the cubes and put it on top of the other cube
using the Control Cards.  
#### How to play: 
The player is presented with the set-up. Cozmo approaches the player, explains the goal
of the game, and gives the player the trigger to start. Once Cozmo has started the game, the player
will start the egg timer and show any number of Control Cards to the robot one after the other to
build up a programme of actions to execute. This programme should lead to the successful execution
of the given goal. Once the player has finished programming Cozmo using the Control Cards or the
time on the egg timer has run out, the player shows the Execution Card and Cozmo will start executing
the programme. If this leads to a successful completion of the task, Cozmo notifies the player. If it
does not lead to a successful completion of the task, Cozmo will reset the playing field and start again.

#### Steps of the game:
1. Cozmo explains the goal (stack one cube on top of the other)  
2. One after the other, the player shows a sequence of Control Cards to Cozmo.  
3. The player shows the Execution Card.  
4. Cozmo executes the sequence of actions Programmed in step 2.  
5. Cozmo checks if the goal has been achieved  
6. End of the game    
    a. If the goal has been achieved, Cozmo congratulates the player,    
    b. Otherwise, Cozmo resets the game and starts at step 1.  

This game has to be evaluated in an experiment using the other participants of the course. Evaluated
the game using success rate, speed for finishing the game, and System Usability scale questionnaire.
Technical implementation details: In order to create this game, the system has to include:
• A map that stores the starting position of the cubes and the player and keeps track
of Cozmos current position.  
• An exploration algorithm that creates this map  
• A world model that keeps track of the current state of the world (position of cubes, player,
and goal condition)  
• A victory condition check (comparing the current state of the world to the desired goal
condition)  
• A reset procedure that uses Cozmo to put all the cubes in the places they have been in when
the game was started and subsequently approach the player  
• A set of actions representing the actions on the Control Cards, i.e. Detect cube (find a cube in
the current camera view), Approach cube (move towards the cube until Cozmo touches it), Raise
forklift, Lower forklift, Turn left (turn 90 deg counter clockwise), Turn right (turn 90 clockwise),
Move forward (move 10cm forward), Move backward (move 10cm backward)  
• A programme memory that stores the sequence of Control Cards shown by the player  
• A communication component able to explain the goal of the game, declare victory or defeat,
and give feedback to the player during play.  
• Face detection  
• ARMarker detection  

#### Physical implementation details: 
The game set-up has to include the components listed above. The Control and Execution Cards have to be created. 
The target environment is a tabletop. The game can be enhanced by creating a maze or obstacles for Cozmo.  

#### Evaluation and outcome: 
You have to evaluate the game with your peers. Invite people out with your
group to play the game. Make observations about success rate and completion time, and have your
participants fill your UX questionnaire. Details of the technical and physical implementation together
with the evaluation results are to be presented during the lecture in 15-minute presentation.
