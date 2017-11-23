/* exported GitCommander */
function GitCommander(repo) {

    function Commander() {
        return {
            _commands: {},
            addCommands: function(commands) {
                this._commands = commands;

                return this;
            },
            alias: function(a) {
                var self = this;

                Object.keys(a).forEach(function(aliasName){
                    self._commands[aliasName] = function(params) {
                        a[aliasName].split(' && ').forEach(function(command) {
                            self._commands[command](params);
                        });
                    };
                });

                return this;
            },
            run: function(command, params) {
                params = params || [params];
                this._commands[command](params);
            }
        };
    }

    var commander = new Commander()
        .addCommands({
            branch:  function(options) {
                if ( '-d' === options[0] ) {
                    repo.branchRemove(options[1]);
                } else {
                    repo.branch(options);
                }
            },

            add: function() {
                repo.add();
            },

            commit: function(options) {
                if ( '-a' === options[0] ) {
                    repo.add();
                }
                repo.commit();
            },

            checkout: function(options) {
                if ( '-b' === options[0] ) {
                    options.shift();
                    repo.branch(options);
                }
                repo.switchToBranch(options[0]);
            },

            reset: function(options) {
                var subTokens = options[0].split('~');

                if (subTokens.length > 1) {
                    repo.reset(~~subTokens[1]);
                } else {
                    repo.resetTo(subTokens[0]);
                }
            },

            rebase: function(options) {
                repo.rebase(options[0]);
            },

            gc: function() {
                repo.gc();
            },

            revert: function() {
                repo.revert();
            },

            'cherry-pick': function() {
                repo.cherryPick();
            },

            merge: function(options) {
                repo.merge(
                    _.without(options, '--no-ff'),
                    _.contains(options, '--no-ff')
                );
            }

        })
        .alias({
            b: 'branch',
            co: 'checkout',
            ci: 'add && commit'
        });

    function _run(commandStr) {
        var command;

        commandStr = commandStr.split(' ');
        command = commandStr[1];

        if (commandStr[0] !== 'git' || !command) return false;

        commander.run(command, commandStr.slice(2));

        return true;
    }

    return {
        run: function(commandStr) {
            commandStr.split(' && ').forEach(function(et) {
                _run(et);
            });
        }
    };
}
