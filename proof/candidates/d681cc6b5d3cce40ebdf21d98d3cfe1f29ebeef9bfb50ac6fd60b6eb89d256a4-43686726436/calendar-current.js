(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d681cc6b5d3cce40.js","sha256":"d681cc6b5d3cce40ebdf21d98d3cfe1f29ebeef9bfb50ac6fd60b6eb89d256a4","count":2106,"publishedAt":"2026-11-15T06:43:36Z","state":"calendar-state.json","stateSha256":"e2b67ce8e5948a4c987de074f2d7d4b7793a69ecd581ca73081629070cb44159","sourceState":"calendar-source-state.json","sourceStateSha256":"ed586231847bef7acbb6cae59b4d7786e0f42320b3feb490148f2e4cd1095791"});
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
