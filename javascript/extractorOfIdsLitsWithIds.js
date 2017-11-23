// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const util = require("./jsExtractionUtil");

    const tokenContextLength = 20; // must be an even number

    function getContext(tokens, idx, targetLength) {
        let preContext = [];
        let currIdx = idx - 1;
        while (currIdx >= 0 && preContext.length < targetLength) {
            // go backward in token sequence and add identifiers to preContext
            let currToken = tokens[currIdx];
            if (util.isId(currToken)) preContext = [currToken].concat(preContext);
            currIdx--;
        }

        let postContext = [];
        currIdx = idx + 1;
        while (currIdx < tokens.length && postContext.length < targetLength) {
            // go forward in token sequence and add identifiers to postContext
            let currToken = tokens[currIdx];
            if (util.isId(currToken)) postContext.push(currToken);
            currIdx++;
        }

        return [preContext, postContext];
    }

    function visitFile(path, allIdsLits) {
        console.log("Reading " + path);

        const code = fs.readFileSync(path);
        const tokens = util.getTokens(code);
        const k = tokenContextLength / 2;
        if (tokens) {
            for (let i = 0; i < tokens.length; i++) {
                const token = tokens[i];
                if (util.isIdLit(token)) {
                    let [preContext, postContext] = getContext(tokens, i, k);
                    preContext = util.tokensToStrings(preContext);
                    while (preContext.length !== k) preContext = [""].concat(preContext);
                    postContext = util.tokensToStrings(postContext);
                    while (postContext.length !== k) postContext.push("");
                    const idLit = {
                        token: util.tokenToString(token),
                        context: preContext.concat(postContext)
                    };
                    allIdsLits.push(idLit);
                }
            }
        } else {
            console.log("Ignoring file with parse errors: " + path);
        }
    }

    module.exports.visitFile = visitFile;

})();