(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.92d597de47b209fa.js","sha256":"92d597de47b209fa5b55c04cf084457ffa0e391a2684b5e2d820a39fad213d82","count":2051,"publishedAt":"2026-10-27T15:21:32Z","state":"calendar-state.json","stateSha256":"3dc048ad08b8194fb57e8edd252f5d9c4ee122bb847a90b962dff739d4ea2004","sourceState":"calendar-source-state.json","sourceStateSha256":"61308a4444bbb49660f5b41116ad417af9ce1dbee5d8e8a63d19586d0b0c369e"});
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
