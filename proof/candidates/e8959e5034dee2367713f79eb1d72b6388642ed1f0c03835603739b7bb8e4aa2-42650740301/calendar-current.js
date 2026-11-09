(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e8959e5034dee236.js","sha256":"e8959e5034dee2367713f79eb1d72b6388642ed1f0c03835603739b7bb8e4aa2","count":2201,"publishedAt":"2026-11-09T16:04:27Z","state":"calendar-state.json","stateSha256":"7664c373f37e8a6a4d553a3481f535193201adc3daf66172fb4392b44f5158a2","sourceState":"calendar-source-state.json","sourceStateSha256":"b71d5d6a4d0fcd04cefc3063c9aa155e747df628ff0c9b72f7fe6ad45115d752"});
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
