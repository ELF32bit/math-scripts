set background white
//{s 0.8} for tight pleats
//{s 0.9} for pleats

rule frame {
{ s 1 6 1 x 4.5 z 4.5 color #097bf6 } box
{ s 1 6 1 x 4.5 z -4.5 color #f609f2 } box
{ s 1 6 1 x -4.5 z 4.5 color #f68409 } box
{ s 1 6 1 x -4.5 z -4.5 color #09f60d } box

{ s 8 1 1 y 2.5 z 4.5 color #097bf6 } box
{ s 8 1 1 y 2.5 z -4.5 color #09f60d } box
{ s 8 1 1 y -2.5 z 4.5 color #097bf6 } box
{ s 8 1 1 y -2.5 z -4.5 color #09f60d } box

{ s 1 1 8 y 2.5 x 4.5 color #f609f2 } box
{ s 1 1 8 y 2.5 x -4.5 color #f68409 } box
{ s 1 1 8 y -2.5 x 4.5 color #f609f2 } box
{ s 1 1 8 y -2.5 x -4.5 color #f68409 } box
}

rule water {
{ s 8 1 8 y 2.5 a 0.5 color blue} box
}

rule frameR1 maxdepth 19 {
{ s 1.10466507859750 ry 5 b 0.9 } frameR1
frame
//water
}

rule lights {
{s 60 a 0.25 color white} sphere
{z 30 s 60 a 0.25 color white } sphere
{z -30 s 60 a 0.25 color white } sphere
{x 30 s 60 a 0.25 color white } sphere
{x -30 s 60 a 0.25 color white } sphere
}

rule final {
{s 8 1 8 y -2.5 color black } box
{s 8 1 8 y 2.5 color white } box
frameR1
}

final
//lights
