(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4181fc70e3299da4.js","sha256":"4181fc70e3299da4fcac1abdc0e95b8687c48d23755af512643135684c8fd1de","count":2226,"publishedAt":"2026-10-01T23:12:56Z","state":"calendar-state.json","stateSha256":"11d6bdc71cb89e4afea684d36d921ded6419fd7fe2a40dd66fbf9e35435e01f7","sourceState":"calendar-source-state.json","sourceStateSha256":"a63f8e92df641bca0f92e1574c67c7addb9e4de2b1a8cb59634d470ad57784e0"});
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
