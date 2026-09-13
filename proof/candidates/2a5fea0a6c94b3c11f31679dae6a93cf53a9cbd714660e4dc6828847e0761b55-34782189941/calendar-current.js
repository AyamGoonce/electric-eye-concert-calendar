(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2a5fea0a6c94b3c1.js","sha256":"2a5fea0a6c94b3c11f31679dae6a93cf53a9cbd714660e4dc6828847e0761b55","count":2435,"publishedAt":"2026-09-13T20:58:50Z","state":"calendar-state.json","stateSha256":"158ebb7f4ff0e7e8e6d7ba6c8590265293e8d330bdf261648855b127ca21361a"});
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
