(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.89efdeeeddfb1707.js","sha256":"89efdeeeddfb17072d7765844cac875be5bfab87e92a8bd112ffb98b0839286d","count":2406,"publishedAt":"2026-09-07T14:44:31Z","state":"calendar-state.json","stateSha256":"6f1a5bed3c941de0c056d1c7b736457215a39a429f724ef469f9fa68f4d6bd8f"});
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
