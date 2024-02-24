#!/bin/bash
python3.12 syntax_analyzer.py ArrayTest/Main.jack > ArrayTest/myMain.xml; \
    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ArrayTest/myMain.xml; \
    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ArrayTest/myMain.xml; \
    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ArrayTest/myMain.xml; \
    ../../tools/TextComparer.sh ArrayTest/myMain.xml ArrayTest/Main.xml


#python3.12 syntax_analyzer.py ExpressionLessSquare/Main.jack > ExpressionLessSquare/myMain.xml; \
#    sed -i 's/<parameterList\/>/<parameterList>\n<\/parameterList>/g' ExpressionLessSquare/myMain.xml; \
#    sed -i 's/<expressionList\/>/<expressionList>\n<\/expressionList>/g' ExpressionLessSquare/myMain.xml; \
#    sed -i 's/<statements\/>/<statements>\n<\/statements>/g' ExpressionLessSquare/myMain.xml; \
#    ../../tools/TextComparer.sh ExpressionLessSquare/myMain.xml ExpressionLessSquare/Main.xml
