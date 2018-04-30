// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    // configuration parameters
    const maxLengthOfCalleeAndArguments = 200; // maximum number of characters

    function visitCode(ast, locationMap, path, allCalls, fileID) {
        console.log("Reading " + path);

        // first pass through AST: visit each fct. def. and extract formal parameter names
        const functionToParameters = {}; // string to array of strings
        let functionCounter = 0;
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (node.type === "FunctionDeclaration" || node.type === "FunctionExpression") {
                    functionCounter++;
                    if (node.params.length > 1) {
                        let functionName = util.getNameOfFunction(node, parent);
                        if (functionName) {
                            if (!functionToParameters.hasOwnProperty(functionName)) {
                                const parameterNames = [];
                                for (let i = 0; i < node.params.length; i++) {
                                    const parameter = node.params[i];
                                    parameterNames.push("ID:"+parameter.name);
                                }
                                functionToParameters[functionName] = parameterNames;
                            } // heuristically use only the first declaration in this file
                        }
                    }
                }
            }
        });
        // console.log("Functions with parameter names: "+Object.keys(functionToParameters).length+" of "+functionCounter);

        // second pass through AST: visit each call site and extract call data
        const calls = [];
        const parentStack = [];
        let callCounter = 0;
        let callWithParameterNameCounter = 0;
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (parent) parentStack.push(parent);
                if (node && node.type === "CallExpression") {
                    if (node.arguments.length === 0) return;

                    let calleeString;
                    let baseString;
                    let calleeNode;
                    if (node.callee.type === "MemberExpression") {
                        if (node.callee.computed === false) {
                            calleeNode = node.callee.property;
                            calleeString = util.getNameOfASTNode(calleeNode);
                            baseString = util.getNameOfASTNode(node.callee.object);
                        } else {
                            calleeNode = node.callee.object;
                            calleeString = util.getNameOfASTNode(calleeNode);
                            baseString = "";
                        }
                    } else {
                        calleeNode = node.callee;
                        calleeString = util.getNameOfASTNode(calleeNode);
                        baseString = "";
                    }

                    if (typeof calleeString === "undefined" || typeof baseString === "undefined") return;

                    const calleeLocation = fileID + util.getLocationOfASTNode(calleeNode, locationMap);

                    const argumentStrings = [];
                    const argumentLocations = [];
                    const argumentTypes = [];
                    for (let i = 0; i < node.arguments.length; i++) {
                        const argument = node.arguments[i];
                        const argumentString = util.getNameOfASTNode(argument);
                        const argumentLocation = fileID + util.getLocationOfASTNode(argument, locationMap);
                        const argumentType = util.getTypeOfASTNode(argument);
                        if (typeof argumentString === "undefined") return;
                        argumentStrings.push(argumentString.slice(0, maxLengthOfCalleeAndArguments));
                        argumentLocations.push(argumentLocation);
                        argumentTypes.push(argumentType);
                    }

                    const parameters = [];
                    let foundParameter = false;
                    for (let i = 0; i < argumentStrings.length; i++) {
                        let parameter = ""; // use empty parameter name if nothing else known
                        if (functionToParameters.hasOwnProperty(calleeString)) {
                            if (i < functionToParameters[calleeString].length) {
                                parameter = functionToParameters[calleeString][i];
                                foundParameter = true;
                            }
                        }
                        parameters.push(parameter);
                    }
                    callCounter++;
                    if (foundParameter) callWithParameterNameCounter++;

                    calleeString = calleeString.slice(0, maxLengthOfCalleeAndArguments);
                    baseString = baseString.slice(0, maxLengthOfCalleeAndArguments);

                    let locString = path + " : " + node.loc.start.line + " - " + node.loc.end.line;
                    if (argumentStrings.length >= 1) {
                        calls.push({
                            base:baseString,
                            callee:calleeString,
                            calleeLocation:calleeLocation,
                            arguments:argumentStrings,
                            argumentLocations:argumentLocations,
                            argumentTypes:argumentTypes,
                            parameters:parameters,
                            src:locString,
                            filename:path
                        });
                    }
                }
            },
            leave:function(node, parent) {
                if (parent) parentStack.pop();
            }
        });
        allCalls.push(...calls);
        console.log("Added calls. Total now: " + allCalls.length);

        // console.log("Calls with resolved parameter name: " + callWithParameterNameCounter+" of "+callCounter);
    }

    module.exports.visitCode = visitCode;

})();
