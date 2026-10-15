(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e71fc0a11796b493.js","sha256":"e71fc0a11796b493369d8a3afe6d2662afc7f73d11b1f3455d94586f3db56294","count":2147,"publishedAt":"2026-10-15T11:40:16Z","state":"calendar-state.json","stateSha256":"c580973ac4e55e014df7336ce36f19c658a675d1b4ec4263fe5245ab39a19d14","sourceState":"calendar-source-state.json","sourceStateSha256":"b2eb57f0b010964636051d7191324d11093ea3206d8b8ea5ab75ff901ac822ff"});
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
