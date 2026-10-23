(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.68f9e11e639f5216.js","sha256":"68f9e11e639f52162a7a2c431743129e26c313fd58711af9b8fb68b40c5b6431","count":2088,"publishedAt":"2026-10-23T11:48:53Z","state":"calendar-state.json","stateSha256":"dc1bf1c9a826452a55507065ba826c061c6b2a8d334d1a19f0e6c5386ee48bd4","sourceState":"calendar-source-state.json","sourceStateSha256":"50637b71e9525ab94cee5e2f875da1b7dc41ea56a0f555cbc2456f11ece9c54f"});
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
