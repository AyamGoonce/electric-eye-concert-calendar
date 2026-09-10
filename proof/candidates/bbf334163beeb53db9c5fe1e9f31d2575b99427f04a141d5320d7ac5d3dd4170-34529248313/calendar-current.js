(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bbf334163beeb53d.js","sha256":"bbf334163beeb53db9c5fe1e9f31d2575b99427f04a141d5320d7ac5d3dd4170","count":2488,"publishedAt":"2026-09-10T20:57:42Z","state":"calendar-state.json","stateSha256":"c29675d49db5231bfdeb826b42b8fb6e2991278a517ff6f6603d009d3fd189b2"});
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
