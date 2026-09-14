(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1d28da2298df339e.js","sha256":"1d28da2298df339ea3e6ae14020ed38a3ab12637447a322a22addd01eb1d83f3","count":2471,"publishedAt":"2026-09-14T23:57:52Z","state":"calendar-state.json","stateSha256":"c53900bee568c927fe68f6ede14f3f312c5f4a392c586b827a25ac6b8e73cd6f"});
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
