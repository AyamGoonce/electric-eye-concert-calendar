(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c97f1277f12b209c.js","sha256":"c97f1277f12b209c3e60cad616a7a7677a05eaf9833fc5ceacd4910a7275fb74","count":2223,"publishedAt":"2026-10-01T10:04:42Z","state":"calendar-state.json","stateSha256":"dad531e24aa5fa595d92847c536f7de96ea2df9da8a2adea6260057f57e1abbb","sourceState":"calendar-source-state.json","sourceStateSha256":"17563fbc15856a6b104f8af0fbca93d473be6dafdff916bb7fb8b6b4bb213077"});
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
