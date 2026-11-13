(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9369f419a9929a6b.js","sha256":"9369f419a9929a6b70fb07d3b6828c36d5de423c1b4f03dcdd43d96a167d5285","count":2165,"publishedAt":"2026-11-13T20:12:57Z","state":"calendar-state.json","stateSha256":"4c2a661bbe31850f031cbfaf2c121bc421c4174fb533667db95fa78cc696c353","sourceState":"calendar-source-state.json","sourceStateSha256":"e0a3d3ec4c3e73cc816fc85958151d69c058b74796f170aec38bca25b68edbcc"});
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
