DO NOT USE THIS YET! IT JUST DOESN'T WORK!

This is supposed to be a simple code assist plugin for SublimeText2.
The way it is intended to work for now is by scanning all javascript files in the current project, and building a model out of the functions, variables and classes so as to propose them through the contextual menu when editing javascript files.

It is not intended to be a code assist tool that knows the type of variable you are currently accessing so as to provide contextual suggestions, but rather just as a tool to speed up typing and making it less error prone.

This is inspired by how the current SublimeText2 code assist works inside a given file, it simply proposes all words typed so far, and even if this is not really code completion as we might know it, it is pretty darn useful!

There are probably other (better) attempts at doing this, but I don't care, this is worth the try anyway.

For now, the tool parses ALL javascript files at the beginning, and this simply is not proving to work out well.
Launching a parsing on 600 files takes about 25 minutes ;-)
