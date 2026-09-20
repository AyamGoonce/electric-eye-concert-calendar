(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.66ffcb82885bdd4c.js","sha256":"66ffcb82885bdd4ce8e2c717383d80fe463278244a9888f23c8eb62022353328","count":2177,"publishedAt":"2026-09-20T20:57:28Z","state":"calendar-state.json","stateSha256":"33cdbb339540f87c597dc3ca1177f9a139be9ca094898b3e2a6224cb8000041f"});
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
