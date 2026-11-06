(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9ba70d0274852840.js","sha256":"9ba70d0274852840023c3518c2dafe871ba2e96e9be0a417f0aa1174ad417152","count":2026,"publishedAt":"2026-11-06T11:00:17Z","state":"calendar-state.json","stateSha256":"ac85dfe7bd28ff6acbd1107c38e84e38427c1650cbcd0129fd7385b398235b80","sourceState":"calendar-source-state.json","sourceStateSha256":"3eda4633abd206ac92e44b48e7315f9c22f359d5a567cfcd9e46d0fa7c918f6f"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
