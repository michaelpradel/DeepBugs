// run grunt --help for help on how to run
// Learn more about configuring this file at <https://github.com/theintern/intern/wiki/Configuring-Intern>.
// These default settings work OK for most people. The options that *must* be changed below are the
// packages, suites, excludeInstrumentation, and (if you want functional tests) functionalSuites.
define({
	// The port on which the instrumenting proxy will listen
	proxyPort: 9000,

	proxyUrl: "http://127.0.0.1:9000/",

	// Browsers to run integration testing against. Note that version numbers must be strings if used with Sauce
	// OnDemand. Options that will be permutated are browserName, version, platform, and platformVersion; any other
	// capabilities options specified for an environment will be copied as-is
	environments: [
		// It seems that specifying version="" or leaving version unspecified
		// does not default to the latest version of the browser.

		// Mobile
		{ platformName: "iOS", platformVersion: "8.1", browserName: "safari", deviceName: "iPhone Simulator",
			"device-orientation": "portrait", "appium-version": "1.3.4", name: "deliteful" },

		// Desktop.
		// Not running on IE9 since Widget-attr test depends on domClass methods only available in IE10_
		{ browserName: "internet explorer", version: "11", platform: "Windows 8.1", requireWindowFocus: "true",
			name : "deliteful"},
		{ browserName: "internet explorer", version: "10", platform: "Windows 8", requireWindowFocus: "true",
			name : "deliteful"},
		// { browserName: "internet explorer", version: "9", platform: "Windows 7" },
		{ browserName: "firefox", version: "31", platform: [ /*"OS X 10.6", "Linux", */ "Windows 7" ],
			// default selenium-version is currently 2.40.0; some Combobox functional tests fail with
			// 2.40.0, while they pass with 2.41.0.
			"selenium-version": "2.41.0",
			name : "deliteful"},
		{ browserName: "chrome", version: "32", platform: [ /*"OS X 10.6", "Linux", */ "Windows 7" ],
			name : "deliteful"},
		{ browserName: "safari", version: "7", platform: [ "OS X 10.9" ], name : "deliteful"}
	],

	// Maximum number of simultaneous integration tests that should be executed on the remote WebDriver service
	maxConcurrency: 3,

	// Whether or not to start Sauce Connect before running tests
	tunnel: "SauceLabsTunnel",
	
	// Maximum duration of a test, in milliseconds
	TEST_TIMEOUT: 300000, // 5 minutes
	
	// Maximum time to wait for someting (pollUntil, etc...)
	WAIT_TIMEOUT: 180000, // 3 minutes
	
	// Interval between two polling request, in milliseconds (for pollUntil)
	POLL_INTERVAL: 500, // 0.5 seconds

	loader: {
		baseUrl: typeof window !== "undefined" ? "../../.." : "..",
		config: {
			"ecma402/locales": "en-US"
		}
	},
	
	useLoader: {
		"host-node": "requirejs",
		"host-browser": "../../../requirejs/require.js"
	},
	
	// Non-functional test suite(s) to run in each browser
	suites: [ "deliteful/tests/unit/all" ],

	// Functional test suite(s) to run in each browser once non-functional tests are completed
	functionalSuites: [ "deliteful/tests/functional/all" ],

	// A regular expression matching URLs to files that should not be included in code coverage analysis
	excludeInstrumentation:
		/*jshint -W101*/
		/^(requirejs.*|dcl|dojo|dstore|dpointer|decor|jquery|lie|delite\/|deliteful\/tests|ecma402|.*themes|.*transitions|.*node_modules)/
});
