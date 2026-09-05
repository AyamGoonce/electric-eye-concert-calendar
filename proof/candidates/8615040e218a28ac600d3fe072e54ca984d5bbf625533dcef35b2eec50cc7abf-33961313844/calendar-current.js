(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8615040e218a28ac.js","sha256":"8615040e218a28ac600d3fe072e54ca984d5bbf625533dcef35b2eec50cc7abf","count":2464,"publishedAt":"2026-09-05T10:49:41Z","state":"calendar-state.json","stateSha256":"f09046418af28389c636d57aa5488b4a5802005759c8eba74b1f408c539e735f"});
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
