// Author: Michael Pradel

(function() {

    var fs = require("fs");
    var esprima = require("esprima");
    var estraverse = require("estraverse");
    var escodegen = require("escodegen");
    var clone = require("clone");

    var rawJSFilesDir = "../data/js/programs_50/";
    var modifiedJSFilesDir = "../data/js/buggy_fcts";

    var maxBugs = 100;

    function randElem(arr) {
        if (!arr || arr.length === 0) return undefined;
        return arr[Math.floor(Math.random() * (arr.length))];
    }

    function randNb(maxInclusive) {
        return Math.floor(Math.random() * (maxInclusive + 1));
    }

    function splitIntoFcts(ast) {
        var fcts = [];
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (node.type === "FunctionDeclaration") {
                    fcts.push(clone(node));
                }
            }
        });
        return fcts;
    }

    var expressionTypes = [
        "ThisExpression",
        "ArrayExpression",
        "ObjectExpression",
        "FunctionExpression",
        "ArrowExpression",
        "SequenceExpression",
        "UnaryExpression",
        "BinaeyExpression",
        "AssignmentExpression",
        "UpdateExpression",
        "LogicalExpression",
        "ConditionalExpression",
        "NewExpression",
        "CallExpression",
        "MemberExpression",
        "ComprehensionExpression"
    ];

    function modifyFunctionArgument(origAST) {
        // TODO: Use expressions from other programs? Otherwise, it always occurs twice.
        var ast = clone(origAST);
        var expressions = [];
        var callExpressions = [];
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (expressionTypes.indexOf(node.type) != -1) {
                    expressions.push(node);
                }
                if (node.type === "CallExpression") {
                    callExpressions.push(node);
                }
            }
        });
        if (callExpressions.length > 0 && expressions.length > 2) {
            var callExpression = randElem(callExpressions);
            var replacementExpression = undefined;
            while (!replacementExpression) {
                replacementExpression = randElem(expressions);
                if (replacementExpression === callExpression) replacementExpression = undefined;
            }
            replacementExpression = clone(replacementExpression);

            var args = callExpression.arguments;
            if (args.length === 0) {
                args.push(replacementExpression);
            } else {
                var idxToReplace = randNb(args.length - 1);
                args[idxToReplace] = replacementExpression;
            }
            return ast;
        }
    }

    var conditionalStmtTypes = [
        "IfStatement",
        "WhileStatement",
        "DoWhileStatement",
        "ForStatement"
    ];

    function modifyConditional(origAST) {
        var ast = clone(origAST);
        var conditionalStmts = [];
        var expressions = [];
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (conditionalStmtTypes.indexOf(node.type) != -1) {
                    conditionalStmts.push(node);
                }
                if (expressionTypes.indexOf(node.type) != -1) {
                    expressions.push(node);
                }
            }
        });

        if (conditionalStmts.length > 0) {
            var condStmt = randElem(conditionalStmts);
            var expr = condStmt.test;
            if (expr.type == "LogicalExpression") {
                condStmt.test = expr.left;
                return ast;
            } else {
                if (expressions.length > 0) {
                    var replacementExpr = randElem(expressions);
                    condStmt.test = replacementExpr;
                    return ast;
                }
            }
        }
    }

    var transformerFcts = [modifyFunctionArgument, modifyConditional];

    var files = fs.readdirSync(rawJSFilesDir);
    var origFcts = [];
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file.endsWith(".js")) {
            var content = fs.readFileSync(rawJSFilesDir + "/" + file, {encoding:"utf8"});
            var origAST = esprima.parse(content);
            var fcts = splitIntoFcts(origAST);
            for (var j = 0; j < fcts.length; j++) {
                var f = fcts[j];
                origFcts.push(f);
            }
        }
    }

    console.log("Functions: " + origFcts.length);

    var astPairs = [];
    for (var i = 0; i < origFcts.length; i++) {
        var origFct = origFcts[i];
        var transformer = randElem(transformerFcts);
        var modifiedFct = transformer(origFct);
        if (modifiedFct) {
            astPairs.push([origFct, modifiedFct]);
        }
    }

    var fileCtr = 0;
    for (var i = 0; i < astPairs.length && fileCtr < maxBugs; i++) {
        fileCtr += 1;
        var astPair = astPairs[i];
        var origCode = escodegen.generate(astPair[0]);
        fs.writeFileSync(modifiedJSFilesDir + "/orig/fct" + fileCtr + ".js", origCode);
        var modifiedCode = escodegen.generate(astPair[1]);
        fs.writeFileSync(modifiedJSFilesDir + "/buggy/fct" + fileCtr + ".js", modifiedCode);
    }

    console.log("Pairs of functions: " + fileCtr);


})();