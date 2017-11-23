// Author: Michael Pradel

(function() {

    const acorn = require("acorn");
    const estraverse = require("estraverse");

    function getChildren(parent, ignoredChild) {
        const children = [];
        for (const prop in parent) {
            if (parent.hasOwnProperty(prop)) {
                const child = parent[prop];
                if (Array.isArray(child)) {
                    for (let i = 0; i < child.length; i++) {
                        const actualChild = child[i];
                        if (actualChild !== ignoredChild) {
                            children.push(actualChild);
                        }
                    }
                } else if (typeof child === "object") {
                    if (child !== ignoredChild) {
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

    function nodeToString(node) {
        let result;
        if (node.type === "Identifier") {
            result = "ID:" + node.name;
        } else if (node.type === "Literal") {
            result = "LIT:" + node.value;
        } else if (Array.isArray(node)) {
            result = "Array";
        } else if (typeof node.type === "string") {
            result = node.type;
        } else {
            throw "Unexpected node type: " + JSON.stringify(node);
        }
        // TODO limit size
        return result;
    }

    const ast = acorn.parse("elems.push(2, 'aa')");
    console.log(JSON.stringify(ast, 0, 2));
    const ancestors= [];
    estraverse.traverse(ast, {
        enter:function(node, parent) {
            if (node.type === "Literal") {
                const positionInParent = positionIn(parent, node);
                const grandParent = ancestors[ancestors.length - 2];
                const positionInGrandParent = positionIn(grandParent, parent);
                const siblings = getChildren(parent, node);
                const uncles = getChildren(grandParent, parent); // getUncles(grandParent, parent);
                const cousins = getAllChildren(uncles);
                const nephews = getAllChildren(siblings);
                console.log("\n"+JSON.stringify(node));
                console.log("Parent     : " + nodeToString(parent));
                console.log("  Position : " + positionInParent);
                console.log("Grandparent: " + nodeToString((grandParent)));
                console.log("  Position : " + positionInGrandParent);
                console.log("Siblings   : " + siblings.map(nodeToString));
                console.log("Uncles     : " + uncles.map(nodeToString));
                console.log("Cousins    : " + cousins.map(nodeToString));
                console.log("Nephews    : " + nephews.map(nodeToString));
            }

            ancestors.push(node);
        },
        leave:function(node, parent) {
            ancestors.pop();
        }
    });

})();