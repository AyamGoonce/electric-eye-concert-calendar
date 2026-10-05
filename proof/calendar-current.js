(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.114b4d40fd364998.js","sha256":"114b4d40fd36499871e9ab5ae639031e6658e630e0e298720b2ffe28371f7d41","count":2194,"publishedAt":"2026-10-05T14:53:22Z","state":"calendar-state.json","stateSha256":"50930aaf71a926b2edca271efcf104dc9eba5da995e1bd62ac1860ad585826bd","sourceState":"calendar-source-state.json","sourceStateSha256":"c5258e6c5770f3b7e2036b2d284c4d5a8173db906819c70c3b0891cf1f273341"});
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
