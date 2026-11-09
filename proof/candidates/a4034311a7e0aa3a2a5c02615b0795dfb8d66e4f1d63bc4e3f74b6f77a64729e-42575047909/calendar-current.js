(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a4034311a7e0aa3a.js","sha256":"a4034311a7e0aa3a2a5c02615b0795dfb8d66e4f1d63bc4e3f74b6f77a64729e","count":1971,"publishedAt":"2026-11-09T06:47:39Z","state":"calendar-state.json","stateSha256":"c40c5c304b84258e67d57bafbb2c42c8a6de1d6639086dd1e697e7954e313810","sourceState":"calendar-source-state.json","sourceStateSha256":"ff78c96d3c92dfc1932ef1069683fe7bc0c4386def2979f455ce788c539d09a3"});
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
