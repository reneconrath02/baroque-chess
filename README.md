# baroque-chess


## Necessary software

To run the full PlayAgainstCaissa, including comments, you will need to install transformer and pytorch. 

`pip install transformers`

`pip install torch`

If torch doesn't work, try 

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117`

Information on both can be found at [transformers](https://huggingface.co/docs/transformers/index) and
[pytorch](https://pytorch.org/)

We used pygame to make and run the GUI. 

## PlayAgainstCaissa

To fully play against Caissa, run the file PlayAgainstCaissa. This is the full version, where the player can see a visual
representation of the states that Caissa is evaluating. Caissa also will make
a comment after each move. In this version, Caissa is set at 3-ply, and will fully run that 3-ply. 

## PlayAgainstCaissaQuick

To play a quicker game against Caissa, you can run PlayAgainstCaissaQuick. This version does not have a chat feature. 
It also uses IDDFS like normal Caissa, and you can change how long Caissa has for each move by changing the CAISSA_TIME_LIMIT, found
at the top of the file. 

## PlayAgainstYourself

To play a game of baroque chess against yourself, you can run PlayAgainstYourself. 

## Other files overview
chat, color, config, const, dragger, game, piece, sound, theme, and board are all files that help run the game. 

Caissa_visualizer is a class that helps display the visual when you run PlayAgainstCaissa. 

Caissa_BC_Player, Caissa_BC_Player_Move_Generator, Caissa_BC_Player_Remark_Generator, Caissa_BC_Player_Transparent, and Caissa_BC_Player_Zobrist
are the files containing the code for Caissa. Caissa_BC_Player and Caissa_BC_Player_Transparent both contain the makeMove() function,
which is what is called to actually make a move. 
