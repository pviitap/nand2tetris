#!/bin/bash
python3.11 syntax_analyzer.py ArrayTest/Main.jack > ArrayTest/myMain.xml; \
    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ArrayTest/myMain.xml; \
    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ArrayTest/myMain.xml; \
    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ArrayTest/myMain.xml; \
    ../../tools/TextComparer.sh ArrayTest/myMain.xml ArrayTest/Main.xml

python3.11 syntax_analyzer.py ExpressionLessSquare/Main.jack > ExpressionLessSquare/myMain.xml; \
    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ExpressionLessSquare/myMain.xml; \
    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ExpressionLessSquare/myMain.xml; \
    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ExpressionLessSquare/myMain.xml; \
    ../../tools/TextComparer.sh ExpressionLessSquare/myMain.xml ExpressionLessSquare/Main.xml

python3.11 syntax_analyzer.py ExpressionLessSquare/SquareGame.jack > ExpressionLessSquare/mySquareGame.xml; \
    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ExpressionLessSquare/mySquareGame.xml; \
    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ExpressionLessSquare/mySquareGame.xml; \
    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ExpressionLessSquare/mySquareGame.xml; \
    ../../tools/TextComparer.sh ExpressionLessSquare/mySquareGame.xml ExpressionLessSquare/SquareGame.xml

python3.11 syntax_analyzer.py ExpressionLessSquare/Square.jack > ExpressionLessSquare/mySquare.xml; \
    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ExpressionLessSquare/mySquare.xml; \
    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ExpressionLessSquare/mySquare.xml; \
    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ExpressionLessSquare/mySquare.xml; \
    ../../tools/TextComparer.sh ExpressionLessSquare/mySquare.xml ExpressionLessSquare/Square.xml
