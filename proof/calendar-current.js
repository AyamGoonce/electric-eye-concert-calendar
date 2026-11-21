(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.35d28783a301fa7e.js","sha256":"35d28783a301fa7ebb3c9ed389f83092e3a491e1e56b903eeacda6b1872acafb","count":2123,"publishedAt":"2026-11-21T11:16:43Z","state":"calendar-state.json","stateSha256":"ff1c2d6a4d94798df9e3af50842c00cda389ebe5651041d75678b6493c381926","sourceState":"calendar-source-state.json","sourceStateSha256":"94bd701896578331c4e447b42578dcefb2e9affff90f2f1f23fbfd8a70bc00ff"});
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
