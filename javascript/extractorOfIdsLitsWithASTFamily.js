// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    function getChildren(parent, ignoredChild) {
        const children = [];
        for (const prop in parent) {
            if (parent.hasOwnProperty(prop) && prop !== "regex" && prop !== "loc") {
                const child = parent[prop];
                if (Array.isArray(child)) {
                    for (let i = 0; i < child.length; i++) {
                        const actualChild = child[i];
                        if (actualChild !== ignoredChild && !(child instanceof RegExp) && actualChild !== null) {
                            children.push(actualChild);
                        }
                    }
                } else if (typeof child === "object" && child !== null) {
                    if (child !== ignoredChild && !(child instanceof RegExp)) {
                        children.push(child);
                    }
                }
            }
        }
        return children;
    }

    function getAllChildren(parents, ignoredChild) {
        const allChildren = [];
        for (let i = 0; i < parents.length; i++) {
            const parent = parents[i];
            const newChildren = getChildren(parent);
            for (let j = 0; j < newChildren.length; j++) {
                const newChild = newChildren[j];
                if (newChild !== ignoredChild) {
                    allChildren.push(newChild)
                }
            }
        }
        return allChildren;
    }

    function positionIn(parent, child) {
        const position = getChildren(parent).indexOf(child);
        if (position === -1) throw "Could not find child in parent: " + JSON.stringify(parent) + " -- "+ JSON.stringify(child);
        return position;
    }

    function visitCode(ast, locationMap, path, allIdsLits, fileID) {
        console.log("Reading " + path);
        const ancestors= [];
        estraverse.traverse(ast, {
            enter:function(node, parent) {
                if (node.type === "Identifier" || node.type === "Literal") {
                    const positionInParent = positionIn(parent, node);
                    const grandParent = ancestors[ancestors.length - 2];
                    const positionInGrandParent = positionIn(grandParent, parent);
                    const siblings = getChildren(parent, node);
                    const uncles = getChildren(grandParent, parent); // getUncles(grandParent, parent);
                    const cousins = getAllChildren(uncles);
                    const nephews = getAllChildren(siblings);

                    const idLit = {
                        token: util.nodeToString(node),
                        context: {
                            parent: util.nodeToString(parent),
                            positionInParent: positionInParent,
                            grandParent: util.nodeToString(grandParent),
                            positionInGrandParent: positionInGrandParent,
                            siblings: Array.from(new Set(siblings.map(util.nodeToString))),
                            uncles: Array.from(new Set(uncles.map(util.nodeToString))),
                            cousins: Array.from(new Set(cousins.map(util.nodeToString))),
                            nephews: Array.from(new Set(nephews.map(util.nodeToString)))
                        },
                        location: fileID + util.getLocationOfASTNode(node, locationMap)
                    };

                    allIdsLits.push(idLit);
                }

                ancestors.push(node);
            },
            leave:function(node, parent) {
                ancestors.pop();
            }
        });
    }

    module.exports.visitCode = visitCode;

})();
