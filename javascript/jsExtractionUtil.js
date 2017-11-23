// Author: Michael Pradel

(function() {

    const acorn = require("acorn");

    const maxLengthOfTokens = 200;

    function getTokens(code) {
        try {
            const tokenizer = acorn.tokenizer(code, {locations:true});
            const tokens = [];
            let nextToken = tokenizer.getToken();
            while (nextToken.type !== acorn.tokTypes.eof) {
                tokens.push(nextToken);
                nextToken = tokenizer.getToken();
            }
            return tokens;
        } catch (e) {
        }
    }

    function getAST(code, noLocations) {
        try {
            if (noLocations) return acorn.parse(code);
            else return acorn.parse(code, {locations:true});
        } catch (e) {
        }
    }

    function getNameOfASTNode(node) {
        if (node.type === "Identifier") return "ID:" + node.name;
        else if (node.type === "CallExpression") return getNameOfASTNode(node.callee);
        else if (node.type === "MemberExpression" && node.computed === true) return getNameOfASTNode(node.object);
        else if (node.type === "MemberExpression" && node.computed === false) return getNameOfASTNode(node.property);
        else if (node.type === "Literal") return "LIT:" + String(node.value);
        else if (node.type === "ThisExpression") return "LIT:this";
        else if (node.type === "UpdateExpression") return getNameOfASTNode(node.argument);
    }

    function getKindOfASTNode(node) {
        if (node.type === "Identifier") return "ID";
        else if (node.type === "CallExpression") return getKindOfASTNode(node.callee);
        else if (node.type === "MemberExpression" && node.computed === true) return getKindOfASTNode(node.object);
        else if (node.type === "MemberExpression" && node.computed === false) return getKindOfASTNode(node.property);
        else if (node.type === "Literal") return "LIT";
        else if (node.type === "ThisExpression") return "LIT";
    }

    function getTypeOfASTNode(node) {
        if (node.type === "Literal") {
            if (node.hasOwnProperty("regex")) return "regex";
            else if (node.value === null) return "null";
            else return typeof node.value;
        } else if (node.type === "ThisExpression") return "object";
        else if (node.type === "Identifier" && node.name === "undefined") return "undefined";
        else return "unknown";
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
        return result.slice(0, maxLengthOfTokens);
    }

    const identifierTokenType = "name";
    const literalTokenTypes = ["num", "regexp", "string", "null", "true", "false"];

    function tokenToString(t) {
        let result;
        if (t.type.label === identifierTokenType) {
            result = "ID:";
        } else if (literalTokenTypes.indexOf(t.type.label) != -1) {
            result = "LIT:";
        } else {
            result = "STD:";
        }

        if (typeof t.value === "undefined") result += t.type.label;
        else if (typeof t.value === "string" || typeof t.value === "number") result += String(t.value);
        else if (t.type.label === "regexp") result += String(t.value.value);
        else {
            console.log("Unexpected token:\n" + JSON.stringify(t, 0, 2));
        }
        return result.slice(0, maxLengthOfTokens);
    }

    function tokensToStrings(tokens) {
        return tokens.map(tokenToString);
    }

    function isIdLit(token) {
        return isId(token) || isLit(token)
    }

    function isId(token) {
        return token.type.label === "name";
    }

    function isLit(token) {
        return token.type.label === "num" || token.type.label === "regexp" || token.type.label === "string"
    }

    function computeLocationMap(tokens) {
        // maps line-column-based location to character-based location
        const lcLocationToCharLocation = {};
        for (let i = 0; i < tokens.length; i++) {
            const t = tokens[i];
            const lcStartLocation = t.loc.start.line + ":" + t.loc.start.column;
            const lcEndLocation = t.loc.end.line + ":" + t.loc.end.column;
            lcLocationToCharLocation[lcStartLocation] = t.start;
            lcLocationToCharLocation[lcEndLocation] = t.end;
        }
        return lcLocationToCharLocation;
    }

    function getLocationOfASTNode(node, lcLocationToCharLocation) {
        const lcStartLocation = node.loc.start.line + ":" + node.loc.start.column;
        const lcEndLocation = node.loc.end.line + ":" + node.loc.end.column;
        const start = lcLocationToCharLocation[lcStartLocation];
        const end = lcLocationToCharLocation[lcEndLocation];
        const diff = end-start;
        return nbToPaddedStr(start, 6) + nbToPaddedStr(diff, 4);
    }

    function nbToPaddedStr(nb, length) {
        let str = String(nb);
        while (str.length < length) {
            str = "0" + str;
        }
        return str;
    }

    function getNameOfFunction(functionNode, parentNode) {
        if (functionNode.id && functionNode.id.name) return "ID:"+functionNode.id.name;
        if (parentNode.type === "AssignmentExpression") {
            if (parentNode.left.type === "Identifier") return "ID:"+parentNode.left.name;
            if (parentNode.left.type === "MemberExpression" &&
                parentNode.left.property.type === "Identifier") return "ID:"+parentNode.left.property.name;
        }
        if (parentNode.type === "VariableDeclarator") {
            if (parentNode.id.type === "Identifier") return "ID:"+parentNode.id.name;
        }
        if (parentNode.type === "Property") {
            if (parentNode.key.type === "Identifier") return "ID:"+parentNode.key.name;
        }
    }

    module.exports.getTokens = getTokens;
    module.exports.getAST = getAST;
    module.exports.getNameOfASTNode = getNameOfASTNode;
    module.exports.getKindOfASTNode = getKindOfASTNode;
    module.exports.getTypeOfASTNode = getTypeOfASTNode;
    module.exports.nodeToString = nodeToString;
    module.exports.tokenToString = tokenToString;
    module.exports.tokensToStrings = tokensToStrings;
    module.exports.isId = isId;
    module.exports.isLit = isLit;
    module.exports.isIdLit = isIdLit;
    module.exports.nbToPaddedStr = nbToPaddedStr;
    module.exports.computeLocationMap = computeLocationMap;
    module.exports.getLocationOfASTNode = getLocationOfASTNode;
    module.exports.getNameOfFunction = getNameOfFunction;

})();