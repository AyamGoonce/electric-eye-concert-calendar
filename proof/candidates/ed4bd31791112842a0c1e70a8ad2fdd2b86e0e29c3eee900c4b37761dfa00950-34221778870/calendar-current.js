(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ed4bd31791112842.js","sha256":"ed4bd31791112842a0c1e70a8ad2fdd2b86e0e29c3eee900c4b37761dfa00950","count":2493,"publishedAt":"2026-09-08T11:44:25Z","state":"calendar-state.json","stateSha256":"6c6a66239ec4ae57994ef72435b5dc64d4fd95c960975f0ea450d57351ce4410"});
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
