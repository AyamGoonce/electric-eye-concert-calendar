(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aa537643358a8fc0.js","sha256":"aa537643358a8fc0ae8cd2b4b49b767240d8a9b95b87a68d9dd0959f009dee1a","count":1728,"publishedAt":"2026-08-23T17:21:50Z","state":"calendar-state.json","stateSha256":"79c1f6a5c3604cd09f3b5baf1bcbfe68069e007d7c528f967dc2eeea905ed766"});
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
