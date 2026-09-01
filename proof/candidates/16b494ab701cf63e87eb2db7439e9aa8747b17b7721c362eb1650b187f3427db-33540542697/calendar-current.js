(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.16b494ab701cf63e.js","sha256":"16b494ab701cf63e87eb2db7439e9aa8747b17b7721c362eb1650b187f3427db","count":2240,"publishedAt":"2026-09-01T17:59:35Z","state":"calendar-state.json","stateSha256":"eed48a397e4879cd76262870633ed6d3aa4a814d7db90991f4e615137cfd8a0e"});
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
