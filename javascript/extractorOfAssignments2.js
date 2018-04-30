// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    const identifierContextWindowSize = 20; // assumption: even number

    function visitCode(ast, locationMap, path, allAssignments, fileID) {
        console.log("Reading " + path);

        let totalAssignments = 0;
        let totalAssignmentsConsidered = 0;

        const pastIdentifiers = [];
        const unfinishedAssignments = [];
        const parentStack = [];
        const assignments = [];
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (parent) parentStack.push(parent);

                if (node && node.type == "Identifier") {
                    pastIdentifiers.push("ID:"+node.name);

                    // finalize assignments with now-available postIdentifierContext
                    let nbFinished = 0;
                    for (let i = 0; i < unfinishedAssignments.length; i++) {
                        const unfinishedAssignment = unfinishedAssignments[i];
                        if (pastIdentifiers.length >= unfinishedAssignment.identifierIndex + identifierContextWindowSize/2) {
                            const postIdentifierContext = pastIdentifiers.slice(unfinishedAssignment.identifierIndex, unfinishedAssignment.identifierIndex + identifierContextWindowSize/2);
                            unfinishedAssignment.assignment.context = unfinishedAssignment.assignment.context.concat(postIdentifierContext);
                            totalAssignmentsConsidered += 1;
                            assignments.push(unfinishedAssignment.assignment);
                            nbFinished++;
                        } else {
                            break;
                        }
                    }
                    unfinishedAssignments.splice(0, nbFinished);
                }

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
                    // TODO: consider assignments to properties (and use property name as rhs)

                    const nameOfLHS = util.getNameOfASTNode(lhs);
                    const nameOfRHS = util.getNameOfASTNode(rhs);
                    const parentName = parent.type;
                    const grandParentName = parentStack.length > 1 ? parentStack[parentStack.length - 2].type : "";
                    const preIdentifierContext = pastIdentifiers.slice(Math.max(0, pastIdentifiers.length - identifierContextWindowSize/2), pastIdentifiers.length);
                    while (preIdentifierContext.length < identifierContextWindowSize/2) {
                        preIdentifierContext.unshift("");
                    }
                    if (typeof nameOfLHS !== "undefined" && typeof nameOfRHS !== "undefined") {
                        let locString = path + " : " + node.loc.start.line + " - " + node.loc.end.line;
                        let typeOfRHS = util.getTypeOfASTNode(rhs);
                        const assignment = {
                            lhs:nameOfLHS,
                            rhs:nameOfRHS,
                            rhsType:typeOfRHS,
                            parent:parentName,
                            grandParent:grandParentName,
                            context:preIdentifierContext, // postIdentifierContext will get appended later
                            src:locString
                        };
                        unfinishedAssignments.push({assignment: assignment, identifierIndex: pastIdentifiers.length});
                    }
                }
            },
            leave:function(node, parent) {
                if (parent) parentStack.pop();
            }
        });

        for (let i = 0; i < unfinishedAssignments.length; i++) {
            const unfinishedAssignment = unfinishedAssignments[i];
            const postIdentifierContext = pastIdentifiers.slice(unfinishedAssignment.identifierIndex, unfinishedAssignment.identifierIndex + identifierContextWindowSize/2);
            while (postIdentifierContext.length < identifierContextWindowSize/2) {
                postIdentifierContext.push("");
            }
            unfinishedAssignment.assignment.context = unfinishedAssignment.assignment.context.concat(postIdentifierContext);
            totalAssignmentsConsidered += 1;
            assignments.push(unfinishedAssignment.assignment);
        }

        allAssignments.push(...assignments);
        console.log("Added assignments. Total now: " + allAssignments.length);
        console.log("Considered assignments: " + totalAssignmentsConsidered + " out of " + totalAssignments + " (" + Math.round(100 * totalAssignmentsConsidered / totalAssignments) + "%)");
    }

    module.exports.visitCode = visitCode;

})();
