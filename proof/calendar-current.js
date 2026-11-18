(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8b21966b5b9bd804.js","sha256":"8b21966b5b9bd8042d8b0442ac2eff18f457b879e502bee96252a5a1e545e9ec","count":2133,"publishedAt":"2026-11-18T20:38:47Z","state":"calendar-state.json","stateSha256":"ff4ffeb18080d6398ad35b25a416edc2901c395024acb2e2d546b2209490440e","sourceState":"calendar-source-state.json","sourceStateSha256":"1688598d537e93d48291f1e398d2174064ab5f1cf2fe037f6f3d3de4cb75e17b"});
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
