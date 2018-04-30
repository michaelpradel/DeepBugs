// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    function visitCode(ast, locationMap, path, allAssignments, fileID) {
        console.log("Reading " + path);

        let totalAssignments = 0;
        let totalAssignmentsConsidered = 0;

        const assignments = [];
        const code = fs.readFileSync(path);
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                let lhs, rhs;
                if (node && node.type === "AssignmentExpression") {
                    totalAssignments += 1;
                    if (node.left.type === "Identifier") {
                        lhs = node.left;
                        rhs = node.right;
                    } else if (node && node.type === "VariableDeclarator" && node.init !== null) {
                        lhs = node.id;
                        rhs = node.init;
                    } else return;

                    const nameOfLHS = util.getNameOfASTNode(lhs);
                    const nameOfRHS = util.getNameOfASTNode(rhs);
                    if (typeof nameOfLHS !== "undefined" && typeof nameOfRHS !== "undefined") {
                        let locString = path + " : " + node.loc.start.line + " - " + node.loc.end.line;
                        let typeOfRHS = util.getTypeOfASTNode(rhs);
                        const assignment = {
                            lhs:nameOfLHS,
                            rhs:nameOfRHS,
                            rhsType:typeOfRHS,
                            src:locString
                        };
                        totalAssignmentsConsidered += 1;
                        assignments.push(assignment);
                    }
                }
            }
        });
        allAssignments.push(...assignments);
        console.log("Added assignments. Total now: " + allAssignments.length);
        console.log("Considered assignments: " + totalAssignmentsConsidered + " out of " + totalAssignments + " (" + Math.round(100 * totalAssignmentsConsidered / totalAssignments) + "%)");
    }

    module.exports.visitCode = visitCode;

})();

