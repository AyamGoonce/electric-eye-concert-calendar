(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2631cc3ac5eb6de2.js","sha256":"2631cc3ac5eb6de2632de87800c244247f9ce4fb33d8f5bacae36b43312d0bc5","count":2079,"publishedAt":"2026-10-20T21:16:16Z","state":"calendar-state.json","stateSha256":"43532e59f80b4d9590b9c7365fabebda3e53101dc888ec9a0fe84b25e1514d6f","sourceState":"calendar-source-state.json","sourceStateSha256":"2813ca1ca1a027fb90384d991df9afa7e53eade411bf4dd95445d447d730d1a1"});
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
