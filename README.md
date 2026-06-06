# /StroCate: MCBE Stronghold Calculator
Stronghold location calculator for Minecraft Bedrock Edition

## Features
* Calculates probability of each chunk (distance from first eye throw < 10000) having a stronghold
* Uses prior probability using information about how strongholds generate in Bedrock Edition
* Updates probability based on measurement using Bayes' theorem
* Users can customize standard measurement error according to how accurate they are in measuring eye
* Multiple input method available
* Calculates probability that stronghold is within N chunks from each chunk

## How to Use
### Game Setting
* Turn on "Enable Copy Coordinate UI", in version 1.20 or higher
  - You can find this option in Settings → General → Creator → Creator Settings → Enable Copy Coordinate UI

### Eye Allginment
* Information in this section is by TyGer. (https://www.youtube.com/@tyger2k)
* Borrowed image from their video. (https://www.youtube.com/watch?v=ktuEf4qcdt8)

![image](https://github.com/user-attachments/assets/c0b2e424-1f80-4423-bab7-6d209191a3bc)
* Standard eye allginment

![image](https://github.com/user-attachments/assets/d7e220e3-fbea-4911-8d82-cd0a2ba29577)
* Allgin this (monitor) pixel in the crosshair to the right of the center (minecraft) pixel of the eye of ender
* This differs from device to device. To find out accurate setup for your device, run command
/tp @p ~ ~ ~ facing @e [type= Eye_of_Ender_signal]
while ender eye is hovering

### Coordinate input
* There are 4 ways you can input coordinates

#### Copy+Paste
* This is available in version 1.20+ and you should turn on "Enable Copy Coordinate UI".
* Copy coordinate (Default: CTRL + ALT + C)
* Paste coordinate by either pressing "PASTE" button or using hotkey (Default: [ for coordinate 1, ] for coordinate 2)

#### Copy+Paste (corner)
* This is identical with "Copy+Paste", but coordinate 1 must be in the corner of the block
  (fractional part of the coordinate should be 0.30 or 0.70)
* Using this makes measurement about 30% more accurate

#### Show coordinates
* This works in all versions, but for version 1.20+, using "Copy+Paste" is recommended as it is far more accurate
* You should turn on "Show coordinates" on the settings
* Paste coordinate using hotkey (Default: [ for coordinate 1, ] for coordinate 2)

#### Manual input
* Manualy input coordinate by typing on the input box
* It doesn't have to be integers, so you can count pixels and write more accurate coordinates

### Input
#### Coord+Coord
* Stand on the relatively flat area
* Throw eye of ender and allign crosshair
  - For more accurate measurement, use low FOV(30°) and/or low camera sensitivity(0%)
 
![image](https://github.com/user-attachments/assets/560213de-383a-49ad-9e6b-70c1d547045e)
* Copy coordinate and press "PASTE" button next to "Coord 1" (or hotkey for 
* Move forward. Make sure your direction doesn't change due to surrounding terrain 
  - Moving more distance does make prediction accurate, but not being obstructed by terrain is much more important
  - Moving 5 blocks would cause 0.03° standard error and moving more than 16 blocks would ensure standard error smaller than 0.01°
* Copy coordinate and press "PASTE" button next to "Coord 2"
* Press "ADD" button and probabilities will be updated

#### Corner+Facing
* Surround yourself with 4 blocks
* Throw eye of ender and stand at the corner in that direction
* Align crosshair
    - For more accurate measurement, use low FOV(30°) and/or low camera sensitivity(0%)
      
![image](https://github.com/user-attachments/assets/66b8774d-bf5c-489b-8ebc-5132ef9cf707)
* Copy coordinate and press "PASTE" button next to "Coord 1"
  - Your both X and Z coordinate should end with either 0.30 or 0.70
* Enable "Full Keyboard Gameplay" and set "Smooth Roatation Speed" to minimum(1)
  - You can find this option in Setting → Controls → Keyboard & Mouse

![이미지_2025-06-14_104357482 (2)](https://github.com/user-attachments/assets/5cfe22f3-b4e5-465d-91c4-99acb6891ae7)
* Look Down straightly and align your crosshair to edge of the block
* Select whether your crosshair is facing X or Z direction
* Count and write how many (minecraft) pixels the crosshair is from the vertex. Around 2.1 in this example
  - This value should be within 0 and 8
* Press "ADD" button and probabilities will be updated

### Settings
#### Align Error
* Set this value based on how accurate you are in aligning crosshair with eye of ender.
  - Smaller value → Assumes accurate crosshair alignment → More confident prediction
  - Bigger value → Assumes less accurate crosshair alignment → Less confident prediction
* Tip
  - 0.03(Minimum): You can align crosshair (monitor) pixel perfect always
  - 0.3(Default): You can align crosshair (minecraft) pixel perfect
  - 1: You can align crosshair within center third of the ender eye
  - 4(Maximum): You can align crosshair within ender eye

#### Pixel Error
* This setting matters only if your input mode is "Corner+Facing"
* Set this value based on how accurate you can measure how many (minecraft) pixel the crosshair is from the vertex.
  - Smaller value → Assumes accurate measurement → More confident prediction
  - Bigger value → Assumes less accurate measurement → Less confident prediction
* Tip
  - 0.01(Minimum): You can count (monitor) pixels accurately and write the value
  - 0.03: You can count (minecraft) pixels and round to 1 decimal point
  - 0.3(Maximum): You can count (minecraft) pixels and round to nearest integer

#### Input Mode
* Coord+Coord
  - Recommeneded if surrounding terrain is flat
  - Generally more accurate than Corner+Facing
* Corner+Facing
  - Recommended if surrounding terrain is irregular
 
#### Prob Within
* Display probability that stronghold is within N chunks from candidate chunk
* This is supported because in Bedrock Edition, most near stronghold generate under the village. If you can find village within your render distance, you can easily locate stronghold with Sprinkz strategy
* It's recommended to set this value according to your render distance

### Troubleshooting
If calculator said 100% probability but stronghold wasn't there, consider..,
* You were obstructed by terrain while measuring direction with "Coord+Coord" input method
* Nearest stronghold was more than 4000 blocks away from (0,0)
* Each eye directed diffrent stronghold
* You set too low value in "align errror" or "pixel error" (=Your measurement were not accurate enough)

## Methodology
### Calculating prior probability
Simulated Bedrock Edition stronghold generation multiple times considering
* Village grid
  - Grid size is 34 chunks in x/z direction
  - Village can generate in chunk 0~27 in each grid
  - Village generate or doesn't generate according to biome, but that's difficult to simulate
  - Assumed there's 26.7% chance of village generating in each grid
* Scattered stronghold grid
  - Grid size is 200 chunks in x/z direction
  - Stronghold can generate in chunk 50~150 in each grid
  - There's 25% chance of stronghold generating in each grid
* Village stronghold generation
  - Simulated village stronghold generation based on Bedrockified by Earthcomputer
  - https://github.com/Earthcomputer/bedrockified/blob/master/src/main/java/net/earthcomputer/bedrockified/BedrockStrongholdStructure.java

Following information was gathered using simulation
* How often nearest stronghold is village stronghold or scattered stronghold
  - Nearest stronghold was village stronghold in 80.9% of the cases, scattered stronghold in 19.1% of the cases
* How distance from (0,0) and probability of having a village stronghold correlated
![Figure_1](https://github.com/user-attachments/assets/9d293f01-8ec5-4f7f-8da1-7a5675671380)
  - X axis: Distance from (0,0) in chunks, Y axis: Relative probability of chunk having a village stronghold
* How distance from (0,0) and probability of having a scattered stronghold correlated
![Figure_2](https://github.com/user-attachments/assets/2594939e-aee5-4d31-9ce5-a5cd6043370c)
  - X axis: Distance from (0,0) in chunks, Y axis: Relative probability of chunk having a scattered stronghold

Estimated probability of each chunk(distance from (0,0) < 4000) having a stronghold based on simulation data

### Calculating stronghold direction
When you throw eye of ender at (x1,z1), it starts flying from (x1+0.5,z1+0.5)=(a,b) and travels 12 blocks

To determine the stronghold direction, we need to calculate the coordinates where the eye is hovering after it flies

![image](https://github.com/user-attachments/assets/41311f61-dca2-4cbf-91d9-c78face4cd50)
* A(x1,z1): Coordinate 1, where user threw eye of the ender
* B(x2,z2): Coordinate 2, where user moved and recorded the second position
* C(x1+0.5,z1+0.5)=(a,b): Where eye of ender starts flying
* F(x,z): The point in the air where eye of ender hovers

F(x,z) is one of intersections between line AB and circle(center=C, radius=12)
This can be calculated by solving following system of equations
* z-z1=(z2-z1)/(x2-x1)*(x-x1): Line AB
* (x-a)^2+(z-b)^2=12^2: Circle
Solving this gives us two points, E and F, where the line intersects the circle

By comparing dot product of vector AB, vector CE and dot product of vector AB/vector CF, we can find out which intersection point corresponds to the actual hovering location of the eye

Stronghold is located on the half-line CF

### Calculating standard error
Program assumes 2 types of error affect the prediction
* Measurement error(σ1): How accurately user aligned crosshair
  - This is affected by user defined "Align error"(ε1)
  - Estimated using: σ1=arctan(ε1/12/16) (12: Distance eye flies, 16: Number of pixels in a block)
* Precision error(σ2): How precisely the direction is measured
  - In "Coord+Coord" mode, this is affected by distance between Coordinate 1 and Coordinate 2
  - Estimated using σ2=arctan(0.01*sqrt(2)/distance)*0.2
  - In "Corner+Facing" mode, this is affected by user defined "Pixel error"(ε1)
  - Estimated using σ2=arctan(ε1/16/0.3) (0.3: Distance between the player and block which player is facing)
* Combined error(σ) is calculated σ=sqrt(σ1^2+σ2^2)

### Updating probability
The posterior probability is proportional to the product of prior probability and the likelihood
* Posterior probability: The probability that a certain chunk contains the stronghold afte the new observation
* Prior probability: The probability that a certain chunk contains the stronghold before considering the new observation
* Likelihood: The probability of making the observation if the stronghold were located in that chunk

For normal distribution with mean(μ) and standard deviation(σ), the probability density function(PDF) is

![image](https://github.com/user-attachments/assets/6dfeba82-db9d-4b86-8060-6d7ee3e7dc6b)

![image](https://github.com/user-attachments/assets/4b4bbb81-6e7d-40bf-b3d3-8a491d815e09)

The value of PDF at x=A represents relative likelihood of observing value A from this distribution

If observed angle is θ and the eye of ender started flying from point C(a,b), for each chunk, the likelihood is calculated
* Eye of ender points to (2,2) of stronghold chunk
* Compute the direction vector from the eye's start point to the (2,2) of the chunk, vector CSn=(xn-a,zn-b)
* Calculate the angle(Δθ) between eye's observed direction and expected direction to the chunk
* Likelihood is value of PDF at x=Δθ, given μ=0, σ=combined error

After calculating unnormalized probabilities for all candidate chunks, normalize them so that total probability sums up to 1
