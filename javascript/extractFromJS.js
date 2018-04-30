// Author: Michael Pradel

(function() {

    const usage = `
Two usage modes:
  1) extractFromJS.js <what> --parallel N <fileList.txt> <dir>
     Analyze all files in <dir> that are listed in <fileList.txt>, using N parallel instances.
     If <fileList.txt> is "all", analyze all files in <dir>.
  2) extractFromJS.js <what> --files <list of files>:
     Analyze the list of files.

The <what> argument must be one of:
  tokens
  calls
  callsMissingArg
  assignments
  binOps
  idsLitsWithTokens
  idsLitsWithIds
  idsLitsWithASTFamily
`;

    const process = require("process");
    const fs = require("fs");
    const walkSync = require("walk-sync");
    const {spawn} = require('child_process');

    const util = require("./jsExtractionUtil");

    const filesPerParallelInstance = 200;

    const fileToIDFileName = "fileIDs.json";

    function spawnSingleInstance(worklist, what) {
        console.log("Left in worklist: " + worklist.length + ". Spawning an instance.");
        const jsFiles = worklist.pop();
        if (jsFiles) {
            const argsToPass = [process.argv[1], what, "--files"].concat(jsFiles);
            const cmd = spawn("node", argsToPass);
            cmd.on("close", (code) => {
                console.log("Instance has finished with exit code " + code);
                if (worklist.length > 0) {
                    spawnSingleInstance(worklist, what);
                }
            });
            cmd.stdout.on('data', (data) => {
                console.log(`${data}`);
            });
            cmd.stderr.on('data', (data) => {
                console.log(`${data}`);
            });
        }
    }

    function spawnInstances(nbInstances, jsFiles, what) {
        const worklist = [];
        for (let i = 0; i < jsFiles.length; i += filesPerParallelInstance) {
            const chunkOfJSFiles = jsFiles.slice(i, i + filesPerParallelInstance);
            worklist.push(chunkOfJSFiles);
        }

        for (let instance = 0; instance < nbInstances; instance++) {
            spawnSingleInstance(worklist, what);
        }
    }

    function getOrCreateFileToID(files) {
        let fileToID;
        try {
            fileToID = JSON.parse(fs.readFileSync(fileToIDFileName, {encoding:"utf8"}));
        } catch (_) {
            fileToID = {};
        }
        let maxID = 1;
        for (let file in fileToID) {
            if (fileToID[file] > maxID) maxID = fileToID[file];
        }
        let haveAdded = false;
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (!fileToID.hasOwnProperty(file)) {
                maxID += 1;
                fileToID[file] = maxID;
                haveAdded = true;
            }
        }
        if (haveAdded) fs.writeFileSync(fileToIDFileName, JSON.stringify(fileToID, 0, 2));
        return fileToID;
    }

    function visitFile(jsFile, extractor, allData, fileID) {
        const code = fs.readFileSync(jsFile);
        const tokens = util.getTokens(code);
        const ast = util.getAST(code);
        if (tokens && ast) {
            const locationMap = util.computeLocationMap(tokens);
            extractor.visitCode(ast, locationMap, jsFile, allData, fileID);
        } else {
            console.log("Ignoring file with parse errors: " + jsFile);
        }
    }

    // read command line arguments
    const args = process.argv.slice(2);
    const what = args[0];
    if (["tokens", "calls", "assignments", "callsMissingArg", "binOps", "idsLitsWithTokens", "idsLitsWithIds", "idsLitsWithASTFamily"].indexOf(what) === -1) {
        console.log(usage);
        process.exit(1);
    }
    if (args[1] === "--parallel") {
        if (args.length !== 5) {
            console.log(usage);
            process.exit(1);
        }
        const nbInstances = args[2];
        const fileListFile = args[3];
        const dir = args[4];

        // filter to use only files in file list
        const relativeJsFiles = walkSync(dir, {globs:["**/*.js"], directories:false});
        let jsFiles;
        if (fileListFile === "all") {
            jsFiles = relativeJsFiles.map(f => dir + (dir.endsWith("/") ? "" : "/") + f);
        } else {
            const filesToConsider = new Set(fs.readFileSync(fileListFile, {encoding:"utf8"}).split("\n"));
            jsFiles = relativeJsFiles.map(f => dir + (dir.endsWith("/") ? "" : "/") + f).filter(p => filesToConsider.has(p));
        }
        console.log("Total number of files: " + jsFiles.length);
        getOrCreateFileToID(jsFiles);
        spawnInstances(nbInstances, jsFiles, what);
    } else if (args[1] === "--files") {
        let extractor;
        if (what === "calls") extractor = require("./extractorOfCalls");
        else if (what === "assignments") extractor = require("./extractorOfAssignments2");
        else if (what === "tokens") extractor = require("./extractorOfTokens");
        else if (what === "binOps") extractor = require("./extractorOfBinOps");
        else if (what === "idsLitsWithTokens") extractor = require("./extractorOfIdsLitsWithTokens");
        else if (what === "idsLitsWithIds") extractor = require("./extractorOfIdsLitsWithIds");
        else if (what === "idsLitsWithASTFamily") extractor = require("./extractorOfIdsLitsWithASTFamily");
        else if (what === "callsMissingArg") extractor = require("./extractorOfCallsMissingArg");

        const allData = [];
        const jsFiles = args.slice(2);
        let fileToID = getOrCreateFileToID(jsFiles);
        for (let i = 0; i < jsFiles.length; i++) {
            const jsFile = jsFiles[i];
            const fileID = fileToID[jsFile]; // assumption: at most 6 digits long

            if (what !== "tokens") {
                visitFile(jsFile, extractor, allData, fileID);
            } else{
                extractor.visitFile(jsFile, allData);
            }
        }
        const fileName = what + "_" + Date.now() + ".json";
        console.log("Writing " + allData.length + " items to file " + fileName);
        fs.writeFileSync(fileName, JSON.stringify(allData, null, 2));
    } else {
        console.log(usage);
        process.exit(1);
    }

})();