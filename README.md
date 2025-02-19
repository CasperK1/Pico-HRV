# To setup your Pico

You need to have git installed. Make sure that you have python installed and that is in the path. You can verify this in terminal
by running <kbd>python --version</kbd> or <kbd>python3 --version</kbd>. If you see python version then python is in the path.

You also need to have mpremote installed. To install mpremote:

- <kbd>pip install mpremote</kbd>
  
  or
  
- <kbd>python -m pip install mpremote</kbd>

When the prerequisites are met then you can install the project and the libraries to your Pico.

## Check out the repository and install libraries
**First close any program that uses pico's I2C bus**

Start a terminal, go to (use <kbd>cd</kbd> command) the directory where you want to copy the project to. Then run:

<kbd>git clone --recurse-submodules https://gitlab.metropolia.fi/georgiia/hw2projectgroup9.git</kbd>

Go to the cloned directory <kbd> cd hw2projectgroup9 </kbd>

Then run:
- <kbd> .\install.cmd</kbd> if you use Windows PowerShell or cmd

- <kbd> ./install.sh</kbd> if you use Linux, OSX or GitBash

## Usage

- For simple HR measurement use first option "MEASURE HR". Then place your finger on the sensor
- For other measurement modes wait for 30s for them to complete. 




