// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    function visitCode(ast, locationMap, path, allBinOps, fileIDStr) {
        console.log("Reading " + path);

        let totalBinOps = 0;
        let totalBinOpsConsidered = 0;

        const parentStack = [];
        const binOps = [];
        let tokenID = 1;
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (parent) parentStack.push(parent);
                if (node.type === "BinaryExpression") {
                    totalBinOps += 1;
                    const leftName = util.getNameOfASTNode(node.left);
                    const rightName = util.getNameOfASTNode(node.right);
                    const leftType = util.getTypeOfASTNode(node.left);
                    const rightType = util.getTypeOfASTNode(node.right);
                    const parentName = parent.type;
                    const grandParentName = parentStack.length > 1 ? parentStack[parentStack.length - 2].type : "";
                    if (typeof leftName !== "undefined" && typeof rightName !== "undefined") {
                        let locString = path + " : " + node.loc.start.line + " - " + node.loc.end.line;
                        const binOp = {
                            left:leftName,
                            right:rightName,
                            op:node.operator,
                            leftType:leftType,
                            rightType:rightType,
                            parent:parentName,
                            grandParent:grandParentName,
                            src:locString
                        };
                        binOps.push(binOp);
                        totalBinOpsConsidered += 1;
                        tokenID += 1;
                    }
                }
            },
            leave:function(node, parent) {
                if (parent) parentStack.pop();
            }
        });
        allBinOps.push(...binOps);
        console.log("Added binary operations. Total now: " + allBinOps.length);
        console.log("Considered binary operations: "+totalBinOpsConsidered+" out of "+totalBinOps+" ("+Math.round(100*totalBinOpsConsidered/totalBinOps)+"%)");
    }

    module.exports.visitCode = visitCode;

})();
